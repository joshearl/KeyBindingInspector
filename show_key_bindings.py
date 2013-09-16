import sublime
import sublime_plugin
import logging
import json
import sys
import inspect
import threading

VERSION = int(sublime.version())
ST2 = VERSION < 3000

logging.basicConfig(format='[KeyBindingInspector] %(levelname)s %(message)s')
logger = logging.getLogger()

if (ST2):
    from lib.package_resources import *
    from lib.strip_commas import strip_dangling_commas
    from lib.minify_json import json_minify
else:
    from KeyBindingInspector.lib.package_resources import *
    from KeyBindingInspector.lib.strip_commas import strip_dangling_commas
    from KeyBindingInspector.lib.minify_json import json_minify

reload_mods = ["lib.package_resources"]

for mod in reload_mods:

    logger.debug("Reloading module %s ..." % mod)
    reload(sys.modules[mod])

PLATFORM = sublime.platform().title()
if PLATFORM == "Osx":
    PLATFORM = "OSX"

class ShowKeyBindingsCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        sublime_plugin.WindowCommand.__init__(self, window)
        self.view = window.active_view()
        self.keyboard_shortcuts_and_commands = []
        self.plugin_settings = sublime.load_settings("KeyBindingInspector.sublime-settings")

    def run(self):
        self.debug = self.plugin_settings.get("debug", False)

        ignored_packages_list = sublime.load_settings(
            "Preferences.sublime-settings").get("ignored_packages", [])

        packages_path = sublime.packages_path()

        key_binding_extractor = KeyBindingExtractor(self.plugin_settings, packages_path, ignored_packages_list)
        key_binding_extractor.start()
        self.handle_key_binding_extraction(key_binding_extractor)

    def handle_key_binding_extraction(self, thread, i=0, direction=1):
        if thread.is_alive():
            self.debug_log("Thread is running ...")

            if (self.view):
                before = i % 8
                after = (7) - before
                if not after:
                    direction = -1
                if not before:
                    direction = 1
                i += direction
                
                self.view.set_status('key_binding_extractor', 'Extracting key bindings [%s=%s]' % \
                    (' ' * before, ' ' * after))

            sublime.set_timeout(lambda: self.handle_key_binding_extraction(thread, i, direction), 100)
            return

        self.debug_log("Thread finished.")

        if (self.view):
            self.view.erase_status('key_binding_extractor')

        key_bindings_list = thread.result
        self.display_key_bindings(key_bindings_list)

    def display_key_bindings(self, key_bindings_list):

        for key_binding in key_bindings_list:
            entry = []
            keys = key_binding["keys"]
            entry.append(", ".join(keys))
            entry.append(str(key_binding["command"]))
            if "args" in key_binding:
                entry.append(json.dumps(key_binding["args"]))
            self.keyboard_shortcuts_and_commands.append(entry)
        
        self.generate_quick_panel(self.keyboard_shortcuts_and_commands)        

    def generate_quick_panel(self, key_bindings_list):
        self.window.show_quick_panel(key_bindings_list, self.run_selected_command)

    def run_selected_command(self, selected_command_index):
        if (selected_command_index == -1):
            self.debug_log("No command selected.")
            return
        self.debug_log("Selected command: " + \
            str(self.keyboard_shortcuts_and_commands[selected_command_index]))

    def debug_log(self, message):
        if (self.debug):
            logger.debug(message)

class KeyBindingExtractor(threading.Thread):
    def __init__(self, settings, packages_path, ignored_packages_list):
        self.debug = settings.get("debug", False)
        self.packages_path = packages_path
        self.ignored_packages_list = ignored_packages_list
        self.result = None
        threading.Thread.__init__(self)

    def run(self):
        if (self.debug):
            logger.debug("Starting work on background thread ...")
        self.result = self.get_key_bindings_list()

    def get_key_bindings_list(self):
        package_list = get_packages_list(self.packages_path, self.ignored_packages_list)
        key_bindings_list = []
        
        for package in package_list:
            package_keymap_file_list = self.get_keymap_files_from(package)
            if (package_keymap_file_list):
                for keymap_file in package_keymap_file_list:
                    
                    package_keymap_list = self.get_package_keymap_list(package, keymap_file)

                    for keymap_file in package_keymap_list: 
                        key_bindings_list.append(keymap_file)
        
        return key_bindings_list

    def get_package_keymap_list(self, package, keymap_file):
        content = get_resource(package, keymap_file)
                    
        if content == None:
            return []

        minified_content = json_minify(content)
        minified_content = strip_dangling_commas(minified_content)
        minified_content = minified_content.replace("\n", "\\\n")

        package_keymap_list = json.loads(minified_content)

        return package_keymap_list

    def get_keymap_files_from(self, package):
        file_list = list_package_files(package)
        platform_keymap_pattern = "default (%s).sublime-keymap" % (PLATFORM.lower())
        package_keymap_file_list = []
        for filename in file_list:
            if filename.lower().endswith("default.sublime-keymap")or \
            filename.lower().endswith(platform_keymap_pattern):
                package_keymap_file_list.append(filename)
        return package_keymap_file_list