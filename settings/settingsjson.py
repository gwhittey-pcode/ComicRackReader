import json

settings_json_server = json.dumps([
    {'type':    'title',
     'title':   'ComicStream Server Settings'},

    {'type':    'string',
     'title':   'Server URL',
     'desc':    'URL for server. Leave ending / off. ex: http://192.168.1.215:8080/tablet',
     'section': 'Server',
     'key':     'url'},

    {'type':    'path',
     'title':   'Storage Directory',
     'desc':    'Where to store Comic Pages Buffer',
     'section': 'Server',
     'key':     'storagedir'},
    {
    'type':     'options',
    'title':    'Maximum Page Height',
    'desc':     'This will set the max height that image will be be grabbed from server default is 1500 due to memory constainst',
    'section':  'Server',
    'key':      'max_height',
    'options': ['1500','1280','1200','1024']
    },
    {'type':    'bool',
     'title':   'Use Api key',
     'desc':    'Use API key to access server',
     'section': 'Server',
     'key':     'use_api_key'},

      {'type':    'string',
     'title':   'API key',
     'desc':    'Api Key for server',
     'section': 'Server',
     'key':     'api_key'},
     
     {'type':    'string',
     'title':   'Username',
     'desc':    'Username for server',
     'section': 'Server',
     'key':     'username'},

     {'type':    'string',
     'title':   'Password',
     'desc':    'Password',
     'section': 'Server',
     'key':     'password'},

    {'type':     'numeric',
    'title':    'Max Pages to Load',
    'desc':     'Number if max pages to load before pagination',
    'section':  'Server',
    'key':      'max_pages_limit'},

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

    {'type':     'options',
    'title':    'Reading List Page Cover Icon Size',
    'desc':     'Size of Reading List Page Cover Icon',
    'section':  'Display',
    'key':      'reading_list_icon_size',
    'options': ['X-Large','Large','Medium','Small']},


    ])

tap_options = ['Next Page','Prev Page','Open Page Nav','Open Collection Browser',
                'Return to Comic List Screen','Go to List of Reading Lists', 'Disabled']
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






    #
    # {'type': 'bool',
    #  'title': 'A boolean setting',
    #  'desc': 'Boolean description text',
    #  'section': 'Server',
    #  'key': 'boolexample'},
    # {'type': 'numeric',
    #  'title': 'Page Buffer',
    #  'desc': 'How many pages to prefetch',
    #  'section': 'Server',
    #  'key': 'pagebuffer'},
    # {'type': 'options',
    #  'title': 'An options setting',
    #  'desc': 'Options description text',
    #  'section': 'Server',
    #  'key': 'optionsexample',
    #  'options': ['option1', 'option2', 'option3']},