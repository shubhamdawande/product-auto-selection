import json
import copy
import random

## routine to write data in json format
def save_to_json(hsn_out_list, asset_data):
    
    # read pre defined design json format
    with open("test_output.json", "r") as read_file:
        data = json.load(read_file)

    if '_id' in data:
        del data['_id']
    
    data['room'] = "5c360388e5194c32118ba33c" # room id
    i = -1

    for set in hsn_out_list:

        # asset format
        fmt = copy.deepcopy(data['assets'][0])

        # _id is generated automatically from server for each asset
        if '_id' in fmt:
            del fmt['_id']
        
        # asset id from database
        data['assets'] = []
        i += 1

        for asset in set:

            # room scale: (1,1,1)
            fmt['transform']['position']['y'] = 0.2
            fmt['transform']['position']['x'] = random.uniform(-0.2,0.2)
            fmt['transform']['position']['z'] = random.uniform(-0.2,0.2)

            '''
            fmt['transform']['position']['y'] =  0+asset_data[asset[1]]._dimension['height']*0.3048/2
            fmt['transform']['position']['x'] =  random.uniform(
                                                 0.1+max(asset_data[asset[1]]._dimension['width'], asset_data[asset[1]]._dimension['depth'])*0.3048/2, 
                                                 0.9-max(asset_data[asset[1]]._dimension['width'], asset_data[asset[1]]._dimension['depth'])*0.3048/2) # considering max room size is 1 meters
            fmt['transform']['position']['z'] =  random.uniform(
                                                 0.1+max(asset_data[asset[1]]._dimension['width'], asset_data[asset[1]]._dimension['depth'])*0.3048/2, 
                                                 0.9-max(asset_data[asset[1]]._dimension['width'], asset_data[asset[1]]._dimension['depth'])*0.3048/2) # considering max room size is 1 meters
            '''

            fmt['asset'] = asset[0]  # asset id
            data['assets'].append(copy.deepcopy(fmt))
        
        with open("data/output_%d.json" % i, "w") as write_file:
            json.dump(data, write_file)