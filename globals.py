## User project related info
org_id = '5b068f62714382439d32fa04'
proj_id = '5c2de062fadece04e42425ed'
room_id = '5c360388e5194c32118ba33c'

# Server info
auth_token = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI1YjJiNGRkYmY3NzE0OTUzNzkzNTdlNTMiLCJuYW1lIjoiYWJoaXNoZWsgZGViIiwiZW1haWwiOiJ2aWt6OTEuZGViQGdtYWlsLmNvbSIsInJvbGUiOiJtZW1iZXIiLCJpYXQiOjE1NDc3MzMyMzAsImV4cCI6MTU0ODA5MzIzMH0.5mgk09LTxqjeXYIPAHYH-Aq4e8dkpVfvss1rwQF9RZA"
header = {"Authorization" : auth_token}
versions_arr = ['5c3f2c52cd51932fec2b1665', '5c3f2c5bcd51932fec2b1666', '5c3f2d62cd51932fec2b1667', '5c3f2d6acd51932fec2b1668', '5c3f2d72cd51932fec2b1669', '5c3f2d7bcd51932fec2b166a']
login_account_info = {"email":"vikz91.deb@gmail.com","password":"19@Kaka91"}
fetch_assets_from_server = False

## Constant lists
brands = ['Wayfair', 'Joss And Main', 'CB2', 'West Elm', 'Crate And Barrel',
          'Homefuly', 'Restoration Hardware', 'Casaone', 'Pepperfry', 'DDECOR',
          'Flipkart', 'Pottery Barn', 'Arhaus', 'All Modern']

themes = ['Modern', 'Industrial', 'CONTEMPORARY', 'TRANSITIONAL', 'ART DECO', 'Indian', 'Indian Contemporary',
          'Bohemian', 'Scandinavian', 'ECCENTRIC / ECLECTIC', 'COASTAL CASUAL', 'Hollywood Regency',
          'SHABBY-CHIC', 'Mid Century', 'Traditional', 'MINIMALIST', 'RUSTIC']

categories = ['Furniture', 'Furnishing', 'Decor', 'Lighting', 'Wall Art', 'Appliances', 'Outdoor',
              'Others', 'Non Shoppable']

room_types = ['Master Bedroom', 'Living Room', 'Kids Bedroom', 'Home Office']

## Desired Count of each item subcategory wise
desired_qty = {
            'Sofas':[0],
            'Chairs':[2],
            'Tables':[2],
            'Dining':[0],
            'Shoe Racks':[0],
            'TV Units':[0],
            'Drawers':[1],
            'Display Units':[2],
            'Wardrobes':[1],
            'Beds':[1],
            'Prayer Units':[0],
            'Dressers':[1],
            'Bar Units':[0],
            'Partitions':[1],
            'Carpets & Rugs':[1],
            'Cushions': [4],
            'Curtains': [2],
            'Door Mats': [1],
            'Bedsheets': [1],
            'Wallpapers': [1],
            'throws': [1],
            'clocks': [1],
            'Plants': [1],
            'Vases': [1],
            'pots & planters': [1],
            'Mirrors': [1],
            'Curios and showpieces':[1],
            'Baskets':[1],
            'Lamps':[2],
            'Lights':[2],
            'Fans':[1],
            'posters':[1],
            'art panels':[1],
            'paintings':[4],
            'Picture Frames':[4],
            'wall accents':[1],
            'Wall Stickers/Decals':[1],
            'Air Purifiers':[1],
            'Room Heaters':[1],
            'Geysers':[1],
            'Outdoor Furniture':[1],
            'False Ceiling':[1],
            'Doors':[1],
            'Windows':[1]
        }

## Room Type: Necessary (need not be mandatory) subcategories
room_type_fit = {}
room_type_fit['Master Bedroom'] = ['Beds', 'Bedsheets', 'Mirrors', 'Dressers', 'Wardrobes', 'Curtains', 'Tables', 'Lights']
room_type_fit['Living Room'] = ['Sofas', 'TV Units', 'Lights', 'Shoe Racks', 'Door Mats', 'Display Units', 'Cushions', 'Curtains']

## User Persona: Necessary subcategories & verticals:
# Personas: young couple, old couple, kids, female bachelors, male bachelors
user_persona_fit = {}
user_persona_fit['Young Couple'] = {'Beds':['King Sized Beds', 'Queen Sized Beds'],
                                    'Dressers':['Dressing Tables', 'Dressing Chairs'],
                                    'Tables':['Coffee Tables', 'Bedside Tables'],
                                    'Display Units':[], 'Chairs':[], 'Wardrobes':[], 'Curtains':[]}

## Subcategory wise pairs
#pairs = [['Tables', 'Chairs'], ['Tables', 'Lamps'], ['Drawers', 'Mirrors']]
pairs = []