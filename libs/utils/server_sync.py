from kivy.app import App
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from libs.utils.comic_server_conn import ComicServerConn
import ntpath


class SyncServer():

    def __init__(self, **kwa):
        self.progress_bar = ProgressBar()  # instance of ProgressBar created.
        self.app = App.get_running_app()
        self.api_url = self.app.api_url
        self.api_key = self.app.config.get('Server', 'api_key')

    def sync_server_reduced(self, reading_list_obj=None,):
        def my_callback(instance):
            print('Popup', instance, 'is being dismissed but is prevented!')
            return True
        for comic in reading_list_obj.comics:
            file_name = ntpath.basename(comic.file_path)
            lsit_count_url = f'{self.api_url}/Comics/{comic.Id}/Sync/'
            fetch_data = ComicServerConn()
            fetch_data.get_server_file_download(
                lsit_count_url, callback=lambda req,
                results: got_readlist_data(results),
                file_path=f'./sync/{file_name}'
            )

        def give_on_progress(request, current_size, total_size):

            print(f'current_size:{current_size}')

        def got_readlist_data(results):
            print('ok')
        popup = Popup(content=Label(text=reading_list_obj.name),
                      size_hint=(.5, .32))
        # popup.bind(on_dismiss=my_callback)
        popup.open()
