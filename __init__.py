# -*- coding: utf-8 -*-

# Copyright 2017 Jaap Karssenberg <jaap.karssenberg@gmail.com>

import gtk

from zim.plugins import PluginClass, extends, WindowExtension
from zim.main import NotebookCommand
from zim.actions import action
from zim.notebook.index.links import LINK_DIR_FORWARD, LINK_DIR_BACKWARD, LINK_DIR_BOTH
from zim.gui.widgets import Dialog, SingleClickTreeView, ScrolledWindow, gtk_combobox_set_active_text


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
		if dir == LINK_DIR_FORWARD:
			return notebook.links.db.execute('''
				SELECT count(target), pages.name FROM links
				JOIN pages ON links.source=pages.id
				GROUP BY source
				ORDER BY count(target) DESC
			''')
		elif dir == LINK_DIR_BACKWARD:
			return notebook.links.db.execute('''
				SELECT count(source), pages.name FROM links
				JOIN pages ON links.target=pages.id
				GROUP BY target
				ORDER BY count(source) DESC
			''')
		else:
			raise NotImplementedError


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
		PagesByNumberOfLinksDialog(self.window, self.window.notebook).run()


class PagesByNumberOfLinksDialog(Dialog):

	LABELS = {
		LINK_DIR_FORWARD: _('Forward'),
		LINK_DIR_BACKWARD: _('Backward'),
		#LINK_DIR_BOTH: _('Both'),
	}

	def __init__(self, parent, notebook):
		Dialog.__init__(self, parent,
			_('Pages By Number Of Links'), # T: dialog title
			buttons=gtk.BUTTONS_CLOSE
		)
		self.notebook = notebook

		self.direction_input = gtk.combo_box_new_text()
		for dir in sorted(self.LABELS):
			self.direction_input.append_text(self.LABELS[dir])

		self.uistate.setdefault('link_direction', LINK_DIR_BACKWARD, self.LABELS.keys())
		gtk_combobox_set_active_text(
			self.direction_input,
			self.LABELS[self.uistate['link_direction']]
		)
		self.direction_input.connect('changed', self.on_direction_input_changed)

		hbox = gtk.HBox()
		hbox.pack_start(gtk.Label(_('Trace Links')+':'), False)
		hbox.add(self.direction_input)
		self.vbox.pack_start(hbox, False)

		self.listview = SingleClickTreeView(gtk.ListStore(int, str))
		self.listview.set_reorderable(True)
		for i, label in enumerate((_('#'), _('Page'))):
			column = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=i)
			column.set_sort_column_id(i)
			self.listview.append_column(column)
		# TODO: self.listview.connect('row-activated', self.on_row_activated())

		self.vbox.add(ScrolledWindow(self.listview))
		self.populate_listview()

	def get_direction(self):
		label = self.direction_input.get_active_text()
		for k, v in self.LABELS.items():
			if v == label:
				return k
		else:
			raise ValueError

	def on_direction_input_changed(self, *a):
		self.uistate['link_direction'] = self.get_direction()
		self.populate_listview()

	def populate_listview(self):
		model = self.listview.get_model()
		model.clear()
		for i, page in LinkAnalysisPlugin.sort_by_number_of_links(
			self.notebook, self.get_direction()
		):
			model.append((i, page))
