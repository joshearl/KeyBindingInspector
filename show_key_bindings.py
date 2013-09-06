import sublime
import sublime_plugin

from lib.package_resources import *

class ShowKeyBindingsCommand(sublime_plugin.WindowCommand):
    def run(self):
        # window.run_command("show_key_bindings")
        packages = get_packages_list()
        print packages
        for package in packages:
            file_list = list_package_files(package)
            print file_list
        