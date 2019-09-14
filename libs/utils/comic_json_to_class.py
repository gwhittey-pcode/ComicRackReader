from pathlib import Path
import os
from kivy.storage.jsonstore import JsonStore
from kivy.properties import ListProperty, ObjectProperty, DictProperty,\
    StringProperty
from operator import attrgetter
from kivy.app import App
from kivy.clock import Clock


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


class ComicReadingList(object):

    # ids = DictProperty({})
    # name = StringProperty()
    def __init__(self, name='', data=None, slug=''):
        self.size = 65
        self.comics = []
        self.mynumber = 32
        self.name = name
        self.data = data
        self.slug = slug
        # self.next_page_url = data['next']
        # self.prev_page_url = data['previous']
        for item in self.data["items"][::-1]:
            new_comic = ComicBook(item)
            self.add_comic(new_comic)

    @property
    def reverse_comics_order(self):
        return reverse(self.comics)
        # return comic list in reverse for comicTopNav )

    @property
    def do_sort_series(self):
        return sorted(self.comics, key=attrgetter('series'))

    @property
    def do_sort_issue(self):
        return sorted(self.comics, key=attrgetter('series', 'issue'))
        # return sorted(comic.issue for comic in
        # sorted(comic.series for comic in self.comics) )

    @property
    def do_sort_pub_date(self):
        return sorted(self.comics, key=attrgetter('pubdate'))

    @property
    def do_sort_order_number(self):
        return sorted(self.comics, key=attrgetter('order_number'))

    def do_sort(self, sort_by):
        if sort_by == 'Issue':
            comic_collection_sorted = self.do_sort_issue
        elif sort_by == 'Pub Date':
            comic_collection_sorted = self.do_sort_pub_date
        elif sort_by == 'order_number':
            comic_collection_sorted = self.do_sort_order_number
        else:
            comic_collection_sorted = self.comics
        return comic_collection_sorted

    def add_comic(self, comic, index=0):
        '''
            Add Single comic book to this colection
        '''
        if index == 0 or len(self.comics) == 0:
            self.comics.insert(0, comic)
        else:
            comics = self.comics
            if index >= len(comics):
                index = len(comics)
            comics.insert(index, comic)

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

    def __init__(self, data, * args, **kwargs):

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
        my_data_dir = Path(os.path.join(app.store_dir, 'comics_db'))
        if not my_data_dir.is_dir():
            os.makedirs(my_data_dir)
        comic_db_json = os.path.join(my_data_dir, 'comics_db.json')
        self.comic_jsonstore = JsonStore(comic_db_json)

    def callback(self, store, key, result):
        print(result)

    def save(self, *args, **kwargs):
        lsit_store_keys = [
            'Id', 'slug', 'Series', 'Number', 'Year', 'Month',
            'UserCurrentPage', 'UserLastPageRead', 'PageCount',
            'Summary', 'Index', 'FilePath', 'ReadListID', 'local_file'
        ]
        put_value = f'{self.Id}'
        for key in lsit_store_keys:
            if key in kwargs:
                print(key)
        self.comic_jsonstore.async_put(
            self.Id, callback=self.callback,
            slug=self.slug,
            data_type='ComicBook',
            Series=self.Series,
            Number=self.Number,
            Month=self.month,
            Year=self.year,
            UserCurrentPage=self.UserCurrentPage,
            UserLastPageRead=self.UserLastPageRead,
            PageCount=self.PageCount,
            Summary=self.Summary,
            Index=0,
            FilePath=self.FilePath,
            ReadlistID=self.readlist_obj.slug,
            file=''
        )
