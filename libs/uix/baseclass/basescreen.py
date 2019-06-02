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
        
    
    def open_lists_screen(self):
       self.app.manager.current = 'comicracklistscreen'
       comicracklistscreen = self.app.manager.get_screen('comicracklistscreen')


    def got_error(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_time_out(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_failure(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_redirect(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))      
