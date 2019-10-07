import ntpath
import os
import pickle
from functools import partial
from pathlib import Path
from time import sleep
import peewee
from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivymd.toast.kivytoast.kivytoast import toast
from kivy.network.urlrequest import UrlRequest
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.db_functions import Comic, ComicIndex, ReadingList
from kivymd.uix.dialog import MDDialog

CHECKBOX_STATE_BOOL = {"normal": False, "down": True}
READINGLIST_DB_KEYS = [
    "name",
    "cb_limit_active",
    "limit_num",
    "cb_only_read_active",
    "cb_purge_active",
    "cb_optimize_size_active",
    "sw_syn_this_active",
    "end_last_sync_num",
    "totalCount",
    "data",
]

READINGLIST_SETTINGS_KEYS = [
    "cb_limit_active",
    "limit_num",
    "cb_only_read_active",
    "cb_purge_active",
    "cb_optimize_size_active",
    "sw_syn_this_active",
]
COMIC_DB_KEYS = [
    "Id",
    "Series",
    "Number",
    "Volume",
    "Year",
    "Month",
    "UserCurrentPage",
    "UserLastPageRead",
    "PageCount",
    "Summary",
    "FilePath",
    "local_file",
    "data",
    "is_sync",
]


def get_size(start_path="."):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


class ComicBook(EventDispatcher):
    """
    class representing a single comic
    """

    Id = StringProperty()
    __str__ = StringProperty()
    slug = StringProperty()
    name = StringProperty()
    Number = StringProperty()
    Series = StringProperty()
    date = StringProperty()
    Year = NumericProperty()
    Month = NumericProperty()
    UserLastPageRead = NumericProperty()
    UserCurrentPage = NumericProperty()
    PageCount = NumericProperty()
    Summary = StringProperty()
    FilePath = StringProperty()
    Volume = NumericProperty()
    readlist_obj = ObjectProperty()
    local_file = StringProperty("None")
    is_sync = BooleanProperty(False)
    data = DictProperty()
    order_index = NumericProperty()

    def __init__(
        self,
        data=None,
        readlist_obj=None,
        comic_Id="",
        comic_index=0,
        mode="Server",
        *args,
        **kwargs,
    ):
        self.readlist_obj = readlist_obj
        if mode in ("Server", "FileOpen"):
            if comic_Id == "":
                comic_data = data
                self.data = comic_data
                self.Id = comic_data["Id"]
                self.__str__ = "{} #{}".format(
                    comic_data["Series"], comic_data["Number"]
                )
                self.slug = str(comic_data["Id"])
                self.name = f"{comic_data['Series']} #{comic_data['Number']}"
                self.Number = comic_data["Number"]
                self.Series = comic_data["Series"]
                self.date = f"{comic_data['Month']}/{comic_data['Year']}"
                self.Year = comic_data["Year"]
                self.Month = comic_data["Month"]
                self.UserLastPageRead = comic_data["UserLastPageRead"]
                self.UserCurrentPage = comic_data["UserCurrentPage"]
                self.PageCount = comic_data["PageCount"]
                self.Summary = comic_data["Summary"]
                self.FilePath = comic_data["FilePath"]
                self.Volume = comic_data["Volume"]
                app = App.get_running_app()
                self.comic_jsonstore = app.comic_db
                self.readlist_obj = readlist_obj
                self.comic_index = comic_index
                self.local_file = ""
                if mode != "FileOpen":
                    Clock.schedule_once(
                        lambda dt: self.get_or_create_db_item(), 0.15
                    )
        if mode == "db_data":
            self.Id = comic_Id
        if mode != "FileOpen":
            # Clock.schedule_once(
            #    lambda dt: self.get_or_create_db_item())
            self.get_or_create_db_item()

    def get_or_create_db_item(self):
        tmp_defaults = {}
        for key in COMIC_DB_KEYS:
            if key == "comic_index":
                pass
            elif key == "data":
                new_dict = {k: self.data[k] for k in self.data.keys()}
                tmp_defaults["data"] = new_dict
            else:
                tmp_defaults[key] = getattr(self, key)

        db_item, created = Comic.get_or_create(
            Id=self.Id, defaults=tmp_defaults
        )
        if created is True:
            rl = self.readlist_obj
            db_item.comic_index.index = self.comic_index
            comic_index_db, created_index = ComicIndex.get_or_create(
                comic=db_item, readinglist=rl.db, index=self.comic_index
            )
            db_item.save()
            if rl.slug not in [item.slug for item in db_item.readinglists]:
                rl.db.comics.add(db_item)
        else:
            for key in COMIC_DB_KEYS:
                if key == "comic_index":
                    pass
                else:
                    setattr(self, key, getattr(db_item, key))
            self.__str__ = f"{db_item.Series} #{db_item.Number}"
            self.name = self.__str__
            self.date = f"{db_item.Month}/{db_item.Year}"
            self.slug = str(self.Id)

            self.comic_index = db_item.comic_index.select(
                ReadingList.slug == self.readlist_obj.slug
            )

    def update(self, key_list=()):
        for key, value in key_list:
            print(f"key:{key}\nval:{value}")

    def callback(self, store, key, result):
        pass

    def set_is_sync(self):
        try:
            db_item = ComicIndex.get(
                ComicIndex.comic == self.Id,
                ComicIndex.readinglist == self.readlist_obj.slug,
            )
            if db_item:
                if db_item.is_sync:
                    setattr(self, "is_sync", db_item.is_sync)
        except peewee.IntegrityError:
            Logger.error("Somthing went wrong")


