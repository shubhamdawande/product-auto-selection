import pickle
import pulp as pl
from globals import *
import copy
from utilities import save_to_json

## Assets database as per asset json
with open('data/asset_list', 'rb') as fp:
    asset_data = pickle.load(fp)

## USER profile as per user json
budget = 1000
persona = 'Young Couple'
room_type = 'Master Bedroom'
room_area = 15 * 20 # 300 sq.ft.
brand_preference = ['Wayfair', 'West Elm', 'Crate And Barrel', 'Homefuly', 'Pepperfry', 'Pottery Barn']
theme_preference = ['Hollywood Regency', 'COASTAL CASUAL']

## Print user information
print 'USER PROFILE'
print 'budget: ', budget
print 'persona: ', persona
print 'room_type: ', room_type
print 'room_area: ', room_area
print 'brand_preference: ', brand_preference
print 'theme_preference: ', theme_preference

## Hyperparameters
## Weights: [theme, brand, mandatory room asset wght, room compat, user compat, category bias, asset repeat penalty]
wghts = [3.0, 1.5, 7.0, 2.0, 1.2, 10.0, -0.5]

print("Forming the MILP problem....")
prob = pl.LpProblem("The Budget Optimization Problem", pl.LpMaximize)

# For storing pulp LP variables
indicator = []

# amount of assets for each sub category
asset_subcat = {}

# value array
val_array = [0] * len(asset_data)

total_price = 0
total_area = 0
total_val1 = 0
total_assets_in_room = 0

subcategory_to_brands = {}
subcategory_to_themes = {}
subcategory_wise_qty = {}

for i in range(0, len(asset_data)):
    
    # each indicator variable denotes Qty of ith asset
    indicator.append(pl.LpVariable(str(i), 0, None, pl.LpInteger))

    # hold the budget and area constraint
    total_price += asset_data[i]._price * indicator[i]
    total_area  += asset_data[i]._dimension['depth'] * asset_data[i]._dimension['width'] * indicator[i]

    # mapping for subcategory to brands
    if asset_data[i]._subcategory in subcategory_to_brands and asset_data[i]._brand in brands:
        subcategory_to_brands[asset_data[i]._subcategory][brands.index(asset_data[i]._brand)] += indicator[i]
    elif asset_data[i]._brand in brands:
        subcategory_to_brands[asset_data[i]._subcategory] = [0] * len(brands)
        subcategory_to_brands[asset_data[i]._subcategory][brands.index(asset_data[i]._brand)] += indicator[i]
    else:
        continue

    # mapping for subcategory to themes
    if asset_data[i]._subcategory in subcategory_to_themes and asset_data[i]._theme in themes:
        subcategory_to_themes[asset_data[i]._subcategory][themes.index(asset_data[i]._theme)] += indicator[i]
    elif asset_data[i]._brand in brands:
        subcategory_to_themes[asset_data[i]._subcategory] = [0] * len(themes)
        subcategory_to_themes[asset_data[i]._subcategory][themes.index(asset_data[i]._theme)] += indicator[i]
    else:
        continue

    '''
    # qty of each subcategory
    if asset_data[i]._subcategory in subcategory_wise_qty:
        subcategory_wise_qty[asset_data[i]._subcategory] += indicator[i]
    else:
        subcategory_wise_qty[asset_data[i]._subcategory] = indicator[i]
    '''

    # theme preference measure
    if asset_data[i]._theme in theme_preference:
        term_theme = 1
    else:
        term_theme = 1/wghts[0]

    # brand preference measure
    if asset_data[i]._brand in brand_preference:
        term_brand = 1
    else:
        term_brand = 1/wghts[1]

    # room compatibility measure
    if asset_data[i]._subcategory in room_type_fit[room_type]: # if asset is mandatory, it has more importance & weight
        term_room = 1
    elif asset_data[i]._room_fit == room_type:                 # if asset is compatible to room
        term_room = 1/wghts[3]
    else:
        term_room = 1/wghts[2]
    
    # user compatibility measure
    if asset_data[i]._subcategory in user_persona_fit:
        term_user = 1
    else:
        term_user = 1/wghts[4]

    val_array[i] = term_theme + term_brand + term_room + term_user

    # objective value to maximize
    total_val1 += (term_theme + term_brand + term_room + term_user) * indicator[i]

    # desired qty
    if asset_data[i]._subcategory in asset_subcat:
        asset_subcat[asset_data[i]._subcategory] += indicator[i]
    else:
        asset_subcat[asset_data[i]._subcategory] = indicator[i]

    # bounds for total assets per room
    total_assets_in_room += indicator[i]


