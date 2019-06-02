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

import webbrowser

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty,StringProperty,ListProperty
from libs.utils.comic_server_conn import ComicServerConn
from kivy.app import App
from libs.utils.convert_base64 import convert_to_image
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.logger import Logger

from settings.settingsjson import settings_json_screen_tap_control 
from libs.uix.widgets.comicbook_screen_widgets import *

import json


class ComicBookScreen(Screen):
    scroller = ObjectProperty()
    top_pop = ObjectProperty()
    section = StringProperty()
    sort_by = StringProperty()
    def __init__(self,**kwargs):
        super(ComicBookScreen, self).__init__(**kwargs)
        self.fetch_data = None
        self.app =  App.get_running_app()
        self.last_load = 0
        self.base_url = self.app.config.get('Server', 'url') + '/BCR'
        self.api_key = self.app.config.get('Server', 'api_key')
    def get_comic_from_server(self,comic_slug,page_count,leaf):
        img_a = ComicBookPageImage(id='10',comic_slug=comic_slug)
        self.ids['btn1'].add_widget(img_a)

    def on_enter(self):
        self.app.remove_action_bar()
        

    def on_leave(self):
        self.app.add_action_bar()
   
    def load_comic_book(self,comic_obj,readinglist_obj):
        
    
        config_app = App.get_running_app()
        settings_data = json.loads(settings_json_screen_tap_control)
        for setting in settings_data:
            if setting['type'] == 'options':

                tap_config = config_app.config.get(setting[u'section'], setting[u'key'])
                if tap_config == 'Disabled':
                      self.ids[setting[u'key']].disabled = True

       
        self.readinglist_obj = readinglist_obj
        self.comic_obj = comic_obj
        comic_book_carousel = self.ids.comic_book_carousel
        comic_book_carousel.clear_widgets()
        if self.scroller:self.scroller.clear_widgets()
        if self.top_pop:self.top_pop.clear_widgets()

    
        number_pages = int(comic_obj.PageCount)
        max_pages_limit = int(App.get_running_app().config.get('Server', 'max_pages_limit'))
        if number_pages<=max_pages_limit:
            x_title = 'Pages 1 to %s of %s '%(number_pages,number_pages)
        else:
            if self.last_load == 0:
                x_title = 'Pages 1 to %s of %s '%(max_pages_limit,number_pages)
            else:
                x_title = 'Pages %s to %s of %s '%(max_pages_limit,(self.last_load + max_pages_limit),number_pages)




        scroll = ScrollView( size_hint=(1,1), do_scroll_x=True, do_scroll_y=False,id='page_thumb_scroll')
        self.page_nav_popup = Popup(id='page_nav_popup',title=x_title, content=scroll, pos_hint ={'y': .0401},size_hint = (1,.35))

        self.scroller = scroll
        outer_grid = GridLayout(rows=1, size_hint=(None,None), spacing=5, padding=(5,0), id='outtergrd')
        outer_grid.bind(minimum_width=outer_grid.setter('width'))
        print ('max_pages_limit:%s'%str(max_pages_limit))
        print ('number_pages:%s'%number_pages)
        i = 0
        if number_pages<=max_pages_limit:
            
            self.use_pagination = False
            for i in range(0, number_pages):
               self.add_pages(comic_book_carousel,outer_grid,comic_obj,i)
        else:
            self.use_pagination = True
            if self.last_load == 0:
                for i in range(0,number_pages)[0:max_pages_limit]:
                    self.add_pages(comic_book_carousel,outer_grid,comic_obj,i)
                self.last_load = max_pages_limit
            else:
                for i in range(0,number_pages)[self.last_load:self.last_load + max_pages_limit]:
                    self.add_pages(comic_book_carousel,outer_grid,comic_obj,i)
                if (self.last_load - max_pages_limit) >=0:
                    self.last_section = (self.last_load - max_pages_limit)
                self.last_load = self.last_load + max_pages_limit

            if self.use_pagination:
                if i+1>=number_pages:
                    self.use_pagination = False
                    self.section = 'Last'
                elif i+1==max_pages_limit:
                    self.section = 'First'
                else:
                    self.section = 'Section'


        scroll.add_widget(outer_grid)
        if self.use_pagination == True:
            if len(self.readinglist_obj.comics)>1:
                self.build_top_nav()
        else:
            if len(self.readinglist_obj.comics)>1:
                self.build_top_nav()
                
    

    
    
    
    
    def add_pages(self,comic_book_carousel,outer_grid,comic_obj,i):
        strech_image = App.get_running_app().config.get('Display', 'stretch_image')
        
        max_height = App.get_running_app().config.get('Server', 'max_height')
        comic_page_scatter = ComicBookPageScatter(id='comic_scatter'+str(i))
        if strech_image == '1':
            s_allow_stretch=True
            s_keep_ratio=False
        else:
            s_allow_stretch=False
            s_keep_ratio=True
        
        comic_page_image = ComicBookPageImage(comic_slug=comic_obj.slug,
                                             id='pi_'+str(i),nocache=True,
                                             allow_stretch=s_allow_stretch,
                                             keep_ratio=s_keep_ratio,
                                             comic_page=i,
                                             source=f"{self.base_url}/Comics/{comic_obj.Id}/Pages/{i}?apiKey={self.api_key}"
                                             
                                            )
        comic_page_scatter.add_widget(comic_page_image)
        comic_book_carousel.add_widget(comic_page_scatter)
        #Let's make the thumbs for popup
        inner_grid = ThumbPopPageInnerGrid(id='inner_grid'+str(i))
        
        #page_thumb = ComicBookPageThumb(comic_obj.slug,id=comic_page_scatter.id,comic_page=i)
        page_thumb = ComicBookPageThumb(comic_slug=comic_obj.slug,id=comic_page_scatter.id,comic_page=i,
                                        source=f"{self.base_url}/Comics/{comic_obj.Id}/Pages/{i}?height=240&apiKey={self.api_key}")

        page_thumb.size_hint_y = None
        page_thumb.height = 240
        inner_grid.add_widget(page_thumb)
        page_thumb.bind(on_release=page_thumb.click)
        smbutton = ThumbPopPagebntlbl(text='P%s'%str(i+1),halign='center')
        inner_grid.add_widget(smbutton)
        outer_grid.add_widget(inner_grid)
       
    def page_nav_popup_open(self):
        self.page_nav_popup.open()
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        for child in self.walk():
            if child.id == current_slide.id:
                Logger.debug('child is %s == slide == %s'%(child.id,current_slide.id ))
                current_page =child

        for child in self.page_nav_popup.walk():
            Logger.debug('%s:%s'% (child,child.id))
            if child.id == 'page_thumb_scroll':
                scroller = child
                for grandchild in scroller.walk():
                    Logger.debug('--------%s:%s'% (grandchild,grandchild.id))
                    if grandchild.id == current_page.id:
                        target_thumb = grandchild
                        Logger.debug('target_thumb: %s'%target_thumb)
                        self.scroller.scroll_to(target_thumb,padding=10, animate=True)
    
    def build_top_nav(self):

        scroll = CommonComicsScroll(id='page_thumb_scroll')
        self.top_pop = Popup(id='page_pop',title='Pages', content=scroll, pos_hint ={'y': .724},size_hint = (1,.379))
        grid = CommonComicsOuterGrid(id='outtergrd')
        grid.bind(minimum_width=grid.setter('width'))
        rev_reading_list = reversed(self.readinglist_obj.comics)
        for comic in rev_reading_list:
            comic_name = str(comic.__str__)
            src_thumb = f"{self.base_url}/Comics/{comic.Id}/Pages/0?height=240&apiKey={self.api_key}"
            inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(comic.Id))
            comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(comic.Id))
            comic_thumb.readinglist_obj = self.readinglist_obj
            comic_thumb.comic = comic
            comic_thumb.readinglist_obj = self.readinglist_obj
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=comic_thumb.open_collection)
            smbutton = CommonComicsCoverLabel(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)
    
  

    def load_random_comic(self):
       self.top_pop.open()
    
    def comicscreen_open_collection_popup(self):
        self.top_pop.open()

class ComicBookPageControlButton(Button):
    pass