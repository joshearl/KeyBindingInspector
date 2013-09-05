import sublime
import os

def get_packages_list():
    """
    Return a list of packages.
    """
    package_set = set()
    package_set.update(_get_packages_from_directory(sublime.packages_path()))

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