# file goes to pyinstaller/hooks
# will be recognized by pyinstaller, no need for hidden modules

from PyInstaller.utils.hooks import (
    collect_data_files, 
    copy_metadata,
    collect_submodules
)
from kivy_deps import sdl2, glew

datas = copy_metadata('kivymd')
hiddenimports = collect_submodules('kivymd')

datas = collect_data_files('kivymd')