## CONSTRAINT : mutually exclusive
total_val2 = 0
for k, v in subcategory_to_brands.items():
    total_val2 -= 1.5 * ((asset_subcat[k] - desired_qty[k]) > 0)

##################### OBJECTIVE FUNCTION ############

prob.setObjective(total_val1 + total_val2)

######################## CONSTRAINTS ################

# price constraint
prob += total_price <= budget

# area constraint
prob += total_area >= room_area * 0.2
prob += total_area <= room_area * 0.6

# mutual exclusiveness for brands
for k, v in subcategory_to_brands.items():
    prob += sum(v[:]) <= min(max(v[:]), desired_qty[k])

# bounds on total items in a room
prob += total_assets_in_room <= 20

'''
### custom modifications from user through the app
# case 1. user removed item of type 'beds'
#prob += subcategory_wise_qty['Beds'] == 0
# case 2. removed item of theme 'Industrial'
#prob += subcategory_to_themes['Display Units']['Industrial'] == 0
# case 3. removed item of brand 'Pepperfry'
#prob += subcategory_to_brands['Display Units']['Pepperfry'] == 0
'''

prob.writeLP("data/design_optimization.lp")

####################### Generate unbiased HSN sets #####################

## HSN : Homefuly Serial Number, refers to a recommended set of k products
## Number of sets to generate
count = 2
val_array_ori = copy.deepcopy(val_array)
hsn_out_list = []

while count >= 0:

    prob.solve(pl.PULP_CBC_CMD())
    print ("Status: ", pl.LpStatus[prob.status])

    final_price = 0
    final_area = 0
    final_val = 0
    hsn_set = []

    for v in prob.variables():

        if v.varValue > 0:
            
            k = v.name
            index = int(k)
            final_price += asset_data[index]._price * v.varValue
            final_area += asset_data[index]._dimension['width'] * asset_data[index]._dimension['depth'] * v.varValue
            final_val += val_array[index] * v.varValue
            print '%22s' % asset_data[index]._subcategory + " / " + '%25s' % asset_data[index]._name + " / " + '%s' % asset_data[index]._price + " $$ / " + '%s' % asset_data[index]._theme + " / " + '%s' % asset_data[index]._brand + " / " + "Qty: " + '%d' % v.varValue + " / " + "value:", val_array[index]
            
            # dump HSN sets for writing to json
            hsn_set.append([asset_data[index]._id, index, v.varValue, val_array[index]])

            # decrease the value of asset for furthur hsn sets if already some set includes it
            total_val1 += indicator[index] * wghts[6]
            val_array[index] += wghts[6]

    hsn_out_list.append(hsn_set)
    print "Final value: ", final_val, "Final price: ", final_price, "Final_area: ", final_area
    print ""
    prob.setObjective(total_val1 + total_val2)
    count -= 1

############################ Generate category biased HSN sets ##########################
idx = 0
count = 2

while count >= 0:
    
    total_val1 = 0
    print "\n%s heavy set" % categories[idx]
    val_array_new = copy.deepcopy(val_array_ori)

    for i in range(0, len(asset_data)):

        # category priority
        if asset_data[i]._category == categories[idx]:
            term_category = 1
        else:
            term_category = 1/wghts[5]
        
        val_array_new[i] += term_category
        total_val1 += (val_array_new[i] * indicator[i])

    idx += 1
    prob.setObjective(total_val1 + total_val2)
    prob.solve(pl.PULP_CBC_CMD())
    print ("Status: ", pl.LpStatus[prob.status])

    final_price = 0
    final_area = 0
    final_val = 0
    hsn_set = []

    for v in prob.variables():

        if v.varValue > 0:
            
            k = v.name
            index = int(k)
            final_price += asset_data[index]._price * v.varValue
            final_area += asset_data[index]._dimension['width'] * asset_data[index]._dimension['depth'] * v.varValue
            final_val += val_array[index] * v.varValue
            print '%10s' % asset_data[index]._category + " / " + '%20s' % asset_data[index]._subcategory + " / " + '%25s' % asset_data[index]._name + " / " + '%s' % asset_data[index]._price + " $$ / " + '%s' % asset_data[index]._theme + " / " + '%s' % asset_data[index]._brand + " / " + "Qty: " + '%d' % v.varValue + " / " + "value:", val_array[index]

            # dump HSN sets for writing to json
            hsn_set.append([asset_data[index]._id, index, v.varValue, val_array[index]])

    hsn_out_list.append(hsn_set)
    print "Final value: ", final_val, "Final price: ", final_price, "Final_area: ", final_area
    print ""
    count -= 1

## Write output to JSON
#save_to_json(hsn_out_list, asset_data)
