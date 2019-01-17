import pickle
import pulp as pl
import copy
import csv
import requests
import json
from pprint import pprint

from utilities import save_to_json
from create_user_profile import create_user_profile
from globals import *

######################### Read assets database dump ##############

with open('dumps/asset_database', 'rb') as fp:
    asset_data = pickle.load(fp)

######################### USER PROFILE ###########################

user = create_user_profile()
room_idx = room_types.index(user._room_type)

######################### Hyperparameters ########################

# Weights: [theme, brand, mandatory room asset wght, room compat, user compat, category bias, asset repeat penalty]
wghts = [3.0, 1.5, 7.0, 2.0, 1.2, 10.0, -0.5]

# Required area coverage bounds
req_area = [0.2, 0.6]

##################################################################

# fix desired qty for mandatory (user defined) assets
for a in user._user_defined_assets:
    desired_qty[a[0]][room_idx] = a[1]

# Formulate an MILP problem
print("Forming the MILP problem....")
prob = pl.LpProblem("The Budget Optimization Problem", pl.LpMaximize)

# For storing pulp LP variables
# each indicator variable denotes qty of ith asset
indicator = []

# amount of assets for each sub category
asset_subcat = {}

# value array per asset in database
val_array = [0] * len(asset_data)

# accumulator variables
total_price = 0
total_area = 0
total_val1 = 0
total_assets_in_room = 0

# feature maps: asset to user features
subcategory_to_brands = {}
subcategory_to_themes = {}
subcategory_wise_qty = {}

for i in range(0, len(asset_data)):
    
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

    # qty of each subcategory
    if asset_data[i]._subcategory in subcategory_wise_qty:
        subcategory_wise_qty[asset_data[i]._subcategory] += indicator[i]
    else:
        subcategory_wise_qty[asset_data[i]._subcategory] = indicator[i]

    # preference measure
    term_theme = 1 if asset_data[i]._theme in user._theme_preference else 1/wghts[0] # theme
    term_brand = 1 if asset_data[i]._brand in user._brand_preference else 1/wghts[1] # brand
    term_user = 1 if asset_data[i]._subcategory in user_persona_fit[user._persona] else 1/wghts[4] # user compatibility
    
    # room compatibility measure
    # if asset is neccessary, it has more weight
    if asset_data[i]._subcategory in room_type_fit[user._room_type] and asset_data[i]._room_fit == user._room_type:
        term_room = 1
    elif asset_data[i]._room_fit == user._room_type: # if asset is compatible to room
        term_room = 1/wghts[3]
    else:
        term_room = 1/wghts[2]
    
    # stores accumulated value for each asset
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


## CONSTRAINT : qty closer to desired quantity
total_val2 = 0
for k, v in subcategory_to_brands.items():
    total_val2 -= 1.5 * ((asset_subcat[k] - desired_qty[k][room_idx]) > 0)

##################### SET OBJECTIVE FUNCTION ###############

prob.setObjective(total_val1 + total_val2)

##################### CONSTRAINTS ##########################

# price constraint
prob += total_price <= user._budget

# area constraint
prob += total_area >= user._room_area * req_area[0]
prob += total_area <= user._room_area * req_area[1]

# mutual exclusiveness for brands
arr = [i[0] for i in user._user_defined_assets]
for k, v in subcategory_to_brands.items():
    if k not in arr:
        prob += sum(v[:]) <= min(max(v[:]), desired_qty[k][room_idx]+1)

# mandatory user defined items
for a in user._user_defined_assets:
    prob += subcategory_wise_qty[a[0]] == a[1], 'constraint_mandatory_%s'%a[0]

prob.writeLP("dumps/design_optimization.lp")

#######################################################################

## HSN : Homefuly Serial Number, refers to a set of k recommended products
## Number of sets to generate
count = 2
val_array_ori = copy.deepcopy(val_array)
hsn_out_list = []
display_output = []

