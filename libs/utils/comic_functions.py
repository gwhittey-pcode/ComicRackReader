import os
from datetime import datetime
from libs.utils.comicapi.comicarchive import MetaDataStyle, ComicArchive
from kivy.logger import Logger
from kivy.app import App
from pathlib import Path
from PIL import Image
from libs.utils.comic_server_conn import ComicServerConn
from kivy.utils import platform
from kivy.core.image import Image as CoreImage
# from kivy.core.image import Image as CoreImage
# from kivy.uix.image import Image as kvImage
# from PIL import Image, ImageDraw, ImageFont


def convert_comicapi_to_json(comic_path):
    """ returns comic format to pass to json_obj"""
    if os.path.exists(comic_path):
        Logger.info(f"Reading in {comic_path}")
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
            "Volume": md.volume,
        }
        return data
    else:
        Logger.error(f"{comic_path} is not valid")


def get_comic_page(comic_obj, page_num):
    """returns name of cache file of requested page """
    app = App.get_running_app()
    cahce_dir = os.path.join(app.store_dir, "cache")
    if comic_obj.is_sync:
        comic_name = comic_obj.Id
    else:
        comic_name = "{}_{}_{}".format(
            comic_obj.Series, comic_obj.Number, comic_obj.Volume
        )

    comic_dir = os.path.join(cahce_dir, comic_name)
    if not Path(comic_dir).is_dir():
        os.makedirs(comic_dir)
    if comic_obj.is_sync:
        md = getComicMetadata(comic_obj.local_file)
    else:
        md = getComicMetadata(comic_obj.FilePath)
    ca = ComicArchive(md.path)
    image_data = ca.getPage(int(page_num))
    filename = os.path.join(comic_dir, f"{page_num}.webp")
    with open(filename, "wb") as outfile:
        outfile.write(image_data)
    return filename


def get_file_page_size(file):
    im = CoreImage(file)
    width, height = im.size
    return width, height
    # if (platform != 'android'):
    #     im = Image.open(file)
    #     width, height = im.size
    #     return width, height
    # else:


def getComicMetadata(path):
    """Returns comicarchinve info from comicapi """
    # TODO: Need to fix the default image path
    ca = ComicArchive(path)
    if ca.seemsToBeAComicArchive():
        if ca.hasMetadata(MetaDataStyle.CIX):
            style = MetaDataStyle.CIX
        else:
            style = None

        if style is not None:
            md = ca.readMetadata(style)
            md.path = ca.path
            md.page_count = ca.page_count
            md.mod_ts = datetime.utcfromtimestamp(os.path.getmtime(ca.path))
            return md
    return None


async def save_thumb(comic_id, c_image_source):
    def got_thumb(results):
        pass

    fetch_data = ComicServerConn()
    app = App.get_running_app()
    id_folder = app.store_dir
    my_thumb_dir = Path(os.path.join(id_folder, "comic_thumbs"))

    if not my_thumb_dir.is_dir():
        os.makedirs(my_thumb_dir)
    file_name = f"{comic_id}.jpg"
    t_file = os.path.join(my_thumb_dir, file_name)
    fetch_data.get_server_file_download(
        c_image_source,
        callback=lambda req, results: got_thumb(results),
        file_path=os.path.join(my_thumb_dir, t_file),
    )
