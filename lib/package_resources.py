import sublime
import os
import re

__all__ = [
    "get_packages_list",
    "list_package_files"
]

def get_packages_list(ignore_packages=True):
    """
    Return a list of packages.
    """

    package_set = set()
    package_set.update(_get_packages_from_directory(sublime.packages_path()))

    if ignore_packages:
        ignored_package_list = sublime.load_settings(
            "Preferences.sublime-settings").get("ignored_packages", [])
        for ignored in ignored_package_list:
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