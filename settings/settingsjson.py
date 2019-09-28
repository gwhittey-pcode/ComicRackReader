import json
from kivy.core.window import Keyboard
hot_keys_options = []
for item in Keyboard.keycodes:
    hot_keys_options.append(item[0])

settings_json_sync = json.dumps([
    {'type':    'title',
     'title':   'Sync Settings'},

    {'type': 'path',
     'title': 'Sync Directory',
     'desc': 'Path to store downloaded sync comics',
     'section': 'Sync',
     'key': 'sync_folder'},

    {'type': 'numeric',
     'title': 'Default Max Comic to Sync',
     'desc': 'This is how many Comics to sync Default',
     'section': 'Sync',
     'key': 'max_num_sync'}

])
settings_json_server = json.dumps([

    {'type':    'string',
     'title':   'Server URL',
     'desc':    'URL for server. Leave ending / off. ex: http://192.168.1.215:8080/tablet',  # noqa
     'section': 'General',
     'key':     'base_url'},

    {'type':    'path',
     'title':   'Cache Directory',
     'desc':    'Where to store Comic Pages Cache',
     'section': 'General',
     'key':     'storagedir'},
    {
        'type':     'options',
        'title':    'Maximum Page Height',
        'desc':     'Maximum Page Height to Download',
        'section':  'General',
        'key':      'max_height',
        'options': ['2000', '1500', '1280', '1200', '1024']
    },

    {
        'type':     'options',
        'title':    'How to Open Synced Comic',
        'desc':     'Select Method to open click on comic in reading list screen if Synced',
        'section':  'General',
        'key':      'how_to_open_comic',
        'options': ['Open Local Copy', 'Open From API Server']
    },
    # {'type':    'bool',
    #  'title':   'Use Api key',
    #  'desc':    'Use API key to access server',
    #  'section': 'General',
    #  'key':     'use_api_key'},

    {'type':    'string',
     'title':   'API key',
     'desc':    'Api Key for server',
     'section': 'General',
     'key':     'api_key'},

    {'type':    'string',
     'title':   'Username',
     'desc':    'Username for server',
     'section': 'General',
     'key':     'username'},

    {'type':    'string',
     'title':   'Password',
     'desc':    'Password',
     'section': 'General',
     'key':     'password'},

    # {'type':    'bool',
    #  'title':   'Use Pagination',
    #  'desc':    'Use Pagination to limit number of books on each List/Series
    # page',
    #  'section': 'General',
    #  'key':     'use_pagination'},

    {'type':     'numeric',
     'title':    'Max ComicBooks',
     'desc':     'Number of books to show on list page(turn pagination on)',
     'section':  'General',
     'key':      'max_books_page'},

    {'type':     'bool',
     'title':    'Open Last Comic at Start',
     'desc':     'Open last comic at application startup',
     'section':  'General',
     'key':      'open_last_comic_startup'},

])


settings_json_dispaly = json.dumps(
    [
        {'type':   'title',
         'title':   'Settings for how comic reader behaves'},

        {'type':    'bool',
         'title':   'Right to Left',
         'desc':    'Default to Right to Left Readin',
         'section': 'Display',
         'key':     'right2left'},

        {'type':    'bool',
         'title':   'Split Double Page',
         'desc':    'Split double pages into 2 slides',
         'section': 'Display',
         'key':     'dblpagesplit'},

        {'type':    'bool',
         'title':   'Stretch to Page',
         'desc':    'If on will stretch to fill page',
         'section': 'Display',
         'key':     'stretch_image'},

        {'type':     'numeric',
         'title':    'Magnifying Glass Size',
         'desc':     'Size of Magnifying Glass Square on each side',
         'section':  'Display',
         'key':      'mag_glass_size'},

        # {'type':     'options',
        #  'title':    'Comic Icon Width',
        #  'desc':     'Comic Thumb Width',
        #  'section':  'Display',
        #  'key':      'comic_thumb_width'},

        # {'type':     'options',
        #  'title':    'Comic Icon Width',
        #  'desc':     'Comic Thumb Width',
        #  'section':  'Display',
        #  'key':      'comic_thumb_height'},
        {'type':     'options',
         'title':    'Reading List Page Cover Icon Size',
         'desc':     'Size of Reading List Page Cover Icon',
         'section':  'Display',
         'key':      'reading_list_icon_size',
         'options': ['X-Large', 'Large', 'Medium', 'Small']},

        {'type':     'numeric',
         'title':    'Max Pages to Load',
         'desc':     'Number if max pages to load before pagination',
         'section':  'Display',
         'key':      'max_comic_pages_limit'},

        {'type':    'numeric',
         'title':   'Window Height',
         'desc':    'Windows Height *If changed App Retart Required',
         'section': 'Display',
         'key':     'window_height'},

        {'type':    'numeric',
         'title':   'Window Width',
         'desc':    'Windows Width *If changed App Retart Required',
         'section': 'Display',
         'key':     'window_width'},

    ])

