import pickle
import pulp as pl
import copy
import csv
import requests
import json
from pprint import pprint

from utilities import save_to_json, make_model_feasible
from create_user_profile import create_user_profile
from globals import *

# MAIN function
# inputs: 
# user quiz data
# current room design json in case of modify design 
# user action data (theme, brand, price) to modify the design
# asset database dump

def milp_optimizer(user_json):

    # Read assets database from dump
    # asset dump to be updated everytime asset database is modified on server
    with open('dumps/asset_database', 'rb') as fp:
        asset_data = pickle.load(fp)
    
    # user profile
    user = create_user_profile(user_json)
    room_idx = room_types.index(user._room_type)
    user_event = user_json['user_event']

    # user modification
    if user_event == 'modify_design':
        
        if user_json['new_budget'] != None:
            user._budget = user_json['new_budget']

        if user_json['new_theme'] != None:
            user._theme  = user_json['new_theme']
        
        if user_json['new_brand'] != None:
            user._brand  = user_json['new_brand']

    # fix desired qty for mandatory assets (as defined by user)
    for a in user._user_mandatory_assets:
        desired_qty[a[0]][room_idx] = a[1]

    # Formulate an MILP problem
    print("Forming the MILP problem....")
    prob = pl.LpProblem("The Budget Optimization Problem", pl.LpMaximize)

    # For storing pulp LP variables
    # each indicator variable denotes qty of i'th asset
    indicator = []

    # value array per asset in database
    val_array = [0] * len(asset_data)

    # accumulator variables
    total_price = 0
    total_area = 0
    total_val1 = 0
    total_assets_in_room = 0

    # feature maps: asset to user features
    subcategory_to_brands = {}
    subcategory_qty = {}
    vertical_qty = {}

    # retrives subcategories compatible to user persona
    user_subcategories = []
    for k in user_persona_fit[user._persona]:
        user_subcategories.append(k)

    for i in range(0, len(asset_data)):
        
        indicator.append(pl.LpVariable(str(i), 0, None, pl.LpInteger))

        # hold the budget and area constraints
        total_price += asset_data[i]._price * indicator[i]
        total_area  += asset_data[i]._dimension['depth'] * asset_data[i]._dimension['width'] * indicator[i]

        # qty of each subcategory
        if asset_data[i]._subcategory in subcategory_qty:
            subcategory_qty[asset_data[i]._subcategory] += indicator[i]
        else:
            subcategory_qty[asset_data[i]._subcategory] = indicator[i]

        # qty of each vertical
        if asset_data[i]._vertical in vertical_qty:
            vertical_qty[asset_data[i]._vertical] += indicator[i]
        else:
            vertical_qty[asset_data[i]._vertical] = indicator[i]

        # mapping for subcategory to brands
        if asset_data[i]._subcategory in subcategory_to_brands:
            subcategory_to_brands[asset_data[i]._subcategory][brands.index(asset_data[i]._brand)] += indicator[i]
        else:
            subcategory_to_brands[asset_data[i]._subcategory] = [0] * len(brands)
            subcategory_to_brands[asset_data[i]._subcategory][brands.index(asset_data[i]._brand)] += indicator[i]

        # preference measures
        term_theme = 1 if asset_data[i]._theme in user._theme_preference else 1/wghts['theme'] # theme
        term_brand = 1 if asset_data[i]._brand in user._brand_preference else 1/wghts['brand'] # brand

        # user to asset compatibility
        # asset vertical or/and subcategory should be under user preference
        if asset_data[i]._subcategory in user_subcategories and asset_data[i]._vertical in user_persona_fit[user._persona][asset_data[i]._subcategory]:
            term_user = 1
        elif asset_data[i]._subcategory in user_subcategories:
            term_user = 1/wghts['user_compat_subcategory']
        else:
            term_user = 1/wghts['user_compat_vertical']
        
        # room to asset compatibility measure
        # if asset is neccessary for the room, it has more weight
        if asset_data[i]._subcategory in room_type_fit[user._room_type] and asset_data[i]._room_type == user._room_type:
            term_room = 1
        elif asset_data[i]._room_type == user._room_type: # if asset is compatible to room
            term_room = 1/wghts['room_compat']
        else:
            term_room = 1/wghts['user_defined_wght']
        
        # stores accumulated value for each asset
        val_array[i] = term_theme + term_brand + term_room + term_user

        # objective value to maximize
        total_val1 += (term_theme + term_brand + term_room + term_user) * indicator[i]

        # bounds for total assets per room
        total_assets_in_room += indicator[i]


    ## Objective 2: We want asset qty closer to desired quantity
    # To minimize -> absolute of (asset_subcategory_qty - desired_subcategory_qty)
    total_val2 = 0
    for k, v in subcategory_qty.items():
        t1 = pl.LpVariable('t1_%s'%k, 0, None, pl.LpInteger)
        t2 = pl.LpVariable('t2_%s'%k, 0, None, pl.LpInteger)
        prob += t1 >= 0
        prob += t2 >= 0
        prob += v == desired_qty[k][room_idx] + t1 - t2
        total_val2 += (wghts['desired_variance_penalty'] * (t1 + t2))

    ## Objective 3: adding asset in pairs increases the total value
    total_val3 = 0
    for pair in pairs:
        total_val3 += (subcategory_qty[pair[1]] >= subcategory_qty[pair[0]]) * 7

    ##################### SET OBJECTIVE FUNCTION ###############

    # total val1 => sum of values offered by each selected asset
    # total val2 => sum of variance in qty of asset subcategory from desired qty
    # total val3 => value offered by adding asset pairs

    prob.setObjective(total_val1 + total_val2 + total_val3)

    ##################### CONSTRAINTS ##########################

    # price constraint
    prob += total_price <= user._budget, 'constraint_budget'

    # area constraint
    prob += total_area >= user._room_area * req_area[0]
    prob += total_area <= user._room_area * req_area[1]

    # mutual exclusiveness feature
    # for brands
    mandatory_assets = [i[0] for i in user._user_mandatory_assets]
    extras = 5
    for k, v in subcategory_to_brands.items():
        if k not in mandatory_assets + user._user_retained_assets:
            if desired_qty[k] > 0:
                prob += sum(v[:]) <= min(max(v[:]), desired_qty[k][room_idx] + extras)
            else:
                prob += sum(v[:]) == 0

    # mandatory user defined items
    for a in user._user_mandatory_assets:
        prob += subcategory_qty[a[0]] == a[1], 'constraint_mandatory_%s'%a[0]

    # user excluded/retained items
    for a in user._user_retained_assets:
        prob += subcategory_qty[a] == 0

    # store pulp model
    prob.writeLP("dumps/design_optimization.lp")

    ## HSN : Homefuly Serial Number, refers to a set of k recommended products
    ## Number of sets to generate
    hsn_out_list = []

    # user actions: genrate_initial_designs, modify_theme, modify_brand, modify_price, modify_mandatory_set etc
    # Gives the initial design set
    print user_event
    if user_event == 'generate_initial_designs':
        
        # stores final csv output
        display_output = []
        display_output.extend([['Name', 'Vertical', 'Subcategory', 'Category', 'Theme', 'Brand', 'Price', 'QTY', 'Asset Value'],
                            [''], ['Customer Req=>'], ['budget:', user._budget], ['persona:', user._persona], ['room_type:', user._room_type], 
                            ['room_area:', user._room_area], ['brand_preference:', user._brand_preference], 
                            ['theme_preference:', user._theme_preference], ['user_mandatory_assets:', user._user_mandatory_assets],
                            ['user_retained_assets:', user._user_retained_assets]])

        ## Generate unbiased HSN sets
        count = 1
        idx = 0
        val_array_ori = copy.deepcopy(val_array)
        
        while count <= 6:
            print "Set: ", count

            if count >= 4:

                total_val1 = 0
                print "%s heavy set" % categories[idx]
                val_array = copy.deepcopy(val_array_ori)

                # for each asset in hsn, we prioritize their category
                for i in range(0, len(asset_data)):

                    # category priority
                    if asset_data[i]._category == categories[idx]:
                        term_category = 2.0
                    else:
                        term_category = 1.0/wghts['category']

                    val_array[i] += term_category
                    total_val1 += (val_array[i] * indicator[i])
                
                idx += 1
                prob.setObjective(total_val1 + total_val2 + total_val3)

            prob.solve(pl.PULP_CBC_CMD())
            print ("Status: ", pl.LpStatus[prob.status])
            
            [prob, user] = make_model_feasible(prob, user)
            print 'user mandatory assets (MODIFIED): ', user._user_mandatory_assets

            # accumulator variables
            final_price = 0
            final_area = 0
            final_val = 0
            number_of_assets = 0
            total_qty = 0
            hsn_set = []

            display_output.append([''])
            display_output.append(['SET %d'%(count)])

            for v in prob.variables():

                if v.varValue > 0 and len(v.name) <= 4:

                    index = int(v.name)
                    final_price += asset_data[index]._price * v.varValue
                    final_area += asset_data[index]._dimension['width'] * asset_data[index]._dimension['depth'] * v.varValue
                    final_val += val_array[index] * v.varValue
                    number_of_assets += 1
                    total_qty += v.varValue
                    print '%11s' % asset_data[index]._category + " | " + '%15s' % asset_data[index]._subcategory + " | " + '%20s' % asset_data[index]._vertical + ' | ' + '%30s' % asset_data[index]._name + " | " + '%s' % asset_data[index]._price + " $$ | " + '%s' % asset_data[index]._theme + " | " + '%s' % asset_data[index]._brand + " | " + "Qty: " + '%d' % v.varValue + " | " + "value: %0.2f"%val_array[index]
                    
                    # dump HSN sets for writing to json
                    asset_obj = asset_data[index]
                    hsn_set.append([asset_obj._id, asset_obj._subcategory, index, v.varValue, val_array[index]])
                    display_output.append([asset_obj._name, asset_obj._vertical, asset_obj._subcategory, asset_obj._category, asset_obj._theme, asset_obj._brand, asset_obj._price, v.varValue, val_array[index]])

                    # decrease the value of asset for furthur hsn sets if already some set includes it
                    total_val1 += indicator[index] * wghts['repeat_penalty']
                    val_array[index] += wghts['repeat_penalty']

            hsn_out_list.append(hsn_set)

            display_output.append(['final_val:', int(final_val), 'final_price: ', int(final_price), 'final_area: ', int(final_area),
                                'n_assets:', number_of_assets, 'total_qty:', total_qty])
            
            print "Final value: ", final_val, "Final price: ", final_price, "Final_area: ", final_area, "n_assets: ", number_of_assets, "total_qty: ", total_qty
            print ""
            if count < 4:
                prob.setObjective(total_val1 + total_val2 + total_val3)
            count += 1

        ## Export output to CSV format
        print 'Writing hsn output to csv...'
        with open('output_data/hsn_budget_%s.csv'%user._budget, 'wb') as myfile:
            wr = csv.writer(myfile)
            for i in range(0, len(display_output)):
                wr.writerow(display_output[i])

    # handles the scenario when user wants to change aspects of existing design
    elif user_event == 'modify_design':
        
        cur_layout_info = user_json['layout']
        assets = cur_layout_info['assets']
        vertical_list = {}

        for a in assets:
            vertical = a['asset']['vertical']
            if vertical in vertical_list:
                vertical_list[vertical].append(a['asset']['transform'])
            else:
                vertical_list[vertical] = []
                vertical_list.append(a['asset']['transform'])
        
        # all vertical types should remain constant
        for k in vertical_list:
            prob += vertical_qty[k] == len(vertical_list[k])

        prob.solve(pl.PULP_CBC_CMD())
        print ("Status: ", pl.LpStatus[prob.status])

        [prob, user] = make_model_feasible(prob, user)
        print 'user defined assets (MODIFIED): ', user._user_mandatory_assets

        final_price = 0
        final_area = 0
        final_val = 0
        number_of_assets = 0
        total_qty = 0
        hsn_set = []
        
        for v in prob.variables():

            if v.varValue > 0 and len(v.name) <= 4:
                
                index = int(v.name)
                final_price += asset_data[index]._price * v.varValue
                final_area += asset_data[index]._dimension['width'] * asset_data[index]._dimension['depth'] * v.varValue
                final_val += val_array[index] * v.varValue
                number_of_assets += 1
                total_qty += v.varValue
                print '%15s' % asset_data[index]._subcategory + " / " + '%18s' % asset_data[index]._vertical + ' / ' + '%26s' % asset_data[index]._name + " / " + '%s' % asset_data[index]._price + " $$ / " + '%s' % asset_data[index]._theme + " / " + '%s' % asset_data[index]._brand + " / " + "Qty: " + '%d' % v.varValue + " / " + "value:", val_array[index]
                
                # dump HSN sets for writing to json
                asset_obj = asset_data[index]
                hsn_set.append([asset_obj._id, asset_obj._subcategory, index, v.varValue, val_array[index]])

        hsn_out_list.append(hsn_set)
    
    ## Write output to JSON
    #save_to_json(hsn_out_list, asset_data, user_event)

    '''
    ################# send data to server #####################

    #response =  requests.post("https://homefuly.com:3443/api/auth/login", json=login_account_info)

    ## Post design json data to server
    print 'Uploading designs to server...'
    for i in range(0, 6):
        with open("output_designs/output_%d.json"%i, "r") as read_file:
            hsn = json.load(read_file)
        response = requests.post("https://homefuly.com:3443/api/organization/" + org_id +"/project/" + proj_id +"/room/" + room_id +"/version/" + versions_arr[i] + "/resetasset",
                                json={'roomasset':{'assets' : hsn['assets']}}, headers=header)
        print response.json().get('status')
    '''

if __name__=="__main__":
    user_json = {'budget':20000, 'persona':'Young Couple', 'room_type':'Master Bedroom', 'room_area':15*15, 
                 'brand_preference': ['Wayfair', 'West Elm', 'Crate And Barrel', 'Pottery Barn'],
                 'theme_preference': ['Hollywood Regency', 'COASTAL CASUAL'],
                 'user_mandatory_assets':[], 'user_retained_assets':[],
                 'user_event':'generate_initial_designs'
                }
    milp_optimizer(user_json)