# stores final csv output
display_output.extend([['Name', 'Vertical', 'Subcategory', 'Category', 'Theme', 'Brand', 'Price', 'QTY', 'Asset Value'], 
                      [''], ['Customer Req=>'], ['budget:', user._budget], ['persona:', user._persona], ['room_type:', user._room_type], 
                      ['room_area:', user._room_area], ['brand_preference:', user._brand_preference], 
                      ['theme_preference:', user._theme_preference], ['user_defined_assets:', user._user_defined_assets]])

####################### Generate unbiased HSN sets #####################

while count >= 0:

    prob.solve(pl.PULP_CBC_CMD())
    print ("Status: ", pl.LpStatus[prob.status])
    
    #################################################################
    ## Routine to remove non optimal solution scenario
    # in case of low budget and too many mandatory assets by removing low value assets
    
    while pl.LpStatus[prob.status] == 'Infeasible':

        max_index = 0
        val = 0
        flag = False # to indicate optimal solution achieved/not
        
        if user_defined_assets == []:
            prob.solve(pl.PULP_CBC_CMD())
            print ("Status: ", pl.LpStatus[prob.status])
            break

        for tupl in user._user_defined_assets:
            if tupl[0] not in room_type_fit[room_type]:
                user._user_defined_assets.remove(tupl)
                del prob.constraints['constraint_mandatory_%s'%tupl[0]]
                prob.solve(pl.PULP_CBC_CMD())
                print ("Status: ", pl.LpStatus[prob.status])
                if pl.LpStatus[prob.status] == 'Optimal':
                    flag = True
                    break
            else:
                idx = room_type_fit[room_type].index(tupl[0])
                if idx >= max_index:
                    max_index = idx
                    val = tupl[1]

        if flag:
            break
        else:
            user._user_defined_assets.remove([room_type_fit[user._room_type][max_index], val])
            del prob.constraints['constraint_mandatory_%s'%room_type_fit[user._room_type][max_index]]
            prob.solve(pl.PULP_CBC_CMD())
            print ("Status: ", pl.LpStatus[prob.status])
            if pl.LpStatus[prob.status] == 'Optimal':
                break
    
    print 'user defined assets (MODIFIED): ', user._user_defined_assets

    ###############################################################

    # accumulator variables
    final_price = 0
    final_area = 0
    final_val = 0
    hsn_set = []

    display_output.append([''])
    display_output.append(['SET %d'%(2-count)])

    for v in prob.variables():

        if v.varValue > 0:
            index = int(v.name)
            final_price += asset_data[index]._price * v.varValue
            final_area += asset_data[index]._dimension['width'] * asset_data[index]._dimension['depth'] * v.varValue
            final_val += val_array[index] * v.varValue
            #print '%22s' % asset_data[index]._subcategory + " / " + '%25s' % asset_data[index]._name + " / " + '%s' % asset_data[index]._price + " $$ / " + '%s' % asset_data[index]._theme + " / " + '%s' % asset_data[index]._brand + " / " + "Qty: " + '%d' % v.varValue + " / " + "value:", val_array[index]
            
            # dump HSN sets for writing to json
            asset_obj = asset_data[index]
            hsn_set.append([asset_obj._id, asset_obj._subcategory, index, v.varValue, val_array[index]])

            display_output.append([asset_obj._name, asset_obj._vertical, asset_obj._subcategory, asset_obj._category, asset_obj._theme, asset_obj._brand, asset_obj._price, v.varValue, val_array[index]])

            # decrease the value of asset for furthur hsn sets if already some set includes it
            total_val1 += indicator[index] * wghts[6]
            val_array[index] += wghts[6]

    hsn_out_list.append(hsn_set)

    display_output.append(['final_val: ', int(final_val), 'final_price: ', int(final_price), 'final_area: ', int(final_area)])
    
    #print "Final value: ", final_val, "Final price: ", final_price, "Final_area: ", final_area
    #print ""
    prob.setObjective(total_val1 + total_val2)
    count -= 1

