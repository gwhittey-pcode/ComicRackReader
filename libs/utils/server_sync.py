from kivy.app import App
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import ntpath
from kivymd.toast.kivytoast.kivytoast import toast

from libs.utils.comic_server_conn import ComicServerConn


class SyncReadingListObject():

    def __init__(self, reading_list=None, **kwords):
        self.reading_list = reading_list
        self.limit = 50
        self.app = App.get_running_app()
        self.api_url = self.app.api_url
        self.fetch_data = ComicServerConn()
        self.num_file_done = 0

    def sync_delayed_work(self, func, items, delay=0):
        '''Apply the func() on each item contained in items
        '''
        if not items:
            return

        def _sync_delayed_work(*l):
            item = items.pop(0)
            if func(item) is False or not len(items):
                return False
            Clock.schedule_once(_sync_delayed_work, delay)
        Clock.schedule_once(_sync_delayed_work, delay)

    def download_file(self, comic):
        def got_file(results):
            self.num_file_done += 1
            toast(f'{file_name} Synced')
            self.file_download = True
        self.file_download = False
        file_name = ntpath.basename(comic.file_path)
        new_readinglist_reversed = self.reading_list.comics[::-1]
        comic_index = new_readinglist_reversed.index(comic)
        self.app.current_files.put(comic.Id,
                                   file=file_name,
                                   Id=comic.Id,
                                   slug=comic.slug,
                                   data_type='ComicBook',
                                   Series=comic.Series,
                                   Number=comic.Number,
                                   Month=comic.month,
                                   Year=comic.year,
                                   UserCurrentPage=comic.UserCurrentPage,
                                   UserLastPageRead=comic.UserLastPageRead,
                                   PageCount=comic.PageCount,
                                   Summary=comic.Summary,
                                   Index=comic_index,
                                   FilePath=comic.file_path,
                                   ReadlistID=self.reading_list.slug
                                   )
        sync_url = f'{self.api_url}/Comics/{comic.Id}/Sync/'
        print(f'sync_url:{sync_url}')
        self.fetch_data.get_server_file_download(
            sync_url, callback=lambda req,
            results: got_file(results),
            file_path=f'{self.app.sync_dir}/comics/{file_name}'
        )

    def _finish_sync(self, dt):
        def _finish_toast(dt):
            toast('Reading List has been Synceddd')

        list_comics = self.reading_list.comics[:self.limit]
        num_comic = len(list_comics)
        if self.num_file_done == num_comic:
            Clock.schedule_once(_finish_toast, 3)
            self.event.cancel()

    def sync_readinglist(self):
        list_comics = self.reading_list.comics[:self.limit]
        self.sync_delayed_work(self.download_file, list_comics, delay=.5)
        self.event = Clock.schedule_interval(self._finish_sync, 0.5)

        # sync_screen = self.app.manager.get_screen('syncscreen')
        # sync_screen.obj_readinglist = page.object_list
        # self.app.manager.current = 'syncscreen'
