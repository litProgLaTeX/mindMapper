# -*- coding: utf-8 -*-
"""
    Wiki page
    ~~~~~~~~~
"""

import os

from collections import OrderedDict

from mindMapper.processor import Processor
from mindMapper.utils import InvalidFileException

class Page(object):
  def __init__(self, path, url, new=False):
    self.links = []
    self.content = None
    self.mapData = None
    self._html = None
    self.body = None
    self.path = path
    self.url = url
    self._meta = OrderedDict()
    if not new:
      self.load()
      self.render()

  def __repr__(self):
    return u"<Page: {}@{}>".format(self.url, self.path)

  def load(self):
    with open(self.path, 'r', encoding='utf-8') as f:
      self.content = f.read()
    mapDataPath = self.path.removesuffix('.md')+'.json'
    if os.path.exists(mapDataPath) :
      with open(mapDataPath) as mapDataFile :
        self.mapData = mapDataFile.read()

  def render(self):
    processor = Processor(self.content, self)
    try:
      self._html, self.body, self._meta = processor.process()
    except ValueError:
      raise InvalidFileException("No metadata & body.")

  def save(self, update=True):
    folder = os.path.dirname(self.path)
    if not os.path.exists(folder): os.makedirs(folder)
    with open(self.path, 'w', encoding='utf-8') as f:
      for key, value in self._meta.items():
        line = u'%s: %s\n' % (key, value)
        f.write(line)
      f.write(u'\n')
      f.write(self.body.replace(u'\r\n', u'\n'))
    if update:
      self.load()
      self.render()

  @property
  def meta(self):
    return self._meta

  def __getitem__(self, name):
    return self._meta[name]

  def __setitem__(self, name, value):
    self._meta[name] = value

  @property
  def html(self):
    return self._html

  def __html__(self):
    return self.html

  @property
  def title(self):
    try:
      return self['title']
    except KeyError:
      return self.url

  @title.setter
  def title(self, value):
    self['title'] = value

  @property
  def tags(self):
    try:
      return self['tags']
    except KeyError:
      return ""

  @tags.setter
  def tags(self, value):
    self['tags'] = value

  def addLink(self, aBaseUrl, aTitle, aModifier) :
    self.links.append({
      'source'   : self.url,
      'target'   : aBaseUrl,
      #'target'   : aBaseUrl.lower(),
      'title'    : aTitle,
      'modifier' : aModifier
    })
