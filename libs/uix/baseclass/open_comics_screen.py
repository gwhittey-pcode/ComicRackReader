from kivy.uix.screenmanager import Screen
from libs.utils.comic_server_conn import ComicServerConn
from kivy.uix.image import Image
from libs.applibs.kivymd.button import MDRaisedButton
from kivy.app import App
from kivy.core.window import Window
from libs.applibs.kivymd.imagelists import SmartTileWithLabel
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from functools import partial


class MySmartTileWithLabel(SmartTileWithLabel):
    my_clock = ObjectProperty()
    do_action = StringProperty()

    def __init__(self, **kwargs):
        super(MySmartTileWithLabel, self).__init__(**kwargs)
        self.menu_items = [{'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Read[/color]',
                            'callback': self.callback_for_menu_items},
                           #    {'viewclass': 'MDMenuItem',
                           #     'text': '[color=#000000]Mark as Read[/color]',
                           #     'callback': self.callback_for_menu_items},
                           #    {'viewclass': 'MDMenuItem',
                           #    'text':'[color=#000000]Mark as UnRead[/color]',
                           #     'callback': self.callback_for_menu_items},
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

    def on_press(self):
        callback = partial(self.menu)
        self.do_action = 'menu'
        Clock.schedule_once(callback, .001)
        self.my_clock = callback

    def menu(self, *args):
        self.do_action = 'menu'

    def on_release(self):
        Clock.unschedule(self.my_clock)
        self.do_action = 'menu'
        return super(MySmartTileWithLabel, self).on_press()

    def open_comic(self):
        new_screen_name = str(self.comic_obj.Id)
        self.app.manager.current = new_screen_name


class OpenComicScreen(Screen):
    def __init__(self, **kwargs):
        super(OpenComicScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.fetch_data = None

    def on_pre_enter(self):
        self.app.show_action_bar()

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
        # close_all_button = MDRaisedButton(text='Close All')
        # grid.add_widget(close_all_button)
        grid.cols = (Window.width-20)//160
        if len(screen_names) == 0:
            pass
        else:
            for name in screen_names:
                if name in self.app.LIST_SCREENS:
                    pass
                else:
                    c_screen = self.app.manager.get_screen(name)
                    c = MySmartTileWithLabel()
                    c.comic_obj = c_screen.comic_obj
                    c.readinglist_obj = c_screen.readinglist_obj
                    c_img_s1 = f'/Comics/{c.comic_obj.Id}/Pages/0?height=240'
                    c_api_url = f'&apiKey={self.api_key}'
                    c_image_source = f'{self.api_url}{c_img_s1}{c_api_url}'
                    c.source = c_image_source
                    c.PageCount = c.comic_obj.PageCount
                    strtxt = f"{c.comic_obj.Series} #{c.comic_obj.Number}"
                    strtxt = f'{strtxt} {c_screen.str_page_count}'
                    c.text = strtxt
                    c.text_color = (0, 0, 0, 1)
                    grid.add_widget(c)
