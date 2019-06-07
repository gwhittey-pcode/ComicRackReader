from kivy.uix.screenmanager import Screen
from libs.utils.comic_server_conn import ComicServerConn
from libs.applibs.kivymd.list import OneLineListItem
from libs.applibs.kivymd.accordionlistitem import MDAccordionListItem
from libs.applibs.kivymd.list import OneLineIconListItem,OneLineAvatarListItem
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from libs.applibs.kivymd.button import MDIconButton
from libs.applibs.kivymd.list import ILeftBodyTouch
from libs.applibs.kivymd.list import ILeftBody
from kivy.uix.image import Image
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.app import App
from kivy.logger import Logger



class MyTv(TreeView):
    
    def __init__(self, **kwargs):
        super(MyTv, self).__init__(**kwargs)
    pass

class AvatarSampleWidget(ILeftBody, Image):
    pass

class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass

class SubFolderContent(BoxLayout):
    callback = ObjectProperty(lambda x: None)

class ComicRackListScreen(Screen):
    def __init__(self,**kwargs):
        self.app = App.get_running_app()
        self.fetch_data = None
        self.Data = ''
        self.fetch_data = ComicServerConn()
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        
        super(ComicRackListScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
         self.base_url = self.app.base_url
         self.api_url = self.app.api_url
         self.app.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.app.back_screen(27)]]
         self.get_reading_list()

    def on_leave(self):
        self.app.list_previous_screens.append(self.name)
        
    def get_reading_list(self):
        print('ok')
        url_send = f'{self.api_url}/lists/'
        self.fetch_data.get_server_data(url_send,self)
        
    def open_readinglist(self,instance,node):
        print(instance.id)
        self.app.manager.current = 'readinglistscreen'
        readinglistscreen = self.app.manager.get_screen('readinglistscreen')
        
        readinglist_slug = instance.id
        readinglist_name = (instance.text).split(' : ')[0]
        print(readinglist_name)
        readinglistscreen.collect_readinglist_data(readinglist_name,readinglist_slug)
        
    def callback(instance):
        print('The button <%s> is being pressed' % instance.text)
    
    def got_json(self,req, result):
        self.ids.mytv.clear_widgets()
        self.my_tree = self.ids.mytv
        for item in result:

            if item['Type'] == "ComicLibraryListItem" or item['Type'] == "ComicSmartListItem":
                new_node = self.my_tree.add_node(TreeViewLabel(text=item['Name'],color=(0.9568627450980393,0.2627450980392157,0.21176470588235294,1),id=item['Id']))
                new_node.bind(on_touch_down=self.open_readinglist)
            elif item['Type'] == "ComicListItemFolder":
                parent = self.my_tree.add_node(TreeViewLabel(text=item['Name'],color=(0.9568627450980393,0.2627450980392157,0.21176470588235294,1),id=item['Id']))
                self.set_files(parent, item['Lists'])

        # for item in result: 
        #     strName = f'{item["Name"]}'
        #     if item['Type'] == "ComicLibraryListItem" or item['Type'] == "ComicSmartListItem":
        #         list_item = OneLineAvatarListItem(text=strName, id=item['Id'])
        #         image_widget = AvatarSampleWidget(source='assets/plus_items/ComicIdListItem.png', id=f"icon_{item['Id']}")
        #         list_item.add_widget(image_widget)
        #         self.ids.grid_list.add_widget(list_item)
        #         list_item.bind(on_press =self.open_readinglist)
        #     elif item['Type'] == "ComicListItemFolder":
        #         list_item = OneLineAvatarListItem(text=strName, id=item['Id'])
        #         image_widget = AvatarSampleWidget(source='assets/plus_items/ComicListItemFolder.png', id=f"icon_{item['Id']}")
        #         list_item.add_widget(image_widget)
        #         self.ids.grid_list.add_widget(list_item)
        #         list_item.bind(on_press =self.open_readinglist)
    def set_files(self, parent, child): 
        for item in child:
            if item['Type'] == "ComicLibraryListItem" or item['Type'] == "ComicSmartListItem" or item['Type'] == "ComicIdListItem":
                new_node = self.my_tree.add_node(TreeViewLabel(text=item['Name'],color=(0.9568627450980393,0.2627450980392157,0.21176470588235294,1),id=item['Id']), parent)
                new_node.bind(on_touch_down=self.open_readinglist)
            elif item['Type'] == "ComicListItemFolder":
                sub_parent = self.my_tree.add_node(TreeViewLabel(text=item['Name'],color=(0.9568627450980393,0.2627450980392157,0.21176470588235294,1),id=item['Id']), parent)
                self.set_files(sub_parent, item['Lists'])
                