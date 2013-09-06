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

        keymap_contents = self.get_keymap_contents()


    def get_keymap_contents(self):
        package_list = get_packages_list()
        keymap_contents = []
        
        for package in package_list:
            package_keymap_list = self.get_keymaps_from(package)
            if (package_keymap_list):
                for keymap in package_keymap_list:
                    content = get_resource(package, keymap)
                    print "Key mappings for %s: " % package
                    print content

                keymap_contents.append(package_keymap_list)
        
        return keymap_contents
            
    def get_keymaps_from(self, package):
        file_list = list_package_files(package)
        platform_keymap_pattern = "default (%s).sublime-keymap" % (PLATFORM.lower())
        package_keymap_list = []
        for filename in file_list:
            if filename.lower().endswith("default.sublime-keymap")or \
            filename.lower().endswith(platform_keymap_pattern):
                package_keymap_list.append(filename)
        return package_keymap_list