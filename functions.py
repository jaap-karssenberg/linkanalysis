# -*- coding: utf-8 -*-

# Copyright 2017 Jaap Karssenberg <jaap.karssenberg@gmail.com>

from zim.notebook.index.links import LINK_DIR_FORWARD, LINK_DIR_BACKWARD, LINK_DIR_BOTH

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
