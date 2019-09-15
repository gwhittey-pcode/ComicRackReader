from peewee import SqliteDatabase, OperationalError, CharField, \
    IntegerField, ForeignKeyField, TextField, Model, ManyToManyField, BooleanField, \
    DeferredThroughModel

from kivy.logger import Logger
db = SqliteDatabase('db/cr_comics_data.db')


def start_db():
    db.create_tables([
        ReadingList,
        Comic,
        ComicIndex,
        ReadingList.comics.get_through_model(),

    ])


class BaseModel(Model):
    class Meta:
        database = db


class Comic(BaseModel):
    Id = CharField(primary_key=True)
    Number = CharField()
    Series = CharField(null=True)
    Year = IntegerField(null=True)
    Month = IntegerField(null=True)
    UserLastPageRead = IntegerField()
    UserCurrentPage = IntegerField()
    PageCount = IntegerField()
    Summary = TextField(null=True)
    FilePath = CharField(null=True)
    Volume = CharField(null=True)
    comic_file = CharField(null=True)
    #comic_index = IntegerField(null=True)
    local_file = CharField(null=True)

    class Meta:
        database = db  # This model uses the "comics_data.db" database.


ComicIndexDeferred = DeferredThroughModel()
#     cb_limit_state = CharField()
#     limit_num = IntegerField()
#     cb_only_read_state = CharField()
#     cb_keep_last_read_state = CharField()
#     cb_optimize_size_state = CharField()
#     sw_syn_this_active = CharField()


class ReadingList(BaseModel):
    name = CharField()
    slug = CharField(primary_key=True)
    comics = ManyToManyField(
        Comic, backref='readinglists', through_model=ComicIndexDeferred)
    cb_limit_state = CharField(null=True)
    limit_num = IntegerField(null=True)
    cb_only_read_state = CharField(null=True)
    cb_keep_last_read_state = CharField(null=True)
    cb_optimize_size_state = CharField(null=True)
    sw_syn_this_active = BooleanField(null=True)

    class Meta:
        database = db  # This model uses the "comics_data.db" database.


class ComicIndex(BaseModel):
    comic = ForeignKeyField(Comic, backref='comic_index')
    readinglist = ForeignKeyField(ReadingList, backref='Indexes')
    index = IntegerField()
    is_sync = BooleanField(default=False)


ComicIndexDeferred.set_model(ComicIndex)


class SyncData(BaseModel):
    readinglist = ForeignKeyField(ReadingList)
