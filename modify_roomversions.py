import requests
from globals import *

version_ids = ['5c3d8aa8e9e71d280db86dab']

# input => design version JSON
def change_theme(version_json):
    
    # pre-processing
    # request layout
    response = requests.get("https://homefuly.com:3443/api/organization/" + org_id +"/project/" + proj_id +"/room/" + room_id +"/version/" + version_ids[i], headers=header)
    data = response.json().get('data')

    # get verticals and transforms
    assets = data['assets']
    vertical_list = {}
    for a in assets:
        vertical = a['asset']['vertical']
        if vertical in vertical_list:
            vertical_list[vertical].append(a['asset']['transform'])
        else:
            vertical_list[vertical] = []
            vertical_list.append(a['asset']['transform'])
    
    
