import json
import copy
import random
import pickle

## routine to write data in json format
def save_to_json(hsn_list, asset_data, room_id):
    
    # demo design version
    ver = 1 

    # read and save demo layout transforms
    if True:
        read_design_json(ver)
    
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

        # read layout reference pickle file
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
                    fmt['transform'] = {
                                        "position": { "x": random.uniform(-0.3,0.3), "y": 0.2, "z": random.uniform(-0.3,0.3)},
                                        "rotation": { "x": 0, "y": 0, "z": 0},
                                        "scale":    { "x": 1, "y": 1, "z": 1}
                                        }

        with open("output_designs/output_%d.json" % i, "w") as write_file:
            json.dump(data, write_file)
        
        i += 1

## To get reference positions for optimal design layout
def read_design_json(ver):
    
    # PICKLE: get asset categories
    with open('dumps/asset_categories', 'rb') as fp:
        asset_categories = pickle.load(fp)

    # JSON: demo design for layout asset positions
    with open("input_data/MasterBedroom_demo_design_%d.json"%ver, "r") as read_file:
            data = json.load(read_file)
    
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
    with open('dumps/layout_positions_MasterBedroom_%s'%ver, 'wb') as fp:
        pickle.dump(layout_positions, fp)