############################ Generate category biased HSN sets ##########################
idx = 0
count = 2

while count >= 0:
    
    total_val1 = 0
    print "%s heavy set" % categories[idx]
    val_array_new = copy.deepcopy(val_array_ori)

    # for each asset in hsn, we prioritize their category 
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

    # accumulator variables
    final_price = 0
    final_area = 0
    final_val = 0
    hsn_set = []

    display_output.append([''])
    display_output.append(['SET %d'%(2-count+3)])

    for v in prob.variables():
        if v.varValue > 0:
            index = int(v.name)
            final_price += asset_data[index]._price * v.varValue
            final_area += asset_data[index]._dimension['width'] * asset_data[index]._dimension['depth'] * v.varValue
            final_val += val_array[index] * v.varValue
            #print '%10s' % asset_data[index]._category + " / " + '%20s' % asset_data[index]._subcategory + " / " + '%25s' % asset_data[index]._name + " / " + '%s' % asset_data[index]._price + " $$ / " + '%s' % asset_data[index]._theme + " / " + '%s' % asset_data[index]._brand + " / " + "Qty: " + '%d' % v.varValue + " / " + "value:", val_array[index]

            # dump HSN sets for writing to json
            hsn_set.append([asset_data[index]._id, asset_data[index]._subcategory, index, v.varValue, val_array[index]])
            display_output.append([asset_obj._name, asset_obj._vertical, asset_obj._subcategory, asset_obj._category, asset_obj._theme, asset_obj._brand, asset_obj._price, v.varValue, val_array[index]])
    
    hsn_out_list.append(hsn_set)
    display_output.append(['final_val: ', int(final_val), 'final_price: ', int(final_price), 'final_area: ', int(final_area)])
    #print "Final value: ", final_val, "Final price: ", final_price, "Final_area: ", final_area
    #print ""
    count -= 1

################# Export output to CSV format #############

print 'Writing hsn output to csv...'
with open('output_data/hsn_budget_%s.csv'%user._budget, 'wb') as myfile:
    wr = csv.writer(myfile)
    for i in range(0, len(display_output)):
        wr.writerow(display_output[i])

################# send data to server #####################

print 'Uploading designs to server...'
org_id = '5b068f62714382439d32fa04'
proj_id = '5c2de062fadece04e42425ed'
room_id = '5c360388e5194c32118ba33c'

## Write output to JSON
save_to_json(hsn_out_list, asset_data, room_id)
#response =  requests.post("https://homefuly.com:3443/api/auth/login", json={"email":"vikz91.deb@gmail.com","password":"19@Kaka91"})

## Post design json data to server
auth_token = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1YjJiNGRkYmY3NzE0OTUzNzkzNTdlNTMiLCJuYW1lIjoiYWJoaXNoZWsgZGViIiwiZW1haWwiOiJ2aWt6OTEuZGViQGdtYWlsLmNvbSIsInJvbGUiOiJtZW1iZXIiLCJpYXQiOjE1NDc2NDYxNDUsImV4cCI6MTU0ODAwNjE0NX0.CNBTbW8jooNYNB-T8deEliQ-pZhteKnM-8EeBg5sMHw"
head = {"Authorization" : auth_token}
versions_arr = ['5c3f2c52cd51932fec2b1665', '5c3f2c5bcd51932fec2b1666', '5c3f2d62cd51932fec2b1667', '5c3f2d6acd51932fec2b1668', '5c3f2d72cd51932fec2b1669', '5c3f2d7bcd51932fec2b166a']

'''
for i in range(0, 6):
    with open("output_designs/output_%d.json"%i, "r") as read_file:
        hsn = json.load(read_file)
    response = requests.post("https://homefuly.com:3443/api/organization/" + org_id +"/project/" + proj_id +"/room/" + room_id +"/version/" + versions_arr[i] + "/resetasset",
                            json={'roomasset':{'assets' : hsn['assets']}}, headers=head)
    print response.json().get('status')
'''