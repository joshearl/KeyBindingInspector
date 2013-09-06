import sublime
import sublime_plugin
import sys

from lib.package_resources import *

reload_mods = ["lib.package_resources"]

for mod in reload_mods:
    print "Reloading module %s ..." % mod
    reload(sys.modules[mod])

PLATFORM = sublime.platform().title()
if PLATFORM == "Osx":
    PLATFORM = "OSX"

class ShowKeyBindingsCommand(sublime_plugin.WindowCommand):
    def run(self):
        # window.run_command("show_key_bindings")
        packages = get_packages_list()
        for package in packages:
            file_list = list_package_files(package)
            platform_keymap = "default (%s).sublime-keymap" % (PLATFORM.lower())
            for filename in file_list:
                if filename.lower().endswith("default.sublime-keymap")or \
                filename.lower().endswith(platform_keymap):
                    print filename
        