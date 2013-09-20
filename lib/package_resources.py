import sublime
import os
import re
import codecs
import zipfile

__all__ = [
    "get_packages_list",
    "list_package_files",
    "get_resource"
]

VERSION = int(sublime.version())
ST2 = VERSION < 3000

def get_packages_list(packages_path, ignored_packages_list):
    """
    Return a list of packages.
    """

    package_set = set()

    if (ST2):
        package_set.update(_get_packages_from_directory(packages_path))
    else: 
        package_set.update(_get_packages_from_directory(packages_path, ".sublime-package"))       

    for ignored in ignored_packages_list:
        package_set.discard(ignored)

    return sorted(list(package_set))

def _get_packages_from_directory(directory, file_ext=""):
    package_list = []
    for package in os.listdir(directory):
        if not package.endswith(file_ext):
            continue
        else:
            package = package.replace(file_ext, "")

        package_list.append(package)
    return package_list

def list_package_files(package, ignore_patterns=[]):
    """
    List files in the specified package.
    """

    package_path = os.path.join(sublime.packages_path(), package, "")
    path = None
    file_set = set()
    file_list = []
    if os.path.exists(package_path):
        for root, directories, filenames in os.walk(package_path):
            temp = root.replace(package_path, "")
            for filename in filenames:
                file_list.append(os.path.join(temp, filename))

    file_set.update(file_list)

    if ST2 is False:
        sublime_package = package + ".sublime-package"
        packages_path = sublime.installed_packages_path()

        if os.path.exists(os.path.join(packages_path, sublime_package)):
            file_set.update(_list_files_in_zip(packages_path, sublime_package))

        packages_path = os.path.dirname(sublime.executable_path()) + os.sep + "Packages"

        if os.path.exists(os.path.join(packages_path, sublime_package)):
            file_set.update(_list_files_in_zip(packages_path, sublime_package))

    file_list = []

    for filename in file_set:
        if not _ignore_file(filename, ignore_patterns):
            file_list.append(_normalize_to_sublime_path(filename))

    return sorted(file_list)

def _ignore_file(filename, ignore_patterns=[]):
    ignore = False
    directory, base = os.path.split(filename)
    for pattern in ignore_patterns:
        if re.match(pattern, base):
            return True

    if len(directory) > 0:
        ignore = _ignore_file(directory, ignore_patterns)

    return ignore

def _normalize_to_sublime_path(path):
    path = os.path.normpath(path)
    path = re.sub(r"^([a-zA-Z]):", "/\\1", path)
    path = re.sub(r"\\", "/", path)
    return path

def get_resource(package_name, resource, encoding="utf-8"):
    return _get_resource(package_name, resource, encoding=encoding)

def _get_resource(package_name, resource, return_binary=False, encoding="utf-8"):
    packages_path = sublime.packages_path()
    content = None
    if VERSION > 3013:
        try:
            if return_binary:
                content = sublime.load_binary_resource("Packages/" + package_name + "/" + resource)
            else:
                content = sublime.load_resource("Packages/" + package_name + "/" + resource)
        except IOError:
            pass
    else:
        path = None
        if os.path.exists(os.path.join(packages_path, package_name, resource)):
            path = os.path.join(packages_path, package_name, resource)
            content = _get_directory_item_content(path, return_binary, encoding)

        if VERSION >= 3006:
            sublime_package = package_name + ".sublime-package"

            packages_path = sublime.installed_packages_path()
            if content is None:
                if os.path.exists(os.path.join(packages_path, sublime_package)):
                    content = _get_zip_item_content(os.path.join(packages_path, sublime_package), resource, return_binary, encoding)

            packages_path = os.path.dirname(sublime.executable_path()) + os.sep + "Packages"

            if content is None:
                if os.path.exists(os.path.join(packages_path, sublime_package)):
                    content = _get_zip_item_content(os.path.join(packages_path, sublime_package), resource, return_binary, encoding)

    return content

def _get_directory_item_content(filename, return_binary, encoding):
    content = None
    if os.path.exists(filename):
        if return_binary:
            mode = "rb"
            encoding = None
        else:
            mode = "r"
        with codecs.open(filename, mode, encoding=encoding) as file_obj:
            content = file_obj.read()
    return content

def _list_files_in_zip(package_path, package):
    if not os.path.exists(os.path.join(package_path, package)):
        return []

    ret_value = []
    with zipfile.ZipFile(os.path.join(package_path, package)) as zip_file:
        ret_value = zip_file.namelist()
    return ret_value

def _get_zip_item_content(path_to_zip, resource, return_binary, encoding):
    if not os.path.exists(path_to_zip):
        return None

    ret_value = None

    with zipfile.ZipFile(path_to_zip) as zip_file:
        namelist = zip_file.namelist()
        if resource in namelist:
            ret_value = zip_file.read(resource)
            if not return_binary:
                ret_value = ret_value.decode(encoding)

    return ret_value