# -*- coding: utf-8 -*-

# Copyright 2017 Jaap Karssenberg <jaap.karssenberg@gmail.com>

import gtk

from zim.plugins import PluginClass, extends, WindowExtension
from zim.main import NotebookCommand, UsageError
from zim.actions import action
from zim.notebook import Path
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


def _source_target(dir):
	assert dir in (LINK_DIR_FORWARD, LINK_DIR_BACKWARD)
	if dir == LINK_DIR_FORWARD:
		return ('source', 'target')
	else:
		return ('target', 'source')


def sort_by_number_of_links(notebook, dir):
	source, target = _source_target(dir)
	return notebook.links.db.execute('''
		SELECT count({target}), pages.name FROM links
		JOIN pages ON links.{source}=pages.id
		GROUP BY {source}
		ORDER BY count({target}) DESC
	'''.format(source=source, target=target))


def compare_by_links(notebook, dir, page1=None):
	source, target = _source_target(dir)
	if page1 is None:
		# Select all pages that have any links, sorted by number of links
		for total, pageid, page1 in notebook.links.db.execute('''
			SELECT count({target}), {source}, pages.name FROM links
			JOIN pages ON links.{source}=pages.id
			GROUP BY {source}
			ORDER BY count({target}) DESC
		'''.format(source=source, target=target)
		):
			for match in _compare_by_links(notebook, dir, total, pageid, page1):
				yield match
	else:
		row1 = notebook.pages.lookup_by_pagename(page1)
		pageid = row1.id
		total, = notebook.links.db.execute(
			'SELECT count(*) FROM links WHERE {source}={page1}'.format(source=source, page1=pageid)
		).fetchone()
		for match in _compare_by_links(notebook, dir, total, pageid, page1.name):
			yield match


def _compare_by_links(notebook, dir, total, pageid, page1):
		source, target = _source_target(dir)

		# Now find all other pages that have a common link target
		# and group these by number of occurrences
		for match, page2 in notebook.links.db.execute('''
			SELECT count({source}), pages.name FROM (
				SELECT source, target FROM links
				WHERE {target} IN (
				    SELECT {target} FROM links WHERE {source} = {page1}
				) AND source <> target -- avoid self references
			) JOIN pages ON {source}=pages.id
			GROUP BY {source}
			ORDER BY count({source}) DESC
		'''.format(source=source, target=target, page1=pageid)
		):
			if page2 != page1:
				yield total, match, page1, page2


def find_common_links(notebook, page1, page2, dir):
	source, target = _source_target(dir)
	row1 = notebook.pages.lookup_by_pagename(page1)
	row2 = notebook.pages.lookup_by_pagename(page2)
	return notebook.links.db.execute('''
		SELECT DISTINCT pages.name FROM links
		JOIN pages ON {target}=pages.id
		WHERE {target} IN (
		    SELECT {target} FROM links WHERE {source} = {page1}
		) AND {target} IN (
			SELECT {target} FROM links WHERE {source} = {page2}
		) AND source <> target -- avoid self references
	'''.format(source=source, target=target, page1=row1.id, page2=row2.id))


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
		for i, page in sort_by_number_of_links(
			self.notebook, self.get_direction()
		):
			model.append((i, page))
