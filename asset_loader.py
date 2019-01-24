import json
import pprint
from asset import Asset
import pickle
from globals import *
import requests
import re

def asset_loader():
    
    ## Retrieve asset and categories from server
    if fetch_assets_from_server:
        response = requests.get("https://homefuly.com:3443/api/assets?limit=2078", headers=header)
        assets_json = response.json().get('data')
        with open("input_data/assets.json", "wb") as write_file:
            json.dump(assets_json, write_file)

        response = requests.get("https://homefuly.com:3443/api/asset_categorys", headers=header)
        asset_categorys_json = response.json().get('data')
        with open("input_data/categorys.json", "wb") as write_file:
            json.dumps(asset_categorys_json, write_file)
    else:
        with open("input_data/categorys.json", "r") as read_file:
            asset_categorys_json = json.loads(read_file.read())

        with open("input_data/assets.json", "r") as read_file:
            assets_json = json.loads(read_file.read())

    ## Convert json data to python interpretable format
    # format = { type id : type name }
    asset_type = {}

    for category in asset_categorys_json['asset_categorys']:
        asset_type[category['_id']] = category['name']
        
        for subcategory in category['subcategories']:
            asset_type[subcategory['_id']] = subcategory['name']

            for vertical in subcategory['verticals']:
                asset_type[vertical['_id']] = vertical['name']

    # PICKLE
    with open('dumps/asset_categories', 'wb') as fp:
        pickle.dump(asset_type, fp)

    # asset info list
    asset_data = {} 
    asset_count = assets_json['count']
    i = 0

    for asset in assets_json['assets']:

        # categories 
        if asset['category'] != '':
            asset_category = asset_type[asset['category']]
        else:
            continue

        # price
        if 'customer' in asset['price']:
            asset_price = asset['price']['customer']
        else:
            continue

        # convert INR to Dollars
        if asset['currency'] == 'INR' and asset_price != None:
            asset_price *= 0.014
        
        # dimension
        if 'dimension' in asset:
            d = asset['dimension']
            asset_dimension = { 'depth' : d['depth'], 'width' : d['width'], 'height' : d['height']}
        
        # subcategories
        if asset['subcategory'] != '':
            if asset['subcategory'] in asset_type:
                asset_subcategory = asset_type[asset['subcategory']]
            else:
                continue
        else:
            continue
            
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
                if asset_brand['organizationInternalLink'] != None:
                    asset_brand = asset['designedBy']['organizationInternalLink']['name']
                else:
                    continue
            else:
                continue

        # room fit
        asset_room_type = asset['roomType']
        if asset_room_type != None:
            asset_room_type = asset['roomType']['name']

        # name
        asset_name = asset['name']

        # id
        asset_id = asset['_id']

        # Create asset
        if asset_category != 'Non Shoppable':

            if asset_price != None and asset_theme != None and asset_room_type != None:
            
                if asset_dimension['width'] <= 10 and asset_dimension['depth'] <= 10 and asset_dimension['height'] < 8:
                    
                    if asset_price > 0 and asset_brand in brands and asset_theme in themes:

                        asset_name = re.sub('[^a-zA-Z0-9 \n\.]', '', asset_name)
                        asset_data[i] = Asset(asset_id, asset_name, asset_category, asset_subcategory, asset_vertical, asset_price,
                                    asset_dimension, asset_theme, asset_brand, asset_room_type)
                        #print [asset_category, asset_subcategory, asset_vertical, asset_name, asset_price,
                        #       asset_dimension, asset_theme, asset_brand, asset_room_type]
                        i += 1
    print i

    ## dump asset data to pickle file
    with open('dumps/asset_database', 'wb') as fp:
        pickle.dump(asset_data, fp)

if __name__=="__main__":
    asset_loader()