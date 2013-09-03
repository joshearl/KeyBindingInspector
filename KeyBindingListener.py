import sublime, sublime_plugin

class KeyBindingListener(sublime_plugin.EventListener):
    def on_window_command(self, window, name, args):
        print("The command name is: " + name)