tap_options = ['Next Page', 'Prev Page', 'Open Page Nav',
               'Open Collection Browser', 'Return to Comic List Screen',
               'Go to Reading Lists Screen', 'Open NavBar', 'None']
settings_json_screen_tap_control = json.dumps(
    [
        {'type':   'title',
         'title':   'Settings for how Screen taps control Comic Reader.'},

        {
            'type':     'options',
            'title':    'Bottom Left Screen',
            'desc':     'This will set the Bottom Left Screen Control',
            'section':  'Screen Tap Control',
            'key':      'bottom_left',
            'options':   tap_options
        },

        {
            'type':     'options',
            'title':    'Bottom Center Screen',
            'desc':     'This will set the Bottom Center Screen Control',
            'section':  'Screen Tap Control',
            'key':      'bottom_center',
            'options':  tap_options
        },
        {
            'type':     'options',
            'title':    'Bottom Right Screen',
            'desc':     'This will set the Bottom Right Screen Control',
            'section':  'Screen Tap Control',
            'key':      'bottom_right',
            'options':  tap_options
        },

        {
            'type':     'options',
            'title':    'Top Left Screen',
            'desc':     'This will set the Top Left Screen Control',
            'section':  'Screen Tap Control',
            'key':      'top_left',
            'options':  tap_options
        },

        {
            'type':     'options',
            'title':    'Top Center Screen',
            'desc':     'This will set the Top Center Screen Control',
            'section':  'Screen Tap Control',
            'key':      'top_center',
            'options':  tap_options
        },
        {
            'type':     'options',
            'title':    'Top Right Screen',
            'desc':     'This will set the Top Right Screen Control',
            'section':  'Screen Tap Control',
            'key':      'top_right',
            'options':  tap_options
        },
        {
            'type':     'options',
            'title':    'Middle Left Screen',
            'desc':     'This will set the Middle Left Screen Control',
            'section':  'Screen Tap Control',
            'key':      'middle_left',
            'options':  tap_options
        },

        {
            'type':     'options',
            'title':    'Middle Center Screen',
            'desc':     'This will set the Middle Center Screen Control',
            'section':  'Screen Tap Control',
            'key':      'middle_center',
            'options':  tap_options
        },
        {
            'type':     'options',
            'title':    'Middle Right Screen',
            'desc':     'This will set the Middle Right Screen Control',
            'section':  'Screen Tap Control',
            'key':      'middle_right',
            'options':  tap_options
        },
        {'type':     'numeric',
         'title':    'Double Tap Time',
         'desc':     'Time in milliseconds during a double tap is allowed',
         'section':  'Screen Tap Control',
         'key':      'dbl_tap_time'},

    ])
#hot_keys_options = ['right', 'left', 'space']
settings_json_hotkeys = json.dumps(
    [
        {'type':   'title',
         'title':   'Keyboard Hotkeys'},

        {
            'type':     'hotkeys',
            'title':    'Next Page',
            'desc':     'This will set the Hotkeys for Next Page',
            'section':  'Hotkeys',
            'key':      'hk_next_page',

        },
        {
            'type':     'hotkeys',
            'title':    'Prev Page',
            'desc':     'This will set the Hotkeys for Prev Page',
            'section':  'Hotkeys',
            'key':      'hk_prev_page',

        },
        {
            'type':     'hotkeys',
            'title':    'Open Page Nav',
            'desc':     'This will set the Hotkeys for Open Page Nav',
            'section':  'Hotkeys',
            'key':      'hk_open_page_nav',

        },
        {
            'type':     'hotkeys',
            'title':    'Open Collection Browser',
            'desc':     'This will set the Hotkeys for Open Collection Browser',
            'section':  'Hotkeys',
            'key':      'hk_open_collection',

        },
        {
            'type':     'hotkeys',
            'title':    'Return to Comic List Screen',
            'desc':     'This will set the Hotkeys for Return to Comic List Screen',
            'section':  'Hotkeys',
            'key':      'hk_return_comic_list',

        },
        {
            'type':     'hotkeys',
            'title':    'Go to Reading Lists Screen',
            'desc':     'This will set the Hotkeys for Return to Comic List Screen',
            'section':  'Hotkeys',
            'key':      'hk_return_base_screen',

        },
        {
            'type':     'hotkeys',
            'title':    'Open NavBar',
            'desc':     'This will set the Hotkeys to Open NavBar(on comicbook reader)',
            'section':  'Hotkeys',
            'key':      'hk_toggle_navbar',

        },

        {
            'type':     'hotkeys',
            'title':    'Toggle Full Screen',
            'desc':     'This will set the Hotkeys to Toggle Full Screen',
            'section':  'Hotkeys',
            'key':      'hk_toggle_fullscreen',

        },



    ])
