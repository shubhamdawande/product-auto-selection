### Global arrays

## Constant fields
brands = ['Wayfair', 'Joss And Main', 'CB2', 'West Elm', 'Crate And Barrel',
          'Homefuly', 'Restoration Hardware', 'Casaone', 'Pepperfry', 'DDECOR',
          'Flipkart', 'Pottery Barn', 'Arhaus', 'All Modern']

themes = ['Modern', 'Industrial', 'CONTEMPORARY', 'TRANSITIONAL', 'ART DECO', 'Indian', 'Indian Contemporary',
          'Bohemian', 'Scandinavian', 'ECCENTRIC / ECLECTIC', 'COASTAL CASUAL', 'Hollywood Regency',
          'SHABBY-CHIC', 'Mid Century', 'Traditional', 'MINIMALIST', 'RUSTIC']

categories = ['Furniture', 'Furnishing', 'Decor', 'Lighting', 'Wall Art', 'Appliances', 'Outdoor',
              'Others', 'Non Shoppable']

## Desired count of each item subcategory
## mapped for Master Bedroom
desired_qty = {
            'Sofas':0,
            'Chairs':1,
            'Tables':1,
            'Dining':0,
            'Shoe Racks':0,
            'TV Units':0,
            'Drawers':1,
            'Display Units':1,
            'Wardrobes':1,
            'Beds':1,
            'Prayer Units':0,
            'Dressers':1,
            'Bar Units':0,
            'Partitions':1,
            'Carpets & Rugs': 1,
            'Cushions': 2,
            'Curtains': 2,
            'Door Mats': 1,
            'Bedsheets': 1,
            'Wallpapers': 1,
            'throws': 1,
            'clocks': 1,
            'Plants': 1,
            'Vases': 1,
            'pots & planters': 1,
            'Mirrors': 1,
            'Curios and showpieces':1,
            'Baskets':1,
            'Lamps':1,
            'Lights':1,
            'Fans':1,
            'posters':1,
            'art panels':1,
            'paintings':4,
            'Picture Frames':4,
            'wall accents':1,
            'Wall Stickers/Decals':1,
            'Air Purifiers':1,
            'Room Heaters':1,
            'Geysers':1,
            'Outdoor Furniture':1,
            'False Ceiling':1,
            'Doors':1,
            'Windows':1
        }

## Necessary subcategories for Master Bedroom & Living Room
room_type_fit = {}
room_type_fit['Master Bedroom'] = ['Beds', 'Bedsheets', 'Mirrors', 'Dressers', 'Wardrobes', 'Lights', 'Curtains']
room_type_fit['Living Room'] = ['Sofas', 'TV Units', 'Lights', 'Shoe Racks', 'Door Mats', 'Display Units', 'Cushions', 'Curtains']

## Subcategories for 1 persona - Young Couple
user_persona_fit = ['Beds', 'Dressers', 'Tables', 'Display Units', 'Bedsheets', 'Chairs', 'Wardrobes']

## As per USER input json
user_mandatory_assets = [['Beds', 1], ['Dressers',1], ['Wardrobes',1], ['Display Units',1]]