from pathlib import Path

from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.storage.StorageNewABC import StorageABC
from cloudmesh.common.DEBUG import VERBOSE
import shutil

# import pwd  # does not work in windows
# from grp import getgrgid # does not work in windows
# from datetime import datetimef # does not work in windows

from cloudmesh.common.Shell import Shell
import os
import platform


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


class Provider(StorageABC):
    """

    cloudmesh:
      a:
        cm:
          active: False
          heading: Local A
          host: localhost
          label: local_a
          kind: local
          version: 1.0
        default:
          directory: .
        credentials:
          directory: ~/.cloudmesh/storage/a

    default location is credentials.directory / default.directory
    """

    def __init__(self, service=None, config="~/.cloudmesh/cloudmesh4.yaml"):
        super(Provider, self).__init__(service=service, config=config)

        self.credentials["directory"] = path_expand(self.credentials["directory"])

    def _filename(self, filename):
        return Path(self.credentials["directory"]) / filename

    def _dirname(self, dirname):
        if dirname == "/":
            dirname = ""
        location = Path(self.credentials["directory"]) / dirname
        return location

    def identifier(self, dirname, filename, status="ok"):
        stat_info = os.stat(filename)
        uid = stat_info.st_uid
        gid = stat_info.st_gid

        identity = {
            "cm":
                {"modified": "today",
                 "created": "today",
                 "location": str(Path(dirname) / filename),
                 "directory": dirname,
                 "filename": filename,
                 "isfile": os.path.isfile(filename),
                 "isdir": os.path.isdir(filename),
                 "name": os.path.basename(filename),
                 "kind": self.kind,
                 "size": "TBD",
                 "service": self.service
                 },
            "status": status,
            "size": os.path.getsize(filename),
            "name": filename,
            # "ownwer": pwd.getpwuid(uid)[0],
            # "group": pwd.getgrgid(gid)[0],
            "creation": datetime.fromtimestamp(creation_date(filename)).strftime("%m/%d/%Y, %H:%M:%S")

        }
        return identity

    def create_file(self, location, content):
        self.create_dir(location)
        writefile(location, content)

    def create_dir(self, directory=None):
        """
        creates a directory

        :param directory: the name of the directory
        :return: dict
        """

        d = self._dirname(directory)
        d.mkdir(parents=True, exist_ok=True)
        identity = self.identifier(directory, None)
        return identity

    def create_dir_from_filename(self, filename=None):
        """
        creates a directory

        :param directory: the name of the directory for the filename
        :return: dict
        """
        directory = os.path.dirname(filename)
        return self.create_dir(directory)

    def _list(self, source=None, recursive=False):
        """
        lists the information as dict

        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        return self._list(source=source, recursive=recursive)

    def _list(self, source=None, recursive=False, status="ok"):
        """
        lists the information as dict

        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        location = self._dirname(source)
        if recursive:
            files = location.glob("**/*")
        else:
            files = location.glob("*")
        result = []
        for file in files:
            entry = self.identifier(source, str(file), status=status)
            result.append(entry)
        return result

    def put(self, source=None, destination=None, recusrive=False):
        """
        puts the source on the service

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or
                            file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """

        source = self._dirname(source)
        if recusrive:
            src = path_expand(source)
            dest = path_expand(destination)
            shutil.copytree(src, dest)
        else:
            src = path_expand(source)
            dest = path_expand(destination)
            shutil.copy2(src, dest)

        return self.list(source=source, recusrive=recusrive)

    def get(self, source=None, destination=None, recusrive=False):
        """
        gets the source and copies it in destination

        :param source: the source which either can be a directory or file
        :param destination: the destination which either can be a directory or
                            file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        destination = self._dirname(source)
        if recusrive:
            src = path_expand(source)
            dest = path_expand(destination)
            shutil.copytree(src, dest)
        else:
            src = path_expand(source)
            dest = path_expand(destination)
            shutil.copy2(src, dest)

        return self.list(source=destination, recusrive=recusrive)

    def delete(self, source=None, recusrive=False):
        """
        deletes the source

        :param source: the source which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """
        raise NotImplementedError
        source = self._dirname(source)
        entries = self._list(source=source, recusrive=recusrive, ststus="deleted")
        shutil.rmtree(path_expand(source))
        return entries

    def search(self,
               directory=None,
               filename=None,
               recursive=False):
        """
        gets the destination and copies it in source

        :param service: the name of the service in the yaml file
        :param directory: the directory which either can be a directory or file
        :param recursive: in case of directory the recursive referes to all
                          subdirectories in the specified source
        :return: dict
        """

        VERBOSE(locals())
        files = self.list(source=directory, recursive=recursive)
        VERBOSE(files)
        result = []
        for entry in files:
            if entry["cm"]["name"] == filename:
                result.append(entry)
        return result

    def tree(self, directory=None):
        source = self._dirname(directory)
        r = Shell.execute(f"tree {source}")
        print(r)
