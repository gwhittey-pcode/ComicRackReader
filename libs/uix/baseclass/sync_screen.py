import os
import ntpath
from kivy.uix.screenmanager import Screen
from libs.utils.comic_server_conn import ComicServerConn
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty

from kivy.uix.image import Image
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.app import App
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest

from kivymd.toast.kivytoast.kivytoast import toast
from kivymd.uix.progressloader import MDProgressLoader
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import ILeftBodyTouch, ILeftBody
from kivy.clock import Clock


class MyMDProgressLoader(MDProgressLoader):

    def __init__(self, **kwargs):
        super(MyMDProgressLoader, self).__init__(**kwargs)
        pass
        self.app = App.get_running_app()

    def retrieve_progress_load(self, url, path):
        """
        :type url: str;
        :param url: link to content;

        :type path: str;
        :param path: path to save content;
        """
        username = self.app.config.get('Server', 'username')
        api_key = self.app.config.get('Server', 'api_key')
        str_cookie = f'API_apiKey={api_key}; BCR_username={username}'
        head = {'Content-Type': "application/json",
                'Accept': "application/json",
                'Cookie': str_cookie

                }
        print('ok')
        req = UrlRequest(
            url,
            req_headers=head,
            on_progress=self.update_progress,
            chunk_size=1024,
            on_success=self.on_success,
            file_path=path,
        )


class SyncScreen(Screen):
    obj_readinglist = ObjectProperty()

    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        self.fetch_data = None
        self.Data = ''
        self.fetch_data = ComicServerConn()
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        super(SyncScreen, self).__init__(**kwargs)
        self.lists_loaded = BooleanProperty()
        self.lists_loaded = False
        self.api_key = self.app.config.get('Server', 'api_key')
        self.file_download = True

    def set_chevron_back_screen(self):
        '''Sets the return chevron to the previous screen in ToolBar.'''

        pass

    def download_progress_hide(self, instance_progress, value):
        '''Hides progress progress.'''
        pass

    def download_progress_show(self, instance_progress):
        self.set_chevron_back_screen()
        instance_progress.open()
        instance_progress.animation_progress_from_fade()

    def delayed_work(self, func, items, delay=0):
        '''Apply the func() on each item contained in items
        '''
        if not items:
            return

        def _finish_toast(self):
            toast('Reading List has been Synced')

        def _delayed_work(*l):
            if self.file_download is not False:
                item = items.pop()
                if func(item) is False or not len(items):
                    Clock.schedule_once(_finish_toast, 3)
                    return False
                Clock.schedule_once(_delayed_work, delay)
            else:
                Clock.schedule_once(_delayed_work, delay)
        Clock.schedule_once(_delayed_work, delay)

    def create_image(self, comic):

        def got_file(results):
            toast(f'{file_name} Synced')
            self.file_download = True
        self.file_download = False
        file_name = ntpath.basename(comic.file_path)
        lsit_count_url = f'{self.api_url}/Comics/{comic.Id}/Sync/'
        self.fetch_data.get_server_file_download(
            lsit_count_url, callback=lambda req,
            results: got_file(results),
            file_path=f'./sync/{file_name}'
        )

    def show_example_download_file(self):
        list_comics = self.obj_readinglist
        self.delayed_work(self.create_image, list_comics, delay=.5)
        # for comic in list_comics:
        #     file_name = ntpath.basename(comic.file_path)
        #     lsit_count_url = f'{self.api_url}/Comics/{comic.Id}/Sync/'
        #     self.fetch_data.get_server_file_download(
        #         lsit_count_url, callback=lambda req,
        #         results: got_readlist_data(results),
        #         file_path=f'./sync/{file_name}'
        #     )

        def give_on_progress(request, current_size, total_size):
            toast('Started')

        def got_readlist_data(results):
            print('ok')
        # self.sync_file()

    def sync_file(self):
        def download_complete():
            toast('Done')
        for comic in self.obj_readinglist:
            file_name = ntpath.basename(comic.file_path)
            file_link = f'{self.api_url}/Comics/{comic.Id}/Sync/'

            progress = MyMDProgressLoader(
                url_on_image=file_link,
                path_to_file=os.path.join('sync/', file_name),
                download_complete=download_complete,
                download_hide=self.download_progress_hide
            )
            progress.label_download = "File Is Downing"
            progress.start(self.ids.box)
