import sublime
import sublime_plugin
import json
import sys
import inspect

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
        keyboard_shortcuts_and_commands = []
        key_bindings_list = self.get_key_bindings_list()

        for key_binding in key_bindings_list:
            entry = []
            entry.append(str(key_binding["keys"]))
            entry.append(str(key_binding["command"]))
            keyboard_shortcuts_and_commands.append(entry)

        self.generate_quick_panel(keyboard_shortcuts_and_commands)

    def get_key_bindings_list(self):
        package_list = get_packages_list()
        key_bindings_list = []
        
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

                    package_keymap_list = json.loads(minified_content)

                    for keymap in package_keymap_list: 
                        key_bindings_list.append(keymap)
        
        return key_bindings_list
            
    def get_keymap_files_from(self, package):
        file_list = list_package_files(package)
        platform_keymap_pattern = "default (%s).sublime-keymap" % (PLATFORM.lower())
        package_keymap_file_list = []
        for filename in file_list:
            if filename.lower().endswith("default.sublime-keymap")or \
            filename.lower().endswith(platform_keymap_pattern):
                package_keymap_file_list.append(filename)
        return package_keymap_file_list

    def generate_quick_panel(self, key_bindings_list):
        self.window.show_quick_panel(key_bindings_list, self.run_selected_command)

    def run_selected_command(self, selected_command_index):
        print "This doesn't quite work yet, but we're getting close!"