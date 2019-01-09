# Class for furniture Assets

class Asset:

    # Product features
    __slots__ = ('_name', '_category', '_subcategory', '_vertical', '_price',
                 '_dimension', '_theme', '_brand', '_room_fit')
    
    def __init__(self, asset_name, asset_category, asset_subcategory, asset_vertical, asset_price,
                asset_dimension, asset_theme, asset_brand, asset_room_fit):
        
        self._name = asset_name
        self._category = asset_category
        self._subcategory = asset_subcategory
        self._vertical = asset_vertical
        self._price = asset_price
        self._dimension = asset_dimension
        self._theme = asset_theme
        self._brand = asset_brand
        self._room_fit = asset_room_fit