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
    comic_index = IntegerField(null=True)

    class Meta:
        database = db  # This model uses the "comics_data.db" database.


class ReadingList(BaseModel):
    name = CharField()
    slug = CharField(primary_key=True)
    comics = ManyToManyField(Comic, backref='comics')

    class Meta:
        database = db  # This model uses the "comics_data.db" database.


class SyncData(BaseModel):
    readinglist = ForeignKeyField(ReadingList)
