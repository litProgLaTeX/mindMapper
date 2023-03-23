# -*- coding: utf-8 -*-
"""
    Wiki page processor
    ~~~~~~~~~~~~~~~~~~~
"""
import traceback

from collections import OrderedDict
import markdown
import re

from flask import url_for

from mindMapper.utils import clean_url

def wikilink(text, page, url_formatter=None):
  """
  Processes Wikilink syntax "[[Link]]" within the html body.
  This is intended to be run after content has been processed
  by markdown and is already HTML.

  :param str text: the html to highlight wiki links in.
  :param Page page: the page being processed.
  :param function url_formatter: which URL formatter to use,
         will by default use the flask url formatter

  Syntax:
    This accepts Wikilink syntax in the form of [[WikiLink]] or
    [[url/location|LinkName]]. Everything is referenced from the
    base location "/", therefore sub-pages need to use the
    [[page/subpage|Subpage]].

  :returns: the processed html
  :rtype: str
  """
  if url_formatter is None:
    url_formatter = url_for
  link_regex = re.compile(
    r"((?<!\<code\>)\[\[([^<].+?) \s*([|] \s* (.+?) \s*)?]])",
    re.X | re.U
  )
  for i in link_regex.findall(text):
    baseUrl = i[1]
    if 0 < baseUrl.find('{') :
      baseUrl, modifier = baseUrl.split('{')
    title = [i[-1] if i[-1] else i[1]][0]
    modifier = 'link'
    if 0 < title.find('{') : 
      title, modifier = title.split('{')
      modifier = modifier.removesuffix('}')
    url = clean_url(baseUrl)
    html_url = u"<a href='{0}' title='{1}'>{2}</a>".format(
      url_formatter('mindMapper.display', url=url),
      modifier,
      title
    )
    text = re.sub(link_regex, html_url, text, count=1)
    page.addLink(baseUrl, title, modifier)
  return text

class Processor(object):
  """
  The processor handles the processing of file content into
  metadata and markdown and takes care of the rendering.

  It also offers some helper methods that can be used for various
  cases.
  """

  preprocessors = []
  postprocessors = [wikilink]

  def __init__(self, text, page):
    """
    Initialization of the processor.

    :param str text: the text to process
    """
    self.md = markdown.Markdown(extensions=[
      'codehilite',
      'fenced_code',
      'meta',
      'tables',
      'mdx_math'  # mathjax support
    ])
    self.input = text
    self.page  = page
    self.markdown = None
    self.meta_raw = None

    self.pre = None
    self.html = None
    self.final = None
    self.meta = None

  def process_pre(self):
    """
    Content preprocessor.
    """
    current = self.input
    for processor in self.preprocessors:
      current = processor(current, self.page)
    self.pre = current

  def process_markdown(self):
    """
    Convert to HTML.
    """
    self.html = self.md.convert(self.pre)

  def split_raw(self):
    """
    Split text into raw meta and content.
    """
    self.meta_raw, self.markdown = self.pre.split('\n\n', 1)

  def process_meta(self):
    """
    Get metadata.

    .. warning:: Can only be called after :meth:`html` was
       called.
    """
    # the markdown meta plugin does not retain the order of the
    # entries, so we have to loop over the meta values a second
    # time to put them into a dictionary in the correct order
    self.meta = OrderedDict()
    if self.md.Meta:        # skip meta-less
      for line in self.meta_raw.split('\n'):
        key = line.split(':', 1)[0]
        # markdown metadata always returns a list of lines, we will
        # reverse that here
        self.meta[key.lower()] = \
          '\n'.join(self.md.Meta[key.lower()])

  def process_post(self):
    """
    Content postprocessor.
    """
    current = self.html
    for processor in self.postprocessors:
      current = processor(current, self.page)
    self.final = current

  def process(self):
    """
    Runs the full suite of processing on the given text, all
    pre and post processing, markdown rendering and meta data
    handling.
    """
    self.process_pre()
    self.process_markdown()
    self.split_raw()
    self.process_meta()
    self.process_post()

    return self.final, self.markdown, self.meta
