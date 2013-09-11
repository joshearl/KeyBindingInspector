import sublime
import os
import re
import codecs

__all__ = [
    "get_packages_list",
    "list_package_files",
    "get_resource"
]

def get_packages_list(packages_path, ignored_packages_list):
    """
    Return a list of packages.
    """

    package_set = set()
    package_set.update(_get_packages_from_directory(packages_path))

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

    path = None
    if os.path.exists(os.path.join(packages_path, package_name, resource)):
        path = os.path.join(packages_path, package_name, resource)
        content = _get_directory_item_content(path, return_binary, encoding)

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