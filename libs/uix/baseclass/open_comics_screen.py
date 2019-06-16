from kivy.uix.screenmanager import Screen
from libs.utils.comic_server_conn import ComicServerConn
from kivy.uix.image import Image
from kivy.app import App
from kivy.core.window import Window
from libs.applibs.kivymd.imagelists import SmartTileWithLabel
from kivy.properties import ObjectProperty, StringProperty, NumericProperty


class CustomeST(SmartTileWithLabel):
    def __init__(self, **kwargs):
        super(CustomeST, self).__init__(**kwargs)
        self.menu_items = [{'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Read[/color]',
                            'callback': self.callback_for_menu_items},
                           {'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Mark as Read[/color]',
                            'callback': self.callback_for_menu_items},
                           {'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Mark as UnRead[/color]',
                            'callback': self.callback_for_menu_items},
                           {'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Close Comic[/color]',
                            'callback': self.callback_for_menu_items},
                           ]
        self.app = App.get_running_app()
        self.comic_slug = StringProperty()
        self.page_count = NumericProperty()
        self.leaf = NumericProperty()
        self.percent_read = NumericProperty()
        self.status = StringProperty()
        self.comic_obj = ObjectProperty()
        self.readinglist_obj = ObjectProperty()

    def callback_for_menu_items(self, *args):
        if args[0] == "[color=#000000]Read[/color]":
            new_screen_name = str(self.comic_obj.Id)
            self.app.manager.current = new_screen_name
        elif args[0] == "[color=#000000]Close Comic[/color]":
            screen_to_close = self.app.manager.get_screen(self.comic_obj.Id)
            self.app.manager.remove_widget(screen_to_close)
            self.app.manager.get_screen('open_comicscreen').build_page()


class OpenComicScreen(Screen):
    def __init__(self, **kwargs):
        super(OpenComicScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.fetch_data = None

    def on_enter(self):
        self.api_key = self.app.config.get('Server', 'api_key')
        self.api_url = self.app.api_url
        self.main_stack = self.ids['main_stack']
        self.m_grid = self.ids["main_grid"]
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]
        self.app.set_screen("Open Comics")
        self.build_page()

    def build_page(self):
        screen_names = self.app.manager.screen_names
        grid = self.m_grid
        grid.clear_widgets()
        if len(screen_names) == 0:
            pass
        else:
            for name in screen_names:
                if name in ['base', 'license', 'about', 'readinglistscreen',
                            'comicracklistscreen', 'open_comicscreen']:
                    pass
                else:
                    c_screen = self.app.manager.get_screen(name)
                    c = CustomeST()
                    c.comic_obj = c_screen.comic_obj
                    c.readinglist_obj = c_screen.readinglist_obj
                    c_image_source = f"{self.api_url}/Comics/{c.comic_obj.Id}/Pages/0?height=240&apiKey={self.api_key}"
                    c.source = c_image_source
                    c.PageCount = c.comic_obj.PageCount
                    strtxt = f"{c.comic_obj.Series} #{c.comic_obj.Number}"
                    c.text = strtxt
                    c.text_color = (0, 0, 0, 1)
                    grid.add_widget(c)
                    grid.cols = (Window.width-20)//160
