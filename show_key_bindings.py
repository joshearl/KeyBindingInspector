import sublime
import sublime_plugin

class ShowKeyBindingsCommand(sublime_plugin.WindowCommand):
	def run(self):
		# enter window.run_command("show_key_bindings") in console to execute
		print "You triggered the Show Key Bindings command!"