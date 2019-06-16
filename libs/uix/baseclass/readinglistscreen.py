# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright © 2017 Easy
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
# LICENSE: MIT
from kivy.core.window import Window

from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.image import AsyncImage
from libs.applibs.kivymd.imagelists import SmartTileWithLabel
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.comic_json_to_class import ComicReadingList, ComicBook
from libs.applibs.kivymd.button import MDRaisedButton
from libs.applibs.kivymd.button import MDFillRoundFlatIconButton
from libs.utils.paginator import Paginator
from libs.uix.baseclass.comicbookscreen import ComicBookScreen
from kivymd.toast import toast


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
                            'callback': self.callback_for_menu_items}]
        self.app = App.get_running_app()
        self.comic_slug = StringProperty()
        self.page_count = NumericProperty()
        self.leaf = NumericProperty()
        self.percent_read = NumericProperty()
        self.status = StringProperty()
        self.comic_obj = ObjectProperty()
        self.readinglist_obj = ObjectProperty()
        self.paginator_obj = ObjectProperty()
        self.pag_pagenum = NumericProperty()

    def callback_for_menu_items(self, *args):
        if args[0] == "[color=#000000]Read[/color]":
            new_screen_name = str(self.comic_obj.Id)
            if new_screen_name not in self.app.manager.screen_names:
                new_screen = ComicBookScreen(
                    readinglist_obj=self.readinglist_obj,
                    comic_obj=self.comic_obj,
                    paginator_obj=self.paginator_obj,
                    pag_pagenum=self.pag_pagenum,
                    name=new_screen_name)
                self.app.manager.add_widget(new_screen)
                self.app.manager.current = new_screen_name


class CustomMDFillRoundFlatIconButton(MDFillRoundFlatIconButton):
    def __init__(self, **kwargs):
        _url = ObjectProperty()
        super(CustomMDFillRoundFlatIconButton, self).__init__(**kwargs)


class ReadingListScreen(Screen):
    def __init__(self, **kwargs):
        super(ReadingListScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.fetch_data = None
        self.readinglist_Id = ObjectProperty()
        self.readinglist_name = ''
        # self.bind_to_resize()
        self.bind(width=self.my_width_callback)
        self.m_grid = ''
        self.main_stack = ''
        self.prev_button = ''
        self.next_button = ''
        self.new_readinglist = None
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        comic_reading_list = ObjectProperty()
        self.api_key = self.app.config.get('Server', 'api_key')
        self.list_count = ''
        self.paginator_obj = ObjectProperty()
        self.current_page = ObjectProperty()
        self.list_loaded = BooleanProperty()
        self.list_loaded = False

    def on_pre_enter(self, *args):
        self.api_key = self.app.config.get('Server', 'api_key')
        self.api_url = self.app.api_url
        self.main_stack = self.ids['main_stack']
        self.m_grid = self.ids["main_grid"]
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]

    def on_leave(self):
        self.app.list_previous_screens.append(self.name)

    def my_width_callback(self, obj, value):
        win_x = (Window.width-30)//160
        win_div = (Window.width-30) % 160
        for key, val in self.ids.items():
            if key == 'main_grid':
                c = val
                c.cols = (Window.width-20)//160

    def collect_readinglist_data(self, readinglist_name, readinglist_Id):
        self.readinglist_name = readinglist_name
        self.app.set_screen(self.readinglist_name + ' Page 1')
        self.readinglist_Id = readinglist_Id
        self.fetch_data = ComicServerConn()
        lsit_count_url = f'{self.api_url}/Lists/{readinglist_Id}/Comics/'
        # self.fetch_data.get_list_count(lsit_count_url,self)
        self.fetch_data.get_server_data(lsit_count_url, self)

    def get_page(self, instance):
        page_num = instance.page_num
        self.app.set_screen(self.readinglist_name + f' Page {page_num}')
        page = self.paginator_obj.page(page_num)
        self.current_page = page
        if page.has_next():
            self.next_button.opacity = 1
            self.next_button.disabled = False
            self.next_button.page_num = page.next_page_number()
        else:
            self.next_button.opacity = 0
            self.next_button.disabled = True
            self.next_button.page_num = ''
        if page.has_previous():
            self.prev_button.opacity = 1
            self.prev_button.disabled = False
            self.prev_button.page_num = page.previous_page_number()
        else:
            self.prev_button.opacity = 0
            self.prev_button.disabled = True
            self.prev_button.page_num = ''
        self.build_page(page.object_list)

    def build_page(self, object_lsit):
        grid = self.m_grid
        main_stack = self.main_stack
        grid.clear_widgets()
        for comic in object_lsit:
            c = CustomeST()
            c.comic_obj = comic
            c.readinglist_obj = self.new_readinglist
            c.paginator_obj = self.paginator_obj
            c_image_source = f"{self.api_url}/Comics/{comic.Id}/Pages/0?height=240&apiKey={self.api_key}"
            c.source = source = c_image_source
            c.PageCount = comic.PageCount
            c.pag_pagenum = self.current_page.number
            strtxt = f"{comic.Series} #{comic.Number}"
            c.text = strtxt
            c.text_color = (0, 0, 0, 1)
            grid.add_widget(c)
            grid.cols = (Window.width-20)//160

    def got_json(self, req, result):

        self.comic_collection = result
        self.new_readinglist = ComicReadingList(
            name=self.readinglist_name, data=result)
        for item in self.new_readinglist.data["items"]:
            new_comic = ComicBook(item)
            self.new_readinglist.add_comic(new_comic)

        if int(self.app.config.get('Server', 'use_pagination')) == 1:
            max_books_page = int(self.app.config.get(
                'Server', 'max_books_page'))
            orphans = max_books_page - 1
            new_readinglist_reversed = self.new_readinglist.comics[::-1]
            self.paginator_obj = Paginator(
                new_readinglist_reversed, max_books_page)
            page = self.paginator_obj.page(1)
            self.current_page = page
            if page.has_next():
                self.next_button.opacity = 1
                self.next_button.disabled = False
                self.next_button.page_num = page.next_page_number()
            else:
                self.next_button.opacity = 0
                self.next_button.disabled = True
                self.next_button.page_num = ''
            if page.has_previous():
                self.prev_button.opacity = 1
                self.prev_button.disabled = False
                self.prev_button.page_num = page.previous_page_number()
            else:
                self.prev_button.opacity = 0
                self.prev_button.disabled = True
                self.prev_button.page_num = ''
            self.build_page(page.object_list)
        else:
            self.build_page(self.new_readinglist.comics)
        self.list_loaded = True
        # building back and prev page buttons for pagination of reading list
        # if self.new_readinglist.data["previous"] is not None:
        #     self.prev_button.opacity = 1
        #     self.prev_button.disabled = False
        #     _url_prev = self.new_readinglist.data["previous"]
        #     self.prev_button._url = _url_prev
        # else:
        #     self.prev_button.opacity = 0
        #     self.prev_button.disabled = True
        #     _url_prev = ''
        # if self.new_readinglist.data["next"] is not None:
        #     self.next_button.opacity = 1
        #     self.next_button.disabled = False
        #     _url_next = self.new_readinglist.data["next"]
        #     self.next_button._url = _url_next
        # else:
        #     self.next_button.opacity = 0
        #     self.next_button.disabled = True
        #     _url_prev = ''
