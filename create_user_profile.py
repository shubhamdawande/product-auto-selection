class User:

    __slots__ = ('_budget', '_persona', '_room_type', '_room_area', '_brand_preference', '_theme_preference', '_user_defined_assets')

    def __init__(self, budget, persona, room_type, room_area, brand_preference, theme_preference, user_defined_assets):
        
        self._budget = budget
        self._persona = persona
        self._room_type = room_type
        self._room_area = room_area
        self._brand_preference = brand_preference
        self._theme_preference = theme_preference
        self._user_defined_assets = user_defined_assets


def create_user_profile():

    budget = 2000
    persona = 'Young Couple'
    room_type = 'Master Bedroom'
    room_area = 15 * 20 # in ft
    brand_preference = ['Wayfair', 'West Elm', 'Crate And Barrel', 'Pottery Barn']
    theme_preference = ['Hollywood Regency', 'COASTAL CASUAL']

    ## As per USER input: these asset subcategories are mandatory
    user_defined_assets = [['Beds', 1], ['Mirrors', 1], ['Cushions', 4]] 

    user = User(budget, persona, room_type, room_area, brand_preference, theme_preference, user_defined_assets)

    ## Print user information
    print 'USER PROFILE'
    print 'budget: ', user._budget
    print 'persona: ', user._persona
    print 'room_type: ', user._room_type
    print 'room_area: ', user._room_area
    print 'brand_preference: ', user._brand_preference
    print 'theme_preference: ', user._theme_preference
    print 'user_defined_assets: ', user._user_defined_assets
    print ''
    return user