class ComicReadingList(EventDispatcher):

    # ids = DictProperty({})
    name = StringProperty()
    comics = ListProperty()
    data = DictProperty()
    slug = StringProperty()
    comic_db = ObjectProperty()
    comic_json = ListProperty()
    cb_only_read_active = BooleanProperty(False)
    cb_only_read_active = BooleanProperty(False)
    cb_purge_active = BooleanProperty(False)
    cb_optimize_size_active = BooleanProperty(False)
    cb_limit_active = BooleanProperty(False)
    limit_num = NumericProperty(25)
    sw_syn_this_active = BooleanProperty(False)
    comic_db_in = BooleanProperty(False)
    db = ObjectProperty()
    comics_loaded = ObjectProperty(False)
    last_comic_read = NumericProperty()
    start_last_sync_num = NumericProperty(0)
    end_last_sync_num = NumericProperty(0)
    totalCount = NumericProperty()
    pickled_data = ObjectProperty()
    sync_list = ListProperty()

    def __init__(self, name="", data=None, slug="", mode="Server"):
        self.slug = slug
        self.name = name
        self.event = None
        if data != "db_data":

            self.pickled_data = pickle.dumps(data, -1)
            self.data = pickle.loads(self.pickled_data)
            self.comic_json = self.data["items"]
            if mode != "FileOpen":
                if name == "Single_FileLoad":
                    self.totalCount = 0
                else:
                    self.totalCount = self.data["totalCount"]
        if mode != "FileOpen":
            self.get_or_create_db_item(mode=mode)

    def add_comic(self, comic, index=0):
        """
            Add Single comic book to this colection
        """
        self.comics.insert(0, comic)

    def get_or_create_db_item(self, mode):
        tmp_defaults = {}
        try:
            for key in READINGLIST_DB_KEYS:
                if key == "data":
                    new_dict = {k: self.data[k] for k in self.data.keys()}
                    tmp_defaults["data"] = new_dict
                else:
                    tmp_defaults[key] = getattr(self, key)
            db_item, created = ReadingList.get_or_create(
                slug=self.slug, defaults=tmp_defaults
            )
            self.db = db_item
            if db_item:
                for key in READINGLIST_DB_KEYS:
                    setattr(self, key, getattr(db_item, key))
                if created is True:
                    len_dbcomics = len(db_item.comics)
                    if (
                        len_dbcomics == len(self.comic_json)
                        and len(self.comic_json) != 0
                    ):
                        self.comic_db_in = True
                        self.comics = self.db.comics.order_by(
                            -Comic.comic_index.index
                        )
                else:
                    self.comic_db_in = True
                    comicindex_db = ComicIndex.get(
                        ComicIndex.readinglist == self.slug
                    )
                    if mode == "local_file":
                        list_comics = self.db.comics.where(
                            Comic.is_sync == True, Comic.local_file != ""
                        ).order_by(  # noqa
                            comicindex_db.index
                        )
                        print(f"len:{len(list_comics)}")
                    else:
                        list_comics = self.db.comics.order_by(
                            comicindex_db.index
                        )
                    for comic in list_comics:
                        new_comic = ComicBook(
                            comic_Id=comic.Id,
                            readlist_obj=self,
                            mode="db_data",
                        )
                        self.comics.append(new_comic)
                    self.comics_loaded = True
        except peewee.OperationalError:
            Logger.critical(
                "Somthing happened in get_or_create of readinglist"
            )

    def save_settings(self, *args, **kwargs):
        try:
            rl = ReadingList.get(ReadingList.slug == self.slug)
            for key in READINGLIST_SETTINGS_KEYS:
                setattr(rl, key, kwargs[key])
                setattr(self, key, kwargs[key])
            rl.save()
        except peewee.OperationalError:
            pass

    def do_db_refresh(self, screen=None):
        def __finish_toast(dt):
            app = App.get_running_app()
            screen = app.manager.get_screen("server_readinglists_screen")
            screen.refresh_callback()
            toast("DataBase Refresh Complete")

        def __got_readlist_data(results):
            def __updated_progress(results):
                pass

            the_keys = [
                "Id",
                "Series",
                "Number",
                "Volume",
                "Year",
                "Month",
                "UserCurrentPage",
                "UserLastPageRead",
                "PageCount",
                "Summary",
                "FilePath",
            ]
            for server_comic in results["items"]:
                for db_comic in self.comics:
                    if db_comic.Id == server_comic["Id"]:
                        for key in the_keys:
                            if getattr(db_comic, key) != server_comic[key]:
                                if key in (
                                    "UserCurrentPage",
                                    "UserLastPageRead",
                                ) and (db_comic.is_sync):
                                    if (
                                        db_comic.UserLastPageRead
                                        > server_comic["UserLastPageRead"]
                                    ) or (
                                        db_comic.UserCurrentPage
                                        > server_comic["UserCurrentPage"]
                                    ):
                                        if (
                                            db_comic.UserCurrentPage
                                            > db_comic.UserLastPageRead
                                        ):
                                            current_page = (
                                                db_comic.UserCurrentPage
                                            )  # noqa
                                        else:
                                            current_page = (
                                                db_comic.UserLastPageRead
                                            )  # noqa
                                        update_url = "{}/Comics/{}/Progress".format(
                                            api_url, db_comic.Id
                                        )
                                        self.fetch_data.update_progress(
                                            update_url,
                                            current_page,
                                            callback=lambda req, results: __updated_progress(
                                                results
                                            ),
                                        )
                                    else:
                                        x_str = db_comic.__str__
                                        Logger.info(
                                            "Updating DB Record for {} of {}".format(
                                                key, x_str
                                            )
                                        )
                                        toast(
                                            "Updating DB Record for {} of {}".format(
                                                key, x_str
                                            )
                                        )
                                        db_item = Comic.get(
                                            Comic.Id == db_comic.Id
                                        )
                                        if db_item:
                                            setattr(
                                                db_item, key, server_comic[key]
                                            )
                                            db_item.save()
                                            setattr(self, key, db_item)

            Clock.schedule_once(__finish_toast, 3)

        self.fetch_data = ComicServerConn()
        app = App.get_running_app()
        api_url = app.api_url
        server_url = f"{api_url}/Lists/{self.slug}/Comics/"

        self.fetch_data.get_server_data_callback(
            server_url,
            callback=lambda req, results: __got_readlist_data(results),
        )

    def get_last_comic_read(self):
        last_read_comic = 0
        for comic in self.comics:
            if (
                comic.UserLastPageRead == comic.PageCount - 1
                and comic.PageCount > 1
            ):
                last_read_comic = self.comics.index(comic)
        return last_read_comic

    def do_sync(self):
        def _syncrun_callback(*args):
            pass

        app = App.get_running_app()
        if app.sync_is_running is True:
            self.please_wait_dialog = MDDialog(
                title="Sync Already in Progress",
                size_hint=(0.8, 0.4),
                text_button_ok="Ok",
                text=f"Please wait till current Sync is done",
                events_callback=_syncrun_callback,
            )
            self.please_wait_dialog.open()
            return
        if self.event is not None:
            toast("Sync Already In Progress wait till it finshes")
            return
        self.num_file_done = 0
        sync_range = 0
        self.fetch_data = ComicServerConn()
        rl_db = ReadingList.get(ReadingList.slug == self.slug)

        end_last_sync_num = rl_db.end_last_sync_num
        if end_last_sync_num != 0:
            end_last_sync_num = end_last_sync_num - 1
        comicindex_db = ComicIndex.get(ComicIndex.readinglist == self.slug)
        last_read_comic_db = self.db.comics.where(
            (Comic.UserLastPageRead == Comic.PageCount - 1)
            & (Comic.PageCount > 1)
        ).order_by(comicindex_db.index)
        if len(last_read_comic_db) > 1:
            last_read_index = ComicIndex.get(
                ComicIndex.comic == last_read_comic_db[-1].Id,
                ComicIndex.readinglist == self.slug,
            ).index
        elif len(last_read_comic_db) != 0:
            last_read_index = ComicIndex.get(
                ComicIndex.comic == last_read_comic_db[0].Id,
                ComicIndex.readinglist == self.slug,
            ).index
        else:
            last_read_index = 0

        if self.cb_limit_active:
            if self.cb_only_read_active:
                list_comics = self.db.comics.where(
                    ~(Comic.UserLastPageRead == Comic.PageCount - 1)
                    & (Comic.PageCount > 1)
                    & (Comic.been_sync)
                    != True
                ).order_by(
                    comicindex_db.index
                )  # noqa: E712
                if last_read_index < end_last_sync_num:
                    sync_range = int(self.limit_num)
                    tmp_comic_list = list_comics[0:sync_range]
                else:
                    sync_range = int(end_last_sync_num) + int(self.limit_num)
                    tmp_comic_list = list_comics[end_last_sync_num:sync_range]
                purge_list = self.db.comics.where(
                    (Comic.UserLastPageRead == Comic.PageCount - 1)
                    & (Comic.PageCount > 1)
                    & (Comic.is_sync == True)
                ).order_by(
                    comicindex_db.index
                )  # noqa: E712
                new_end_last_sync_num = int(end_last_sync_num) + int(
                    len(tmp_comic_list)
                )
                # rl_db.end_last_sync_num = new_end_last_sync_num
                # rl_db.save()
            else:
                list_comics = Comic.select().where(
                    (Comic.is_sync == False) & (Comic.been_sync == False)
                ).order_by(
                    comicindex_db.index
                )  # noqa: E712,E501
                for comic in list_comics:
                    print(comic.Id)
                sync_range = int(self.limit_num)
                tmp_comic_list = list_comics[0:sync_range]
                purge_list = self.db.comics.where(
                    Comic.is_sync == True
                ).order_by(
                    comicindex_db.index
                )  # noqa: E712
                new_end_last_sync_num = int(end_last_sync_num) + int(
                    len(tmp_comic_list)
                )
                # rl_db.end_last_sync_num = new_end_last_sync_num
                # rl_db.save()
        else:
            sync_range = len(self.comics)
            # rl_db.end_last_sync_num = new_end_last_sync_num
            # rl_db.save()
            if self.cb_only_read_active:
                list_comics = self.db.comics.where(
                    ~(Comic.UserLastPageRead == Comic.PageCount - 1)
                    & (Comic.PageCount > 1)
                ).order_by(
                    comicindex_db.index
                )  # noqa: E712
                tmp_comic_list = list_comics[0:sync_range]
            else:
                list_comics = self.db.comics.where(
                    (Comic.is_sync == False) & (Comic.been_sync == False)
                ).order_by(
                    comicindex_db.index
                )  # noqa: E712,E501
                tmp_comic_list = list_comics[end_last_sync_num:sync_range]
        db_item = ReadingList.get(ReadingList.slug == self.slug)
        for key in READINGLIST_SETTINGS_KEYS:
            v = getattr(db_item, key)
            globals()["%s" % key] = v
        app = App.get_running_app()
        id_folder = os.path.join(app.sync_folder, self.slug)
        my_comic_dir = Path(os.path.join(id_folder, "comics"))
        if os.path.isdir(my_comic_dir):
            print(f"{get_size(my_comic_dir)/1000000} MB")
        sync_comic_list = []
        for comic in tmp_comic_list:
            if comic.is_sync is False:
                sync_comic_list.append(comic)
        if self.cb_purge_active:
            for item in purge_list:
                os.remove(item.local_file)
                db_comic = Comic.get(Comic.Id == item.Id)
                db_comic.is_sync = False
                db_comic.local_file = ""
                db_comic.save()
        self.sync_readinglist(comic_list=sync_comic_list)

    def get_server_file_download(self, req_url, callback, file_path):
        def is_finished(dt):
            if req.is_finished is True:
                app = App.get_running_app()
                screen = app.manager.get_screen("server_readinglists_screen")
                screen.ids.sync_button.enabled = True
                Clock.schedule_once(self.download_file)
            else:
                Clock.schedule_once(is_finished, 0.25)

        app = App.get_running_app()
        username = app.config.get("General", "username")
        api_key = app.config.get("General", "api_key")
        str_cookie = f"API_apiKey={api_key}; BCR_username={username}"
        head = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": str_cookie,
        }

        req = UrlRequest(
            req_url, req_headers=head, on_success=callback, file_path=file_path
        )
        app = App.get_running_app()
        screen = app.manager.get_screen("server_readinglists_screen")
        if len(self.sync_list) != 0:
            screen.ids.sync_status_lbl.text = (
                f"Sync is Running Left in Que: {len(self.sync_list)}"
            )
            Clock.schedule_once(is_finished, 0.25)
        else:
            toast("Reading List has been Synced, Refreshing Screen")
            screen.ids.sync_status_lbl.text = ""
            screen.ids.sync_button.enabled = True
            app.sync_is_running = False
            screen.refresh_callback()

    def got_file(self, comic_obj, comic_file="", *args, **kwargs):
        self.num_file_done += 1
        toast(f"{comic_file} Synced")
        self.file_download = True
        db_comic = Comic.get(Comic.Id == comic_obj.Id)
        db_comic.is_sync = True
        db_comic.save()
        db_comic = Comic.get(Comic.Id == comic_obj.Id)
        db_comic.local_file = comic_file
        db_comic.been_sync = True
        db_comic.save()
        rl_db = ReadingList.get(ReadingList.slug == self.slug)
        rl_db.end_last_sync_num += 1
        rl_db.save()

    def download_file(self, dt):
        def got_thumb(results):
            pass

        app = App.get_running_app()
        screen = app.manager.get_screen("server_readinglists_screen")
        screen.ids.sync_button.enabled = False
        if len(self.sync_list) == 0:
            toast("Reading List has been Synced, Refreshing Screen")
            app = App.get_running_app()
            screen = app.manager.get_screen("server_readinglists_screen")
            screen.ids.sync_status_lbl.text = ""
            screen.ids.sync_button.enabled = True
            app.sync_is_running = False
            screen.refresh_callback()
            return
        comic = self.sync_list.pop(0)
        self.file_download = False
        file_name = ntpath.basename(comic.FilePath)
        y = 240
        part_url = f"/Comics/{comic.Id}/Pages/0?"
        app = App.get_running_app()
        part_api = f"&apiKey={app.api_key}&height={round(dp(y))}"
        thumb_url = f"{app.api_url}{part_url}{part_api}"

        if self.cb_optimize_size_active is False:
            sync_url = f"{app.api_url}/Comics/{comic.Id}/Sync/File/"
        elif self.cb_optimize_size_active is True:
            sync_url = f"{app.api_url}/Comics/{comic.Id}/Sync/Webp"
        print(f"sync_url:{sync_url}")
        app = App.get_running_app()
        id_folder = os.path.join(app.sync_folder, self.slug)
        self.my_comic_dir = Path(os.path.join(id_folder, "comics"))
        self.my_thumb_dir = Path(os.path.join(id_folder, "thumb"))
        if not self.my_comic_dir.is_dir():
            os.makedirs(self.my_comic_dir)
        if not self.my_thumb_dir.is_dir():
            os.makedirs(self.my_thumb_dir)
        t_file = os.path.join(self.my_comic_dir, file_name)
        self.get_server_file_download(
            sync_url,
            callback=self.got_file(comic, comic_file=t_file),
            file_path=t_file,
        )
        thumb_name = f"{comic.Id}.jpg"
        self.fetch_data.get_server_file_download(
            thumb_url,
            callback=lambda req, results: got_thumb(results),
            file_path=os.path.join(self.my_thumb_dir, thumb_name),
        )

    def _finish_sync(self, comic_list, *largs):
        def __finish_toast(dt):
            toast("Reading List has been Synced, Refreshing Screen")
            app = App.get_running_app()
            screen = app.manager.get_screen("server_readinglists_screen")
            screen.refresh_callback()

        list_comics = comic_list
        num_comic = len(list_comics)
        if self.num_file_done == num_comic:
            Clock.schedule_once(__finish_toast, 3)
            self.event.cancel()
            self.event = None

    def sync_readinglist(self, comic_list=[]):
        list_comics = comic_list
        app = App.get_running_app()
        self.sync_list = comic_list
        app = App.get_running_app()
        screen = app.manager.get_screen("server_readinglists_screen")
        screen.ids.sync_status_lbl.text = (
            f"Sync is Running Left in Que: {len(self.sync_list)}"
        )
        app.sync_is_running = True
        screen.ids.sync_button.enabled = False
        Clock.schedule_once(self.download_file)
        # app.delayed_work(
        #    self.download_file, list_comics, delay=.5)
        # self.event = Clock.schedule_interval(
        #     partial(self._finish_sync, comic_list), 0.5
        # )

