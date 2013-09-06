import sublime
import sublime_plugin
import json
import sys

from lib.package_resources import *
from lib.strip_commas import strip_dangling_commas
from lib.minify_json import json_minify

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
        keymap_list = self.get_keymap_list()
        print keymap_list

    def get_keymap_list(self):
        package_list = get_packages_list()
        keymap_list = []
        
        for package in package_list:
            package_keymap_file_list = self.get_keymap_files_from(package)
            if (package_keymap_file_list):
                for keymap in package_keymap_file_list:
                    content = get_resource(package, keymap)
                    
                    if content == None:
                        continue

                    minified_content = json_minify(content)
                    minified_content = strip_dangling_commas(minified_content)
                    minified_content = minified_content.replace("\n", "\\\n")

                    keymap = json.loads(minified_content)
                    keymap_list.append(keymap)
        
        return keymap_list
            
    def get_keymap_files_from(self, package):
        file_list = list_package_files(package)
        platform_keymap_pattern = "default (%s).sublime-keymap" % (PLATFORM.lower())
        package_keymap_file_list = []
        for filename in file_list:
            if filename.lower().endswith("default.sublime-keymap")or \
            filename.lower().endswith(platform_keymap_pattern):
                package_keymap_file_list.append(filename)
        return package_keymap_file_list