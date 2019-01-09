import json
import pprint
from asset import Asset
import pickle

## load asset categories
with open("categorys.json", "r") as read_file:
   asset_categorys_json = json.loads(read_file.read())

asset_type = {} # type id : type name
for category in asset_categorys_json['data']['asset_categorys']:
    asset_type[category['_id']] = category['name']
    
    for subcategory in category['subcategories']:
        asset_type[subcategory['_id']] = subcategory['name']

        for vertical in subcategory['verticals']:
            asset_type[vertical['_id']] = vertical['name']


## load asset database
with open("assets.json", "r") as read_file:
    assets_json = json.loads(read_file.read())

asset_data = {} # asset info list
asset_count = assets_json['data']['count']
i = 0

for asset in assets_json['data']['assets']:

    # categories 
    asset_category = asset_type[asset['category']]

    # price
    if 'customer' in asset['price']:
        asset_price = asset['price']['customer']
    else:
        asset_price = 0

    if asset['currency'] == 'INR' and asset_price != None:
        asset_price /= 65
    
    # dimension
    if 'dimension' in asset:
        d = asset['dimension']
        asset_dimension = { 'depth' : d['depth'], 'width' : d['width'], 'height' : d['height']}
        
    # subcategories
    if asset['subcategory'] != '':
        asset_subcategory = asset_type[asset['subcategory']]
    else:
        asset_subcategory = ''
        
    # verticals
    if asset['vertical'] != '':
        asset_vertical = asset_type[asset['vertical']]
    else:
        asset_vertical = ''

    # style/theme
    asset_theme = asset['theme']
    if asset_theme != None:
        asset_theme = asset['theme']['name']

    # brand
    asset_brand = asset['designedBy']
    #print asset_brand
    if asset_brand != '':
        if 'organizationInternalLink' in asset_brand:
            asset_brand = asset['designedBy']['organizationInternalLink']['name']
        else:
            asset_brand = ''

    # room fit
    asset_room_fit = asset['roomType']
    if asset_room_fit != None:
        asset_room_fit = asset['roomType']['name']

    # name
    asset_name = asset['name']

    # Create asset
    if asset_subcategory != '' and asset_category != 'Non Shoppable':

        if asset_price != None and asset_theme != None and asset_room_fit != None and asset_brand != '':
        
            if asset_dimension['width'] <= 10 and asset_dimension['depth'] <= 10:
            
                asset_data[i] = Asset(asset_name, asset_category, asset_subcategory, asset_vertical, asset_price,
                                  asset_dimension, asset_theme, asset_brand, asset_room_fit)
                #print [asset_name, asset_category, asset_subcategory, asset_vertical, asset_price,
                #       asset_dimension, asset_theme, asset_brand, asset_room_fit]
                i += 1
print i

## dump asset data to pickle file
with open('data/asset_list', 'wb') as fp:
    pickle.dump(asset_data, fp)