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
from functools import partial
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty,StringProperty,ListProperty
from libs.utils.comic_server_conn import ComicServerConn
from kivy.app import App
from libs.utils.convert_base64 import convert_to_image
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatter  import Scatter
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.logger import Logger
from kivy.metrics import dp
from settings.settingsjson import settings_json_screen_tap_control 
from libs.uix.widgets.comicbook_screen_widgets import *
from libs.applibs.kivymd.dialog import MDDialog
from kivy.loader import Loader
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
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.api_key = self.app.config.get('Server', 'api_key')
        self.paginator = ObjectProperty()
        self.current_page = None      
        self.comic_obj = ObjectProperty()
        self.comic_obj = None
        self.fetch_data = ComicServerConn()
        self.last_page_done = False
    def open_mag_glass(self):
        print(self.ids.comic_book_carousel.index)
    
    def on_pre_enter(self):
        self.app.remove_action_bar()
        
    def on_pre_leave(self):
        self.app.add_action_bar()
    
    def load_UserCurrentPage(self):
        for slide in self.ids.comic_book_carousel.slides:
            if slide.comic_page == self.comic_obj.UserCurrentPage:
                self.ids.comic_book_carousel.load_slide(slide)

    def slide_changed(self, index):
        
        if index != None:
            current_page = self.ids.comic_book_carousel.current_slide.comic_page
            comic_obj = self.comic_obj
            comic_Id = comic_obj.Id
            
            update_url = f'{self.api_url}/Comics/{comic_Id}/Progress'
            self.fetch_data.update_progress(update_url,current_page,self)

    def progress_updated(self,req,results):
        pass

    def load_comic_book(self,comic_obj,readinglist_obj):
        
        if self.comic_obj !=None:
            if comic_obj.Id == self.comic_obj.Id:
                return
        self.last_page_done = False
        self.api_key = self.app.config.get('Server', 'api_key')
        config_app = App.get_running_app()
        settings_data = json.loads(settings_json_screen_tap_control)
        for setting in settings_data:
            if setting['type'] == 'options':

                tap_config = config_app.config.get(setting[u'section'], setting[u'key'])
                if tap_config == 'Disabled':
                      self.ids[setting[u'key']].disabled = True

        Loader.pool.tasks.queue.clear()
        self.readinglist_obj = readinglist_obj
        self.comic_obj = comic_obj
        
        comic_book_carousel = self.ids.comic_book_carousel
        comic_book_carousel.clear_widgets()
        if self.scroller:self.scroller.clear_widgets()
        if self.top_pop:self.top_pop.clear_widgets()

    
        number_pages = int(comic_obj.PageCount)
 
        x_title = self.comic_obj.__str__
        scroll = ScrollView( size_hint=(1,1), do_scroll_x=True, do_scroll_y=False,id='page_thumb_scroll')
        self.page_nav_popup = Popup(id='page_nav_popup',title=x_title, content=scroll, pos_hint ={'y': .0401},size_hint = (1,.35))

        self.scroller = scroll
        outer_grid = GridLayout(rows=1, size_hint=(None,None), spacing=5, padding=(5,0), id='outtergrd')
        outer_grid.bind(minimum_width=outer_grid.setter('width'))
        i = 0
            
        self.use_pagination = False
        for i in range(0, number_pages):
            self.add_pages(comic_book_carousel,outer_grid,comic_obj,i)
            if i == comic_obj.UserCurrentPage:              
                m_UserCurrentPage = 'comic_scatter'+str(i)
       
        scroll.add_widget(outer_grid)    
        self.build_top_nav()
        self.next_comic = self.get_next_comic()
        self.prev_comic = self.get_prev_comic()
        self.build_next_comic_dialog()
        self.build_prev_comic_dialog()
        self.app.manager.current = 'comic_book_screen'
        
    def add_pages(self,comic_book_carousel,outer_grid,comic_obj,i):
        #fire off dblpage split if server replies size of image is width>height
        def got_page_size(results):
            if results['width'] > results['height']:
                proxyImage = Loader.image(comic_page_source)
                proxyImage.bind(on_load=partial(comic_page_image._new_image_downloaded,comic_page_scatter,outer_grid,comic_obj,i,comic_page_source))

        
        
        max_height = App.get_running_app().config.get('Server', 'max_height')
        comic_page_scatter = ComicBookPageScatter(id='comic_scatter'+str(i),comic_page=i,do_rotation=False, do_scale=False,
                  do_translation=False)
        s_allow_stretch = App.get_running_app().config.get('Display', 'stretch_image')
        s_keep_ratio = App.get_running_app().config.get('Display', 'keep_ratio')
        # if strech_image == '1':
        #     s_allow_stretch=True
        #     s_keep_ratio=False
        # else:
        #     s_allow_stretch=False
        #     s_keep_ratio=True
        if max_height == 0:
            comic_page_source = f"{self.api_url}/Comics/{comic_obj.Id}/Pages/{i}?apiKey={self.api_key}"
        else:
            comic_page_source = f"{self.api_url}/Comics/{comic_obj.Id}/Pages/{i}?apiKey={self.api_key}&height={round(dp(max_height))}"
        comic_page_image = ComicBookPageImage(comic_slug=comic_obj.slug,
                                             id='pi_'+str(i), 
                                             allow_stretch=s_allow_stretch,
                                             keep_ratio=s_keep_ratio,
                                             comic_page=i,
                                             source=comic_page_source

                                            )
        comic_page_scatter.add_widget(comic_page_image)
        comic_book_carousel.add_widget(comic_page_scatter)
        #Let's make the thumbs for popup
        inner_grid = ThumbPopPageInnerGrid(id='inner_grid'+str(i))
        page_thumb = ComicBookPageThumb(comic_slug=comic_obj.slug,id=comic_page_scatter.id,comic_page=i,
                                        source=f"{self.api_url}/Comics/{comic_obj.Id}/Pages/{i}?height={round(dp(240))}&apiKey={self.api_key}")

        page_thumb.size_hint_y = None
        page_thumb.height = dp(240)
        inner_grid.add_widget(page_thumb)
        page_thumb.bind(on_release=page_thumb.click)
        smbutton = ThumbPopPagebntlbl(text='P%s'%str(i+1),halign='center')
        inner_grid.add_widget(smbutton)
        outer_grid.add_widget(inner_grid)
        
        get_size_url = f"{self.api_url}/Comics/{comic_obj.Id}/Pages/{i}/size?apiKey={self.api_key}"
        self.fetch_data.get_page_size_data(get_size_url,callback=lambda req, results:got_page_size(results) )
        # proxyImage = Loader.image(comic_page_source,nocache=True)
        # proxyImage.bind(on_load=partial(
        #                                comic_page_image._new_image_downloaded, 
        #                                 comic_page_scatter,outer_grid,comic_obj, 
        #                                 i,comic_page_source
        #                                 )
        #                 )
        if comic_obj.PageCount-1 == i:
            self.last_page_done = True
            self.load_UserCurrentPage()
    
    def page_nav_popup_open(self):
        self.page_nav_popup.open()
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        for child in self.walk():
            if child.id == current_slide.id:
                current_page = child

        for child in self.page_nav_popup.walk():
            if child.id == 'page_thumb_scroll':
                scroller = child
                for grandchild in scroller.walk():
                    if grandchild.id == current_page.id:
                        target_thumb = grandchild
                        self.scroller.scroll_to(target_thumb,padding=10, animate=True)
    
    def build_top_nav(self):
        scroll = CommonComicsScroll(id='page_thumb_scroll',size_hint=(1,1), do_scroll_x=True, do_scroll_y=False)
        self.top_pop = Popup(id='page_pop',title='Comics in List', title_align = 'center', 
                            content=scroll, pos_hint ={'y': .7},size_hint = (1,.3)
                            )
        grid = CommonComicsOuterGrid(id='outtergrd',size_hint=(None,None), spacing=5, padding=(5,5))
        grid.bind(minimum_width=grid.setter('width'))
        
        if int(self.app.config.get('Server','use_pagination')) == 1:
            self.paginator = self.app.manager.get_screen('readinglistscreen').paginator
            if self.current_page == None:
                page = self.app.manager.get_screen('readinglistscreen').current_page
                comics_list = page.object_list
                self.current_page = page
                self.top_pop.title = f'Group# {page.number} of {self.paginator.num_pages()}'
            else:
                page = self.current_page
                self.top_pop.title = f'Group# {page.number} of {self.paginator.num_pages()}'
                comics_list = page.object_list  
            if page.has_previous():
                comic_name = 'Prev Page'
                src_thumb = 'assets/prev_page.jpg'
                inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str('prev'), padding=(1,1))
                comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str('prev'))
                comic_thumb.readinglist_obj = self.readinglist_obj
                comic_thumb.readinglist_obj = self.readinglist_obj
                comic_thumb.new_page_num = page.previous_page_number()
                inner_grid.add_widget(comic_thumb)
                comic_thumb.bind(on_release=self.top_pop.dismiss)
                comic_thumb.bind(on_release=self.load_new_page)
                smbutton = CommonComicsCoverLabel(text=comic_name)
                inner_grid.add_widget(smbutton)
                grid.add_widget(inner_grid)
        else:
            comics_list = reversed(self.readinglist_obj.comics)

        for comic in comics_list:
            comic_name = str(comic.__str__)
            src_thumb = f"{self.api_url}/Comics/{comic.Id}/Pages/0?height={round(dp(240))}&apiKey={self.api_key}"
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
        if int(self.app.config.get('Server','use_pagination')) == 1:
            if page.has_next():
                comic_name = 'Next Page'
                src_thumb = 'assets/next_page.jpg'
                inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str('next'))
                comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str('next'))
                comic_thumb.readinglist_obj = self.readinglist_obj
                comic_thumb.readinglist_obj = self.readinglist_obj
                comic_thumb.new_page_num = page.next_page_number()
                inner_grid.add_widget(comic_thumb)
                comic_thumb.bind(on_release=self.top_pop.dismiss)
                comic_thumb.bind(on_release=self.load_new_page)               
                smbutton = CommonComicsCoverLabel(text=comic_name)
                inner_grid.add_widget(smbutton)
                grid.add_widget(inner_grid)
        scroll.add_widget(grid)
    
    def load_new_page(self,instance):
        new_page = self.paginator.page(instance.new_page_num)
        self.current_page = new_page
        
        self.build_top_nav()
        self.top_pop.open()

    def load_next_page_comic(self,instance):
        new_page = self.paginator.page(instance.new_page_num)
        self.current_page = new_page
        n_paginator = self.paginator
        page = self.current_page
        comics_list = page.object_list
        self.load_comic_book(self.next_comic,self.readinglist_obj)
    
    def load_prev_page_comic(self,instance):
        new_page = self.paginator.page(instance.new_page_num)
        self.current_page = new_page
        n_paginator = self.paginator
        page = self.current_page
        comics_list = page.object_list
        self.load_comic_book(self.prev_comic,self.readinglist_obj)

    def get_next_comic(self):
        n_paginator = self.paginator
        page = self.current_page
        comic_obj = self.comic_obj
        comics_list = page.object_list
        index = comics_list.index(comic_obj)

        if comic_obj.Id == comics_list[-1].Id and page.has_next():
            n_page = n_paginator.page(page.next_page_number())
            comics_list = n_page.object_list
            next_comic = comics_list[0]
        else:
            if index >= len(comics_list)-1:
                if len(comics_list)<=1:
                    next_comic = self.comic_obj
                else:
                    next_comic = comics_list[index]
            else:
                if len(comics_list)<=1:
                    next_comic = self.comic_obj
                else:
                    next_comic = comics_list[index+1]
        return next_comic

    def get_prev_comic(self):#TODO Fix when 1 comic is loaded there should not be a next and prev comic.
        n_paginator = self.paginator
        page = self.current_page
        comics_list = page.object_list
        comic_obj = self.comic_obj
        index = comics_list.index(comic_obj)# first index where x appears
        if comic_obj.Id == comics_list[0].Id and page.has_previous():
            n_page = n_paginator.page(page.previous_page_number())
            comics_list = n_page.object_list
            prev_comic = comics_list[-1]
        else:
            if index < len(comics_list):
                if index == 0:
                    if self.section == 'Section' or self.section == 'Last':
                        prev_comic = self.comic_obj


                    else:
                        prev_comic = comics_list[index]
                else:
                    if self.section == 'Section' or self.section == 'Last':
                        prev_comic = self.comic_obj
                    else:
                        prev_comic = comics_list[index-1]
        return prev_comic

    def build_next_comic_dialog(self):
        ''' Make popup showing cover for next comic'''
        n_paginator = self.paginator
        page = self.current_page
        comics_list = page.object_list
        comic = self.next_comic
        comic_obj = self.comic_obj
        index = comics_list.index(comic_obj) # first index where x appears
        if index+1 == len(comics_list) and page.has_next():
            n_page = n_paginator.page(page.next_page_number())
            comics_list = n_page.object_list
            next_page_number = page.next_page_number()
        comic_name = str(comic.__str__)
        src_thumb = f"{self.api_url}/Comics/{comic.Id}/Pages/0?height={round(dp(240))}&apiKey={self.api_key}"
        inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(comic.Id),pos_hint={.5:.5})
        comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(comic.Id),pos_hint={.5:.5})
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        comic_thumb.readinglist_obj = self.readinglist_obj
        if index+1 == len(comics_list) and page.has_next():
            comic_thumb.new_page_num = next_page_number
        else:
            comic_thumb.new_page_num = page.number
        inner_grid.add_widget(comic_thumb)
        
        smbutton = CommonComicsCoverLabel(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list)-1:
            if index+1 == page.end_index():
                dialog_title = 'Load Next Page'
            else:
                dialog_title = 'On Last Comic'
        else:
            if index+1 == page.end_index():
                dialog_title = 'Load Next Page'
            else:
                dialog_title = 'Load Next Comic'
        self.next_dialog = Popup(id='next_pop',title=dialog_title, 
                                content=content, pos_hint ={.5: .724},
                                size_hint=(.25, .25)
                                )
        comic_thumb.bind(on_release=self.next_dialog.dismiss)

        if index >= len(comics_list)-1:
            if len(comics_list)>=1:
                comic_thumb.bind(on_release=self.load_next_page_comic)
            else:
                return
        else:
            if len(comics_list)>=1:
                comic_thumb.bind(on_release=self.load_next_page_comic)
            else:
                comic_thumb.bind(on_release=comic_thumb.open_collection)

    def build_prev_comic_dialog(self):
        n_paginator = self.paginator
        page = self.current_page
        comics_list = page.object_list
        comic = self.prev_comic
        comic_obj = self.comic_obj
        index = comics_list.index(comic_obj) # first index where x appears
        prev_page_number = 1
        if index == 0 and page.has_previous():
            n_page = n_paginator.page(page.previous_page_number())
            comics_list = n_page.object_list
            prev_page_number = page.previous_page_number()
        comic_name = str(comic.__str__)
        src_thumb = f"{self.api_url}/Comics/{comic.Id}/Pages/0?height={round(dp(240))}&apiKey={self.api_key}"
        inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(comic.Id),pos_hint={.5:.5})
        comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(comic.Id),pos_hint={.5:.5})
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        if index == 0 and page.has_previous():
            comic_thumb.new_page_num = prev_page_number
        else:
            comic_thumb.new_page_num = page.number
        comic_thumb.readinglist_obj = self.readinglist_obj
        inner_grid.add_widget(comic_thumb)
        
        smbutton = CommonComicsCoverLabel(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list)-1:
            if len(comics_list)>=1:
                dialog_title = 'Load Prev Page'
            else:
                dialog_title = 'On Last Comic'
        else:
            if len(comics_list)>=1:
                dialog_title = 'Load Prev Page'
            else:
                dialog_title = 'Load Next Comic'

        self.prev_dialog = Popup(id='prev_pop',title=dialog_title, 
                                content=content, pos_hint ={.5: .724},
                                size_hint=(.25, .25)
                                )
        comic_thumb.bind(on_release=self.prev_dialog.dismiss)

        comic_thumb.bind(on_release=self.prev_dialog.dismiss)   
        if index < len(comics_list):
            if index == 0:
                if len(comics_list)>1:
                    comic_thumb.bind(on_release=self.load_prev_page_comic)
                else:
                    return
            else:
                if len(comics_list)>1:
                    comic_thumb.bind(on_release=self.load_prev_page_comic)
                else:
                    comic_thumb.bind(on_release=comic_thumb.open_collection)



    def open_next_dialog(self):
         self.next_dialog.open()
    
    def open_prev_dialog(self):
         self.prev_dialog.open()

    def load_random_comic(self):
       self.top_pop.open()

    def load_next_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if self.comic_obj.PageCount-1 == comic_scatter.comic_page and comic_book_carousel.next_slide == None:
            self.open_next_dialog()
            return
        else:
            comic_book_carousel.load_next()
    
    def load_prev_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if comic_scatter.comic_page == 0 and comic_book_carousel.previous_slide == None:
            self.open_prev_dialog()
            return
        else:
            comic_book_carousel.load_previous()

    def comicscreen_open_collection_popup(self):
        self.top_pop.open()
    




class ComicBookPageControlButton(Button):
    pass