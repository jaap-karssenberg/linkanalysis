# -*- coding: utf-8 -*-

# Copyright 2017 Jaap Karssenberg <jaap.karssenberg@gmail.com>


from zim.plugins import PluginClass, extends, WindowExtension
from zim.main import NotebookCommand, UsageError
from zim.actions import action
from zim.notebook import Path

from .functions import *

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


class LinkAnalysisCommand(NotebookCommand):

	arguments = ('COMMAND', 'NOTEBOOK', '[PAGE1]', '[PAGE2]')

	options = (
		('direction=', 'd', 'Link direction'),
	)

	def build_notebook(self):
		# HACK around hardcoding of argument sequence
		self.arguments = ('NOTEBOOK',)
		self.args = (self.args[1],)
		return NotebookCommand.build_notebook(self)

	def run(self):
		args = self.get_arguments()
		command = args[0]
		notebook, p = self.build_notebook()

		if self.opts.get('direction', 'forw').lower().startswith('back'):
			dir = LINK_DIR_BACKWARD
		else:
			dir = LINK_DIR_FORWARD

		if command == 'sort':
			list = sort_by_number_of_links(notebook, dir)
		elif command == 'compare':
			if args[3] is not None:
				page1 = Path(Path.makeValidPageName(args[2]))
				page2 = Path(Path.makeValidPageName(args[3]))
				list = find_common_links(notebook, page1, page2, dir)
			elif args[2] is not None:
				page1 = Path(Path.makeValidPageName(args[2]))
				list = compare_by_links(notebook, dir, page1)
			else:
				list = compare_by_links(notebook, dir)
		else:
			raise UsageError, _('Unknown command: %s') % command

		for columns in list:
			print '\t'.join(map(unicode, columns))


@extends('MainWindow')
class MainWindowExtension(WindowExtension):

	uimanager_xml = '''
	<ui>
	<menubar name='menubar'>
		<menu action='view_menu'>
			<placeholder name='plugin_items'>
				<menuitem action='show_pages_by_number_of_links'/>
			</placeholder>
		</menu>
	</menubar>
	</ui>
	'''

	@action('Sort pages by number of links...')
	def show_pages_by_number_of_links(self):
		from .dialog import PagesByNumberOfLinksDialog
		PagesByNumberOfLinksDialog(self.window, self.window.notebook).run()
