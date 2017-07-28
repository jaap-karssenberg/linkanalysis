# Link Analysis Plugin
Plugin for link structure analysis for the zim desktop wiki

## Commandline usage

Usage: `zim --plugin linkanalysis COMMAND NOTEBOOK [PAGE]`

Supported commands:
  - "`sort`" print out pages sorted by number of (back)links
  - "`compare`" print out pairs of pages that share one or more (back)links

Options:
  - `-d` `--direction`:  "`forward`" for normal links or "`backward`" for backlinks

**sort** prints two columns: that total number of (back)links and the page

**compare** prints four columns: the first is the total number of (back) links for
the first page, the second is the number of matches between the pages and the
third and fourth columns give the respective pages

## Concept
Based on an idea by Laecy -- <laesaleigh@gmail.com>

The use case in the request is about a notebook that contains pages for books or articles and uses links between pages to track references from one source to another. The goal is to analyze this body of references and find

  1. references that are most often refered and/or have the biggest influence
  2. sources that quote almost all of the same references

The first could be addressed by simply generating a list of pages ordered by number of back links. A more advanced version would also offer a tally of the number of backlinks of these referrers. Thus offering a kind of "influence" metric.

The second would be based on comparing the backlinks between any two pages and rank pairs of pages based on how big the overlap is between the referrers. Again this kind be done on the first order backlinks or over the total network over several steps.

Finally both cases could be analyzed for either backlinks, forward links, or both.

![Concept sketch of dialogs](./img/concept.png)


## Implementation
- [ ] Test cases
- [x] Sort pages by number of backlinks via commandline
- [x] Sort pages by number of backlinks via dialog
- [ ] Make listview in dialog robust for very large notebooks
- [x] Compare pages by number of backlinks via commandline
- [ ] Compare pages by number of via backlinks dialog
- [ ] Sort pages in "influence network" of a given starting page by degree and number of occurrences via commandline
- [ ] Sort pages in "influence network" of a given starting page by degree and number of occurrences via dialog
- [ ] Extend sort and compare with selection of links in "influence network"
- [ ] Add filter option to compare pages to a given starting page
- [ ] Add filter option to combine analysis view with regular search query
- [ ] Add command / dialog to report on matches between a pair of pages


## Installing this plugin
- Go to `~/.local/zim/plugins` (create folder if needed)
- Run `git clone https://github.com/jaap-karssenberg/linkanalysis.git`

TODO: link to resource with more verbose instructions, also covering windows

## Links
- [Zim Desktop Wiki website](http://zim-wiki.org/)
- [Zim Destkop Wiki on github](https://github.com/jaap-karssenberg/zim-desktop-wiki)
