from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as kvImage
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta, date
from libs.utils.comicapi.comicarchive import MetaDataStyle, ComicArchive
from libs.utils.comicapi.issuestring import IssueString
from libs.utils.comicapi.comicarchive import ComicArchive
from io import BytesIO
from kivy.logger import Logger
import json
from kivy.app import App
from pathlib import Path
from PIL import Image


def convert_comicapi_to_json(comic_path):
    print(comic_path)
    """ returns comic format to pass to json_obj"""
    if os.path.exists(comic_path):
        md = getComicMetadata(comic_path)

        data = {
            "Id": f"{md.series}_{md.issue}_{md.volume}",
            "Series": md.series,
            "Number": md.issue,
            "Month": md.month,
            "Year": md.year,
            "UserLastPageRead": 0,
            "UserCurrentPage": 0,
            "PageCount": int(md.pageCount),
            "Summary": md.comments,
            "FilePath": comic_path,
            'Volume': md.volume
        }
        return data
    else:
        Logger.error(f'{comic_path} is not valid')


def get_comic_page(comic_obj, page_num):
    """returns name of cache file of requested page """
    app = App.get_running_app()
    cahce_dir = app.cache_dir
    comic_name = f'{comic_obj.Series}_{comic_obj.Number}_{comic_obj.Volume}'
    comic_dir = os.path.join(cahce_dir, comic_name)
    if not Path(comic_dir).is_dir():
        os.makedirs(comic_dir)
    md = getComicMetadata(comic_obj.file_path)
    ca = ComicArchive(md.path)
    image_data = ca.getPage(int(page_num))
    filename = os.path.join(comic_dir, f'{page_num}.webp')
    with open(filename, "wb") as outfile:
        outfile.write(image_data)
    return filename


def get_file_page_size(file):
    im = Image.open(file)
    width, height = im.size
    return width, height


def getComicMetadata(path):
    """Returns comicarchinve info from comicapi """
    # TODO: Need to fix the default image path
    ca = ComicArchive(path, default_image_path=None)
    if ca.seemsToBeAComicArchive():
        Logger.info(f"Reading in {path}")
        if ca.hasMetadata(MetaDataStyle.CIX):
            style = MetaDataStyle.CIX
        else:
            style = None

        if style is not None:
            md = ca.readMetadata(style)
            md.path = ca.path
            md.page_count = ca.page_count
            md.mod_ts = datetime.utcfromtimestamp(
                os.path.getmtime(ca.path))
            return md
    return None