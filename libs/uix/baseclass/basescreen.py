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

from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.logger import Logger
import json

from base64 import b64encode
from kivy.uix.button import Button
import urllib.parse
from libs.utils.comic_server_conn import ComicServerConn
from libs.applibs.kivymd.list import OneLineListItem
from libs.applibs.kivymd.accordionlistitem import MDAccordionListItem
from libs.applibs.kivymd.list import OneLineIconListItem,OneLineAvatarListItem
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from libs.applibs.kivymd.button import MDIconButton
from libs.applibs.kivymd.list import ILeftBodyTouch
from libs.applibs.kivymd.list import ILeftBody
from kivy.uix.image import Image
from libs.applibs.kivymd.toast import toast

class AvatarSampleWidget(ILeftBody, Image):
    pass

class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass

class SubFolderContent(BoxLayout):
    callback = ObjectProperty(lambda x: None)

class BaseScreen(Screen):
    def __init__(self,**kwargs):
        self.app = App.get_running_app()
        self.fetch_data = None
        self.Data = ''
        self.api_key = ''
        self.fetch_data = ComicServerConn()
        self.base_url = self.app.config.get('Server', 'url') + '/BCR'
        super(BaseScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        self.check_login()
        self.get_reading_list()
        
    def get_reading_list(self):
        url_send = f'{self.base_url}/lists/'
        self.fetch_data.get_server_data(url_send,self)
    
    def check_login(self):
        #see if user has a api key stored from server
        self.username = self.app.config.get('Server', 'username')
        self.password = self.app.config.get('Server', 'password')
        self.api_key = self.app.config.get('Server', 'api_key') 
        req_url = f"{self.app.config.get('Server', 'url')}/auth"       
        if self.api_key == '':
            self.fetch_data.get_api_key(req_url,self.username,self.password,self)
    
    def got_api(self,req, result):#get api key from server and store it in settings.
        api_key = result['ApiKey']
        self.app.config.set('Server','api_key',api_key)
        self.app.config.write()
 

    def update_leaf(self):
        Window.fullscreen = 'auto'
        
    def open_readinglist(self,instance):
        self.app.manager.current = 'readinglistscreen'
        readinglistscreen = self.app.manager.get_screen('readinglistscreen')
        readinglist_slug = instance.id
        readinglist_name = (instance.text).split(' : ')[0]
        print(readinglist_name)
        readinglistscreen.collect_readinglist_data(readinglist_name,readinglist_slug)
        
    def callback(instance):
        print('The button <%s> is being pressed' % instance.text)
    
    def got_json(self,req, result):
        self.ids.grid_list.clear_widgets()
        def callback(text):
            toast(f'{text} to {content.name_item}')
                
        def walk_comiclistitemfolder(a_folder,parent_widget):
            print(a_folder['Name'])
            print(parent_widget)
            if len(a_folder) >=1:
                
                for sub_item in a_folder['Lists']:
                    content = SubFolderContent(callback=callback)
                    print(f"{sub_item['Name']} : {sub_item['Type']}")
                    if sub_item['Type'] == "ComicLibraryListItem" or sub_item['Type'] == "ComicSmartListItem" or sub_item['Type'] == 'ComicIdListItem' or sub_item['Type'] == 'ComicSmartListItem':
                        list_item = OneLineAvatarListItem(text=strName, id=sub_item['Id'])
                        image_widget = AvatarSampleWidget(source='assets/plus_items/ComicIdListItem.png', id=f"comic_{sub_item['Id']}")
                        list_item.add_widget(image_widget)
                        content.ids.grid_sublist.add_widget(list_item)
                        list_item.bind(on_press =self.open_readinglist)  
                    elif sub_item['Type'] == "ComicListItemFolder":
                        
                        c = MDAccordionListItem(content=content,
                                                icon='assets/plus_items/ComicListItemFolder.png', title=sub_item['Name'], id=sub_item['Id'])
                        d = content.ids.grid_sublist.add_widget(c)
                        walk_comiclistitemfolder(sub_item,c)

        
        
        
        
        content = SubFolderContent()
        for item in result: 
            strName = f'{item["Name"]}'
            if item['Type'] == "ComicLibraryListItem" or item['Type'] == "ComicSmartListItem":
                list_item = OneLineAvatarListItem(text=strName, id=item['Id'])
                image_widget = AvatarSampleWidget(source='assets/plus_items/ComicIdListItem.png', id=f"icon_{item['Id']}")
                list_item.add_widget(image_widget)
                self.ids.grid_list.add_widget(list_item)
                list_item.bind(on_press =self.open_readinglist)
            elif item['Type'] == "ComicListItemFolder":
                
                c = MDAccordionListItem(content=content,
                                        icon='assets/plus_items/ComicListItemFolder.png', title=strName, id=item['Id'])
                self.ids.grid_list.add_widget(c)
                #walk_comiclistitemfolder(item,c)
        
       
        

                

        def iterate(dictionary):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    iterate(value)
                    continue
            print('key {!r} -> value {!r}'.format(key, value))
        for item in result:
            print(item) 
            iterate(item)
 


    def got_error(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_time_out(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_failure(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_redirect(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))      
