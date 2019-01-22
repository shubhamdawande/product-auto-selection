class User:

    __slots__ = ('_budget', '_persona', '_room_type', '_room_area', '_brand_preference', '_theme_preference', '_user_defined_assets',
                 '_user_retained_assets')

    def __init__(self, budget, persona, room_type, room_area, brand_preference, theme_preference, user_defined_assets, user_retained_assets):
        
        self._budget = budget
        self._persona = persona
        self._room_type = room_type
        self._room_area = room_area
        self._brand_preference = brand_preference
        self._theme_preference = theme_preference
        self._user_defined_assets = user_defined_assets
        self._user_retained_assets = user_retained_assets

## Customize user profile based upon quiz inputs
def create_user_profile():

    budget = 20000
    persona = 'Young Couple'
    room_type = 'Master Bedroom'
    room_area = 15 * 15 # in ft
    brand_preference = ['Wayfair', 'West Elm', 'Crate And Barrel', 'Pottery Barn']
    theme_preference = ['Hollywood Regency', 'COASTAL CASUAL']

    ## As per USER input: these asset subcategories are mandatory
    user_defined_assets = [['Beds', 1], ['Curtains', 1], ['Cushions', 4]]

    ## User retained assets to be excluded
    user_retained_assets = []

    user = User(budget, persona, room_type, room_area, brand_preference, theme_preference, user_defined_assets, user_retained_assets)

    ## Print user information
    print 'USER PROFILE'
    print 'budget: ', user._budget
    print 'persona: ', user._persona
    print 'room_type: ', user._room_type
    print 'room_area: ', user._room_area
    print 'brand_preference: ', user._brand_preference
    print 'theme_preference: ', user._theme_preference
    print 'user_defined_assets: ', user._user_defined_assets
    print 'user_retained_assets: ', user._user_retained_assets
    print ''

    return user
