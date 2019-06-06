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
from libs.utils.paginator import Paginator
from kivymd.toast import toast

#Cusom Tiles
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
        self.readinglist_Id = ObjectProperty()
        self.readinglist_name = ''
        #self.bind_to_resize()
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
        self.paginator = ObjectProperty()
        self.current_page = ObjectProperty()
        super(ReadingListScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.api_key = self.app.config.get('Server', 'api_key')
        self.api_url = self.app.api_url
        self.main_stack = self.ids['main_stack']
        self.m_grid = self.ids["main_grid"]
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]  
        self.app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.app.back_screen(27)]]
    
    def on_leave(self):
        self.app.list_previous_screens.append(self.name)

    def my_width_callback(self,obj, value):
        win_x = (Window.width-30)//160
        win_div = (Window.width-30) % 160
        for key, val in self.ids.items():
            if key == 'main_grid':
                c = val
                c.cols = (Window.width-20)//160

    
    def collect_readinglist_data(self, readinglist_name,readinglist_Id):
    
        self.readinglist_name = readinglist_name
        self.readinglist_Id = readinglist_Id
        self.fetch_data = ComicServerConn()
        lsit_count_url = f'{self.api_url}/Lists/{readinglist_Id}/Comics/'
        #self.fetch_data.get_list_count(lsit_count_url,self)
        self.fetch_data.get_server_data(lsit_count_url,self)
        
    

    def get_page(self, instance):
        page_num = instance.page_num
        page = self.paginator.page(page_num)
        self.current_page = page
        print(f"page.has_next:{page.has_next()}")
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
        

    def build_page(self,object_lsit):
        grid = self.m_grid
        main_stack = self.main_stack
        grid.clear_widgets()
        for comic in object_lsit:
            c = CustomeST()
            c.comic_obj = comic
            c.readinglist_obj = self.new_readinglist
            c_image_source = f"{self.api_url}/Comics/{comic.Id}/Pages/0?height=240&apiKey={self.api_key}"
            c.source = source=c_image_source 
            print(f"comic.PageCount:{comic.PageCount}")
            c.PageCount = comic.PageCount
            strtxt = f"{comic.Series} #{comic.Number}"
            c.text = strtxt
            grid.add_widget(c)
            grid.cols = (Window.width-20)//160
       
    def got_json(self,req, result):
        
        self.comic_collection = result
        self.new_readinglist = ComicReadingList(name=self.readinglist_name, data=result)
        for item in self.new_readinglist.data["items"]:
            new_comic = ComicBook(item)
            self.new_readinglist.add_comic(new_comic)

        if int(self.app.config.get('Server','use_pagination')) == 1:
            max_books_page = int(self.app.config.get('Server','max_books_page'))
            orphans = max_books_page - 1
            new_readinglist_reversed = self.new_readinglist.comics[::-1]
            self.paginator = Paginator(new_readinglist_reversed,max_books_page)
            print(f"um_page:{self.paginator.num_pages()}")
            page = self.paginator.page(1)
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
        

    
        #building back and prev page buttons for pagination of reading list
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

        