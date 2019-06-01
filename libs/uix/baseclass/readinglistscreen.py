# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright © 2017 Easy
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
# 
# LICENSE: MIT
from kivy.core.window import Window
    
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import ObjectProperty,StringProperty,NumericProperty
from kivy.uix.image import AsyncImage
from libs.applibs.kivymd.imagelists import SmartTileWithLabel
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.comic_json_to_class import ComicReadingList, ComicBook
from libs.applibs.kivymd.button import MDRaisedButton
from libs.applibs.kivymd.button import MDRoundFlatIconButton
import pprint
from kivymd.toast import toast

class CustomeST(SmartTileWithLabel):
    def __init__(self,**kwargs):
        self.menu_items =[{'viewclass': 'MDMenuItem',
                 'text': 'Read',
                 'callback': self.callback_for_menu_items},
                 {'viewclass': 'MDMenuItem',
                 'text': 'Mark as Read',
                 'callback': self.callback_for_menu_items},
                 {'viewclass': 'MDMenuItem',
                 'text': 'Mark as UnRead',
                 'callback': self.callback_for_menu_items}]
        self.app = App.get_running_app()
        self.comic_slug = StringProperty()
        self.page_count = NumericProperty()
        self.leaf = NumericProperty()
        self.percent_read = NumericProperty()
        self.status = StringProperty()
        self.comic_obj = ObjectProperty()
        self.readinglist_obj = ObjectProperty()
        super(CustomeST, self).__init__(**kwargs)

    def callback_for_menu_items(self, *args):
        if args[0] == "Read":
            self.app.manager.current = 'comic_book_screen'
            comicbook_screen = self.app.manager.get_screen('comic_book_screen')
            comicbook_screen.load_comic_book(self.comic_obj,self.readinglist_obj)
        toast(args[0])

class CustomMDRoundFlatIconButton(MDRoundFlatIconButton):
    def __init__(self,**kwargs):
        
        _url = ObjectProperty()
        super(CustomMDRoundFlatIconButton, self).__init__(**kwargs)
    

class ReadingListScreen(Screen):
    def __init__(self,**kwargs):
        self.app = App.get_running_app()
        self.fetch_data = None
        self.readinglist_slug = ObjectProperty()
        self.readinglist_name = ''
        #self.bind_to_resize()
        self.bind(width=self.my_width_callback)
        self.m_grid = ''
        self.main_stack = ''
        self.prev_button = ''
        self.next_button = ''
        self.new_readinglist = None
        
        comic_reading_list = ObjectProperty()

        super(ReadingListScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.main_stack = self.ids['main_stack']
        self.m_grid = self.ids["main_grid"]
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]  

    
    def my_width_callback(self,obj, value):
        win_x = (Window.width-30)//160
        win_div = (Window.width-30) % 160
        for key, val in self.ids.items():
            if key == 'main_grid':
                c = val
                c.cols = (Window.width-20)//160
              
    def collect_readinglist_data(self, readinglist_name,readinglist_slug):

        self.readinglist_name = readinglist_name
        self.fetch_data = ComicServerConn()
        base_url = App.get_running_app().config.get('Server', 'url')
        self.fetch_data = ComicServerConn()
        url_send = f'{base_url}readinglists/{readinglist_slug}/issue_list/?page=1'        
        self.fetch_data.get_server_data(url_send,self)

    def get_page(self, instance):
        self.fetch_data = ComicServerConn()
        self.fetch_data.get_server_data(instance._url,self)
   


    def got_json(self,req, result):
        self.comic_collection = result
        self.new_readinglist = ComicReadingList(name=self.readinglist_name, data=result)
        
        grid = self.m_grid
        main_stack = self.main_stack
        grid.clear_widgets()
        observers = self.prev_button.get_property_observers('on_release')
        #building back and prev page buttons for pagination of reading list
        if self.new_readinglist.data["previous"] is not None:
            self.prev_button.opacity = 1
            self.prev_button.disabled = False
            _url_prev = self.new_readinglist.data["previous"]
            self.prev_button._url = _url_prev
        else:
            self.prev_button.opacity = 0
            self.prev_button.disabled = True
            _url_prev = ''
        if self.new_readinglist.data["next"] is not None:
            self.next_button.opacity = 1
            self.next_button.disabled = False
            _url_next = self.new_readinglist.data["next"]
            self.next_button._url = _url_next
        else:
            self.next_button.opacity = 0
            self.next_button.disabled = True
            _url_prev = ''

        for item in self.new_readinglist.data["reading_list"]["comics"]:
            new_comic = ComicBook(item)
            self.new_readinglist.add_comic(new_comic)
            c = CustomeST()
            c.comic_obj = new_comic
            c.readinglist_obj = self.new_readinglist
            if item["image"] is None:
                c.source = source=('./assets/no_cover.jpg')                
            else:
                c.source = source=item["image"]  
            c.comic_slug = item["slug"]
            c.page_count = item["page_count"]
            c.leaf = item["leaf"]
            c.status = item["status"]
            c.percent_read = item["percent_read"]
            strtxt = str(item["__str__"]) + " Order # " + str(item["order_number"][0])
            c.text = strtxt
            grid.add_widget(c)
            grid.cols = (Window.width-20)//160
       