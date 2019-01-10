import json

## routine to write data in json format
def save_json(hsn_out_list):
    
    i = -1
    for set in hsn_out_list:
        
        i += 1
        with open("output_%d.json"%i, "r+") as read_file:
            data = json.load(read_file)

