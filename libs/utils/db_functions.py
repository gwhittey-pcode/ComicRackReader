from peewee import SqliteDatabase, OperationalError, CharField, \
    IntegerField, ForeignKeyField, TextField, Model, ManyToManyField

from kivy.logger import Logger
db = SqliteDatabase('db/cr_comics_data.db')


def start_db():
    db.create_tables([
        ReadingList,
        Comic,
        ReadingList.comics.get_through_model()
    ])


class BaseModel(Model):
    class Meta:
        database = db


class Comic(BaseModel):
    comic_Id = CharField(unique=True)
    Number = CharField()
    Series = CharField()
    Year = IntegerField()
    Month = IntegerField()
    UserLastPageRead = IntegerField()
    UserCurrentPage = IntegerField()
    PageCount = IntegerField()
    Summary = TextField()
    FilePath = CharField()
    Volume = CharField()
    comic_file = CharField(null=True)
    comic_index = IntegerField(null=True)

    class Meta:
        database = db  # This model uses the "comics_data.db" database.


class ReadingList(BaseModel):
    name = CharField()
    slug = CharField(unique=True)
    comics = ManyToManyField(Comic, backref='comics')

    class Meta:
        database = db  # This model uses the "comics_data.db" database.


class SyncData(BaseModel):
    readinglist = ForeignKeyField(ReadingList)
