import json
import copy
import random
import pickle
import requests
import pulp as pl
from globals import *

## routine to write data in json format
def save_to_json(hsn_list, asset_data, user_action):
    
    # demo design version
    ver = 0

    # read and save demo layout transforms
    if fetch_demo_design:
        read_design_json()
    
    # JSON: read pre defined design json format
    with open("input_data/MasterBedroom_demo_design_%d.json"%ver, "r") as read_file:
        data = json.load(read_file)

    ## JSON cleaning
    # design is posted with new id
    if '_id' in data:
        del data['_id']
    
    # redundant
    del data['createdAt']
    del data['updatedAt']
    del data['chats']
    
    data['room'] = room_id

    # set asset format
    fmt = copy.deepcopy(data['assets'][0])
    
    # _id is generated automatically from server for each asset
    if '_id' in fmt:
        del fmt['_id']
    fmt['inuse'] = True
    i = 0

    for set in hsn_list:

        # read layout hotspots pickle file
        with open('dumps/layout_positions_MasterBedroom_%d'%ver, 'rb') as fp:
            layout_ref = pickle.load(fp)

        data['assets'] = []
        data['name'] = 'room%d'%(i+1)

        for asset in set:

            for j in range(0, int(asset[3])):
                if asset[1] in layout_ref:
                    if len(layout_ref[asset[1]]) > 1:
                        fmt['transform'] = layout_ref[asset[1]][0]
                        layout_ref[asset[1]].pop(0)
                    elif len(layout_ref[asset[1]]) == 1:
                        fmt['transform'] = layout_ref[asset[1]][0]
                    
                    fmt['asset'] = asset[0] # asset id
                    data['assets'].append(copy.deepcopy(fmt))
                else:
                    fmt['transform'] = {"position": { "x": random.uniform(-0.3,0.3), "y": 0.2, "z": random.uniform(-0.3,0.3)},
                                        "rotation": { "x": 0, "y": 0, "z": 0},
                                        "scale":    { "x": 1, "y": 1, "z": 1}}
        
        if user_action == 'generate_initial_design':

            with open("output_designs/output_%d.json" % i, "w") as write_file:
                json.dump(data, write_file)
        
        elif user_action == 'modify_design':
            
            with open("output_designs/output_modified.json", "w") as write_file:
                json.dump(data, write_file)
        
        i += 1

## To get reference positions for optimal design layout
def read_design_json():
    
    # PICKLE: get asset categories
    with open('dumps/asset_categories', 'rb') as fp:
        asset_categories = pickle.load(fp)

    demo_design_ids = ['5c3d8aa8e9e71d280db86dab']

    # 3 demo design layouts
    for i in range(0,len(demo_design_ids)):
    
        # JSON: demo design for layout asset positions
        print 'Fetching demo design from server...'
        response = requests.get("https://homefuly.com:3443/api/organization/" + org_id +"/project/" + proj_id +"/room/" + room_id +"/version/" + demo_design_ids[i], headers=header)
        
        if response.json().get('status') == 'success':
            data = response.json().get('data')
            with open("input_data/MasterBedroom_demo_design_%d.json"%i, "wb") as write_file:
                json.dump(data, write_file)
        
        layout_positions = {}
        assets = data['assets']
        
        for asset in assets:
            if asset['inuse']:
                transform = asset['transform']
                subcategory = asset_categories[asset['asset']['subcategory']]
                if subcategory in layout_positions:
                    layout_positions[subcategory].append(transform)
                else:
                    layout_positions[subcategory] = []
                    layout_positions[subcategory].append(transform)

        # PICKLE
        with open('dumps/layout_positions_MasterBedroom_%s'%i, 'wb') as fp:
            pickle.dump(layout_positions, fp)


## ROUTINE to remove non optimal solution scenario
# in case of low budget and too many mandatory assets by removing low value assets

def make_model_feasible(prob, user):

    while pl.LpStatus[prob.status] == 'Infeasible':

        max_index = 0
        val = 0
        flag = False # to indicate optimal solution achieved/not
                
        if user._user_mandatory_assets == []:
            prob.solve(pl.PULP_CBC_CMD())
            print ("Status: ", pl.LpStatus[prob.status])
            if prob.status == 'Infeasible':
                raise Exception('Some unknown constraint is violated!!')
            return prob, user

        for tupl in user._user_mandatory_assets:
            if tupl[0] not in room_type_fit[room_type]:
                user._user_mandatory_assets.remove(tupl)
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
            return prob, user
        else:
            user._user_mandatory_assets.remove([room_type_fit[user._room_type][max_index], val])
            del prob.constraints['constraint_mandatory_%s'%room_type_fit[user._room_type][max_index]]
            prob.solve(pl.PULP_CBC_CMD())
            print ("Status: ", pl.LpStatus[prob.status])
            if pl.LpStatus[prob.status] == 'Optimal':
                return prob, user
    
    return prob, user