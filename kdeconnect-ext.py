import importlib
from subprocess import check_output, call
from gi.repository import GObject
from kdeconnect import send_files, get_available_devices
import zipfile
import urllib
import urllib.parse as urlparse
from urllib.request import url2pathname
from os import remove

TARGET = "%%TARGET%%".title()
Nautilus = importlib.import_module("gi.repository.{}".format(TARGET))


class KDEConnectExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        GObject.Object.__init__(self)

    def zipdir(self, path, ziph):
        # ziph is zipfile handle
        import os
        for root, dirs, files in os.walk(path):
            for file in files:
                #print("KDEConnectExtension: zipdir: dirs+[file]: "+str(dirs+[file]))
                ziph.write(os.path.join(root, file), os.path.join(*(dirs + [file])))

    def menu_activate_cb(self, menu, files, device_id, device_name, folder_list):
        import zipfile
        import os
        for folder_name in folder_list:
            zip_name = url2pathname(urlparse.urlparse(folder_name + '.zip').path)
            zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) # TODO: BUG/WARNING: Overwrites already existing files with the same name!!
            self.zipdir(zip_name[:-4] + '/', zipf)
            zipf.close()
            zipfile = Nautilus.FileInfo.create_for_uri(folder_name + '.zip')
            files.append(zipfile)

        send_files(files, device_id, device_name)

        # TODO: BUG: Leaves ZIP files behind. Can’t delete them, as kdeconnect hasn’t opened them yet.
        #            Maybe watch for the file to be opened, then run send_file(), then when the file user goes away, delete it.
        #            But asynchronously, to not block this thread.

    def get_file_items(self, window, files):
        try:
            devices = get_available_devices()
        except Exception as e:
            raise Exception(" KDEConnectExtension: get_file_items: Failed to get available devices")

        files_new = []
        folder_list = []
        for i in range(len(files)):
            if (files[i].is_directory() == False):
                files_new.append(files[i])
            else:
                folder_list.append(files[i].get_uri())

        files = files_new
        #print("KDEConnectExtension: get_file_items: files: "+str(files))
        #print("KDEConnectExtension: get_file_items: folder_list: "+str(folder_list))

        if (len(files_new) + len(folder_list) < 1):
            return []

        items = []
        for device in devices:
            item = Nautilus.MenuItem(
                name="KDEConnectExtension::Send_File",
                label="Send to %s" % device["name"]
            )
            item.connect('activate', self.menu_activate_cb,
                         files, device["id"], device["name"], folder_list)
            items.append(item)

        return items
