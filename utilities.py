import json
import copy

## routine to write data in json format
def save_to_json(hsn_out_list):
    
    # read pre defined design json format
    with open("test_output.json", "r") as read_file:
        data = json.load(read_file)

    del data['_id']
    data['room'] = "5c360388e5194c32118ba33c" # room id
    i = -1

    for set in hsn_out_list:

        # asset format
        fmt = copy.deepcopy(data['assets'][0])
        data['assets'] = []
        i += 1

        for asset in set:
            #print asset
            fmt['asset'] = asset[0]  # asset id
            data['assets'].append(copy.deepcopy(fmt))
        
        with open("data/output_%d.json" % i, "w") as write_file:
            json.dump(data, write_file)


