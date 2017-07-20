# -*- coding: utf-8 -*-

# Copyright 2017 Jaap Karssenberg <jaap.karssenberg@gmail.com>


from zim.plugins import PluginClass, extends, WindowExtension
from zim.main import NotebookCommand
from zim.actions import action
from zim.notebook.index.links import LINK_DIR_FORWARD, LINK_DIR_BACKWARD, LINK_DIR_BOTH


class LinkAnalysisPlugin(PluginClass):

	plugin_info = {
		'name': _('Link Analysis'), # T: plugin name
		'description': _('''\
This plugin provides functions to analyze the link structure of a notebook
'''), # T: plugin description
		'author': 'Jaap Karssenberg',
		'help': None,
	}

	plugin_preferences = (
		# key, type, label, default
		#('pane', 'choice', _('Position in the window'), RIGHT_PANE, PANE_POSITIONS),
			# T: option for plugin preferences
	)

	@classmethod
	def sort_by_number_of_links(cls, notebook, dir):
		return notebook.links.db.execute('''
			SELECT count(source), pages.name FROM links 
			JOIN pages ON links.target=pages.id
			GROUP BY target
			ORDER BY count(source) DESC
		''')


class LinkAnalysisCommand(NotebookCommand):

	arguments = ('COMMAND', 'NOTEBOOK', '[PAGE]')

	def build_notebook(self):
		# HACK around hardcoding of argument sequence
		self.arguments = ('NOTEBOOK', '[PAGE]')
		self.args = self.args[1:]
		return NotebookCommand.build_notebook(self)

	def run(self):
		command, n, p = self.get_arguments()
		notebook, p = self.build_notebook()
		if command == 'sort':
			list = LinkAnalysisPlugin.sort_by_number_of_links(notebook, LINK_DIR_BACKWARD)
		# TODO: "compare"
		# TODO: "network"
		else:
			raise UsageError, _('Unknown command: %s') % command

		for columns in list:
			print '\t'.join(map(unicode, columns))
