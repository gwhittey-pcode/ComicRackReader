from kivy.app import App
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import ntpath
from kivymd.toast.kivytoast.kivytoast import toast
from libs.utils.comic_server_conn import ComicServerConn
from pathlib import Path
import os
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
from libs.utils.db_functions import ReadingList, Comic
"""
NOTE: Sync outline
    - hit sync button:
        TODO: check for last read comic using comic.UserLastPageRead(0 base index) and compare it with PageCount(1 index so needs -1)
        TODO: add in db functions
        
"""
SYNC_SETTINGS_ITEMS = [
    'cb_limit_state',
    'limit_num',
    'cb_only_read_state',
    'cb_keep_last_read_state',
    'cb_optimize_size_state',
    'sw_syn_this_active', ]


class SyncReadingListObject(object):
    cb_only_read_state = 'normal'
    cb_keep_last_read_state = 'normal'
    cb_optimize_size_state = 'normal'
    cb_limit_state = 'normal'
    limit_num = 25
    sw_syn_this_active = False

    def __init__(self, reading_list=None, **kwords):
        self.reading_list = reading_list

        self.app = App.get_running_app()
        self.api_url = self.app.api_url
        self.fetch_data = ComicServerConn()
        self.num_file_done = 0
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
        id_folder = os.path.join(self.app.sync_folder, self.reading_list.slug)
        my_data_dir = Path(os.path.join(id_folder, 'data'))
        self.my_comic_dir = Path(os.path.join(id_folder, 'comics'))
        self.my_thumb_dir = Path(os.path.join(self.my_comic_dir, 'thumb'))
        if not self.my_comic_dir.is_dir():
            os.makedirs(self.my_comic_dir)
        if not self.my_thumb_dir.is_dir():
            os.makedirs(self.my_thumb_dir)
        try:
            db_item = ReadingListLSyncSettings.readinglists.get(
                ReadingList.slug == self.reading_list.slug)
            print(db_item.cb_limt_state)
        except:
            print('error')
        # for item in SYNC_SETTINGS_ITEMS:
        #    val = ""
        #    tmp_defaults[key] = getattr(self, key)
        # NOTE: can be removed once DB functions added
        if not my_data_dir.is_dir():
            os.makedirs(my_data_dir)
        settings_json = os.path.join(my_data_dir, 'settings.json')
        comics_json = os.path.join(my_data_dir, 'sync_comics.json')
        self.this_test = "Test"
        self.sync_data = JsonStore(settings_json)
        self.sync_comics = JsonStore(comics_json)
        self.last_read_comic = self.get_last_comic_read()
        if self.sync_data.exists('options'):
            self.cb_only_read_state = self.sync_data.get(
                "options")["cb_only_read_state"]
            self.cb_keep_last_read_state = self.sync_data.get(
                "options")["cb_keep_last_read_state"]
            self.cb_optimize_size_state = self.sync_data.get(
                "options")["cb_optimize_size_state"]
            self.cb_limit_state = self.sync_data.get("options")[
                "cb_limit_state"]
            self.limit_num = self.sync_data.get("options")["limit_num"]
            self.sw_syn_this_active = self.sync_data.get("options")[
                'sw_syn_this_active']
        else:
            self.cb_only_read_state = 'normal'
            self.cb_keep_last_read_state = 'normal'
            self.cb_optimize_size_state = 'normal'
            self.cb_limit_state = 'normal'
            self.limit_num = 25
            self.sw_syn_this_active = False
        # end note

        self.last = 0
        self.limit = 25
        self.sync_range = int(self.last) + int(self.limit_num)
        self.api_key = self.app.config.get('General', 'api_key')

    def get_comics(self):
        self.sync_comics.get()

    def get_last_comic_read(self):
        last_read_comic = "None Read"
        for comic in self.reading_list.comics:
            if comic.UserLastPageRead == comic.PageCount-1:
                last_read_comic = self.reading_list.comics.index(comic)
                print(f'last_read_comic:{last_read_comic}')
        return last_read_comic

    def save_values(self,
                    cb_limit_state=cb_limit_state,
                    limit_num=limit_num,
                    cb_only_read_state=cb_only_read_state,
                    cb_keep_last_read_state=cb_keep_last_read_state,
                    cb_optimize_size_state=cb_optimize_size_state,
                    sw_syn_this_active=sw_syn_this_active,
                    *args, **kwargs):
        # self.sync_data.put()

        self.sync_data.put('options',
                           cb_limit_state=cb_limit_state,
                           limit_num=limit_num,
                           cb_only_read_state=cb_only_read_state,
                           cb_keep_last_read_state=cb_keep_last_read_state,
                           cb_optimize_size_state=cb_optimize_size_state,
                           sw_syn_this_active=sw_syn_this_active
                           )
        self.cb_only_read_state = cb_only_read_state
        self.cb_keep_last_read_state = cb_keep_last_read_state
        self.cb_optimize_size_state = cb_optimize_size_state
        self.cb_limit_state = cb_limit_state
        self.limit_num = limit_num
        self.sync_range = int(self.last) + int(self.limit_num)
        self.sw_syn_this_active = sw_syn_this_active

    def download_file(self, comic):
        comic_index = 0
        self.file_download = False
        file_name = ntpath.basename(comic.FilePath)
        for i, j in enumerate(self.reading_list.comics):
            if j.Id == comic.Id:
                comic_index = i

        def got_file(results):
            self.num_file_done += 1
            toast(f'{file_name} Synced')
            self.file_download = True
            self.sync_comics.put(comic.Id,
                                 file=file_name,
                                 slug=comic.slug,
                                 data_type='ComicBook',
                                 Series=comic.Series,
                                 Number=comic.Number,
                                 Month=comic.Month,
                                 Year=comic.Year,
                                 UserCurrentPage=comic.UserCurrentPage,
                                 UserLastPageRead=comic.UserLastPageRead,
                                 PageCount=comic.PageCount,
                                 Summary=comic.Summary,
                                 Index=comic_index,
                                 FilePath=comic.FilePath,
                                 ReadlistID=self.reading_list.slug
                                 )

        def got_thumb(results):
            pass

        x = self.comic_thumb_width
        y = self.comic_thumb_height
        thumb_size = f'height={y}&width={x}'
        part_url = f'/Comics/{comic.Id}/Pages/0?'
        part_api = f'&apiKey={self.api_key}&height={round(dp(y))}'
        thumb_url = f"{self.api_url}{part_url}{part_api}"

        if self.cb_optimize_size_state == 'normal':
            sync_url = f'{self.api_url}/Comics/{comic.Id}/File/'
        elif self.cb_optimize_size_state == 'down':
            sync_url = f'{self.api_url}/Comics/{comic.Id}/Sync/'

        self.fetch_data.get_server_file_download(
            sync_url, callback=lambda req,
            results: got_file(results),
            file_path=os.path.join(self.my_comic_dir, file_name)

        )
        thumb_name = f'{comic.Id}.jpg'
        self.fetch_data.get_server_file_download(thumb_url,
                                                 callback=lambda req, results: got_thumb(
                                                     results),
                                                 file_path=os.path.join(
                                                     self.my_thumb_dir, thumb_name)

                                                 )

    def _finish_sync(self, dt):
        def _finish_toast(dt):
            toast('Reading List has been Synceddd')

        list_comics = self.reading_list.comics
        sync_num_comics = list_comics[self.last: self.sync_range]
        num_comic = len(sync_num_comics)
        if self.num_file_done == num_comic:
            Clock.schedule_once(_finish_toast, 3)
            self.event.cancel()

    def sync_readinglist(self):
        list_comics = self.reading_list.comics
        sync_num_comics = list_comics[self.last: self.sync_range]

        print(len(sync_num_comics))
        self.app.delayed_work(
            self.download_file, sync_num_comics, delay=.5)
        self.event = Clock.schedule_interval(self._finish_sync, 0.5)

        # sync_screen = self.app.manager.get_screen('syncscreen')
        # sync_screen.obj_readinglist = page.object_list
        # self.app.manager.current = 'syncscreen'
