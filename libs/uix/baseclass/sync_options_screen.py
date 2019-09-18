from kivy.uix.screenmanager import Screen
from libs.utils.comic_server_conn import ComicServerConn
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.menu import MDDropdownMenu, MDMenuItem
from kivymd.uix.textfield import MDTextFieldRound, FixedHintTextInput
from kivy.uix.image import Image
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.properties import StringProperty, ListProperty, OptionProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.logger import Logger
from kivymd.uix.list import (
    ILeftBody,
    ILeftBodyTouch,
    IRightBodyTouch,
    OneLineIconListItem,
    OneLineAvatarIconListItem,
)
from kivymd.uix.button import MDIconButton


class MyTv(TreeView):
    def __init__(self, **kwargs):
        super(MyTv, self).__init__(**kwargs)
    pass


class ReadingListOptions(Widget):
    pass


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass


class AvatarSampleWidget(ILeftBody, MDIconButton):
    pass


class MyMDTextFieldRound(MDTextFieldRound, FixedHintTextInput):
    def __init__(self, **kwargs):
        super(MyMDTextFieldRound, self).__init__(**kwargs)
    helper_text = StringProperty("This field is required")
    helper_text_mode = OptionProperty(
        "none", options=["none", "on_error", "persistent", "on_focus"]
    )


class IconRightSampleWidget(IRightBodyTouch, MDCheckbox):
    def __init__(self, **kwargs):
        super(IconRightSampleWidget, self).__init__(**kwargs)

    def statechange(self, instance):
        print('State Change')

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)
        print('touch down')


class TreeViewRLNode2(OneLineAvatarIconListItem, TreeViewNode):
    text = StringProperty()
    color = ListProperty([0.4, 0.4, 0.4, 1])
    icon = StringProperty('folder')

    def __init__(self, **kwargs):
        super(TreeViewRLNode2, self).__init__(**kwargs)


class SyncOptions(Screen):
    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        self.fetch_data = None
        self.Data = ''
        self.fetch_data = ComicServerConn()
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        super(SyncOptions, self).__init__(**kwargs)
        self.lists_loaded = BooleanProperty()
        self.lists_loaded = False

    def on_pre_enter(self):
        self.app.show_action_bar()

    def on_enter(self, *args):
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        if self.lists_loaded is False:
            self.get_comicrack_list()
        self.app.set_screen('ComicRack Lists')

    def on_leave(self):
        self.app.list_previous_screens.append(self.name)

    def get_comicrack_list(self):
        url_send = f'{self.api_url}/lists/'
        self.fetch_data.get_server_data(url_send, self)

    def open_readinglist(self, instance, node):
        item_ckbox = instance.ids.chkbox.state

    def got_json(self, req, result):
        self.ids.mytv.clear_widgets()
        self.my_tree = self.ids.mytv
        self.my_tree.clear_widgets()
        self.my_tree.bind(minimum_height=self.my_tree.setter('height'))
        for item in result:
            if item['Type'] == "ComicLibraryListItem" or\
                    item['Type'] == "ComicSmartListItem":
                new_node = self.my_tree.add_node(TreeViewRLNode2(
                    text=item['Name'], color=(
                        0.9568627450980393, 0.2627450980392157,
                        0.21176470588235294, 1), id=item['Id']))
                new_node.bind(on_touch_down=self.open_readinglist)
            elif item['Type'] == "ComicListItemFolder":
                parent = self.my_tree.add_node(
                    TreeViewRLNode2(text=item['Name'], color=(
                        0.9568627450980393, 0.2627450980392157,
                        0.21176470588235294, 1), id=item['Id']))
                self.set_files(parent, item['Lists'])
        self.lists_loaded = True

    def set_files(self, parent, child):
        for item in child:
            if item['Type'] == "ComicLibraryListItem" or\
                    item['Type'] == "ComicSmartListItem" or\
                    item['Type'] == "ComicIdListItem":
                new_node = self.my_tree.add_node(TreeViewRLNode2(
                    text=f'    {item["Name"]}', color=(
                        0.9568627450980393, 0.2627450980392157,
                        0.21176470588235294, 1), id=item['Id']), parent)
                new_node.bind(on_touch_down=self.open_readinglist)
            elif item['Type'] == "ComicListItemFolder":
                sub_parent = self.my_tree.add_node(TreeViewRLNode2(
                    text=item['Name'], color=(
                        0.9568627450980393, 0.2627450980392157,
                        0.21176470588235294, 1), id=item['Id']), parent)
                self.set_files(sub_parent, item['Lists'])
