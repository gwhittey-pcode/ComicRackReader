from pathlib import Path
import os
from kivy.storage.jsonstore import JsonStore
from kivy.properties import ListProperty, ObjectProperty, DictProperty,\
    StringProperty
from operator import attrgetter
from kivy.app import App
from kivy.clock import Clock
from libs.utils.db_functions import ReadingList, Comic
LSIT_STORE_KEYS = [
    'Id', 'slug', 'Series', 'Number', 'Volume', 'Year', 'Month',
    'UserCurrentPage', 'UserLastPageRead', 'PageCount',
    'Summary', 'comic_index', 'FilePath', 'local_file'
]


class ComicReadingList(object):

    # ids = DictProperty({})
    # name = StringProperty()
    def __init__(self, name='', data=None, slug='', mode='Server'):
        self.size = 65
        self.comics = []
        self.mynumber = 32
        self.name = name
        self.data = data
        self.slug = slug
        self.db = None
        self.comics_db = None
        self.comic_json = self.data["items"][::-1]
        if mode == 'Server':
            self.get_or_create_db_item()

    def get_or_create_db_item(self):
        db_item, created = ReadingList.get_or_create(
            slug=self.slug, defaults={'name': self.name})
        self.db = db_item

    def comics_write(self, comic):
        print('Start Comic write')
        comic.save()

        def __comics_write(comic):
            print(f'self.db.slug:{self.db.slug}')
            comic_db = Comic.get(Comic.Id == comic.Id)
            self.db.comics.add(comic_db)
            comic.save()

        app = App.get_running_app()
        # app.delayed_work(__comics_write, self.comics, delay=0)

    def add_comic(self, comic, index=0):
        '''
            Add Single comic book to this colection
        '''
        self.comics.insert(0, comic)

    def remove_comic(self, comic):
        '''
            Remove a comic from the comics of this collection.
        '''

        if comic not in self.comics:
            return
        self.comics.remove(comic)
        comic.collection = None

    def clear_comics(self, comics=None):
        '''
            Remove all Comics added to this Collection.
        '''

        if not comics:
            comics = self.comics
        remove_comic = self.remove_comic
        for comic in comics[:]:
            remove_comic(comic)

    def get_comic_by_number(self, comic_number):
        '''
            Will return the comic that matches id number x this number is
            ATM django-db server id number.
        '''
        for comic in self.comics:
            if comic.Id == comic_number:
                return comic


class ComicBook(object):
    cover = ObjectProperty()
    '''
    class representing a single comic
    '''

    def __init__(self, data, readlist_obj=None, comic_Id='',
                 comic_index=0, mode='Server', * args, **kwargs):
        if comic_Id == '':
            comic_data = data
            self.Id = comic_data['Id']
            self.__str__ = f"{comic_data['Series']} #{comic_data['Number']}"
            self.slug = str(comic_data['Id'])
            self.name = f"{comic_data['Series']} #{comic_data['Number']}"
            self.Number = comic_data['Number']
            self.Series = comic_data['Series']
            self.date = f"{comic_data['Month']}/{comic_data['Year']}"
            self.Year = comic_data['Year']
            self.Month = comic_data['Month']
            self.UserLastPageRead = comic_data['UserLastPageRead']
            self.UserCurrentPage = comic_data['UserCurrentPage']
            self.PageCount = comic_data['PageCount']
            self.Summary = comic_data['Summary']
            self.FilePath = comic_data['FilePath']
            self.Volume = comic_data['Volume']
            app = App.get_running_app()
            self.comic_jsonstore = app.comic_db
            self.readlist_obj = readlist_obj
            self.comic_index = comic_index
            self.local_file = ''
        # self.comic_jsonstore.put(self.Id, tesval='test')
        if mode == 'Server':
            Clock.schedule_once(lambda dt: self.get_or_create_db_item(), 0.5)

    def get_or_create_db_item(self):
        tmp_defaults = {}
        for key in LSIT_STORE_KEYS:
            tmp_defaults[key] = getattr(self, key)
        db_item, created = Comic.get_or_create(
            Id=self.Id, defaults=tmp_defaults)
        rl = self.readlist_obj
        if rl.slug not in [item.slug for item in db_item.readinglists]:
            rl.db.comics.add(db_item)

    def callback(self, store, key, result):
        pass

    def save(self, *args, **kwargs):
        self.get_or_create_db_item()
        self.comic_jsonstore.async_put(self.callback, self.Id, tesval='test')
        # lsit_store_keys = [
        #     'Id', 'slug', 'Series', 'Number', 'Year', 'Month',
        #     'UserCurrentPage', 'UserLastPageRead', 'PageCount',
        #     'Summary', 'Index', 'FilePath', 'ReadListID', 'local_file'
        # ]
        # put_value = f'{self.Id}'
        # for key in lsit_store_keys:
        #     if key in kwargs:
        #         print(key)
        # self.comic_jsonstore.async_put(self.callback,
        #                                self.Id,
        #                                slug=self.slug,
        #                                data_type='ComicBook',
        #                                Series=self.Series,
        #                                Number=self.Number,
        #                                Month=self.Month,
        #                                Year=self.Year,
        #                                UserCurrentPage=self.UserCurrentPage,
        #                                UserLastPageRead=self.UserLastPageRead,
        #                                PageCount=self.PageCount,
        #                                Summary=self.Summary,
        #                                Index=0,
        #                                FilePath=self.FilePath,
        #                                ReadlistID=self.readlist_obj.slug,
        #                                file=''
        #                                )
