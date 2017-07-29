# -*- coding: utf-8 -*-

# Copyright 2017 Jaap Karssenberg <jaap.karssenberg@gmail.com>

import gtk

from zim.gui.widgets import Dialog, SingleClickTreeView, ScrolledWindow, gtk_combobox_set_active_text

from .functions import *


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
