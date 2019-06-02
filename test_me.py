#-*-coding:utf8;-*-

from kivy.app import App
from kivy.uix.treeview import TreeView, TreeViewLabel
from os import path, listdir


class MyTv(TreeView):
    
    def __init__(self, **kwargs):
        super(MyTv, self).__init__(**kwargs)
    
    
    def set_files(self, parent, fd_path):
        if path.isdir(fd_path):
            if parent is not None:
                # set icon for any folder
                # parent.set_icon('folder.png')
                pass
            for item in listdir(fd_path):
                print(item)
                sub_parent = self.add_node(TreeViewLabel(text=item), parent)
                sub_parent.path = path.join(fd_path, item)
            
                self.set_files(sub_parent, sub_parent.path)
        else:
            # check for type of icon to set for file
            # and later call set_icon() to set icon
            # parent.check_icon(fd_path)
            pass

root_project = "data"
root = MyTv()
root.set_files(None, root_project)

class TestApp(App):
    def build(self):
        return root 

TestApp().run()