# -*- coding: utf-8 -*-
"""
    Wiki
    ~~~~
"""

import json
import os
import pickle
from tempfile import NamedTemporaryFile
import tomllib

from flask import abort

from mindMapper.utils import clean_url
from mindMapper.utils import InvalidFileException
from mindMapper.page  import Page

class Wiki(object):
  def __init__(self, root, configPath, cachePath):
    self.root          = os.path.abspath(root)
    self.configPath    = os.path.abspath(configPath)
    self.rebuildMarker = os.path.abspath(os.path.join(self.root, '.rebuild'))
    self.pagesCache    = os.path.abspath(cachePath)

    with open(configPath, "rb") as tomlFile :
      tomlData = tomllib.load(tomlFile)
      self.nodeMapping = {}
      if 'nodeMapping' in tomlData : self.nodeMapping = tomlData['nodeMapping']
      self.nodeMapping['default'] = {'color' : 'black' }
      self.linkMapping = {}
      if 'linkMapping' in tomlData : self.linkMapping = tomlData['linkMapping']
      self.linkMapping['default'] = {'color' : 'black' }

  def path(self, url):
    return os.path.join(self.root, url + '.md')

  def exists(self, url):
    path = self.path(url)
    return os.path.exists(path)

  def get(self, url):
    path = os.path.join(self.root, url + '.md')
    if self.exists(url):
      return Page(path, url)
    return None

  def get_or_404(self, url):
    page = self.get(url)
    if page:
      return page
    abort(404)

  def get_bare(self, url):
    path = self.path(url)
    if self.exists(url):
      return False
    return Page(path, url, new=True)

  def move(self, url, newurl):
    newurl = clean_url(newurl)
    source = os.path.join(self.root, url) + '.md'
    target = os.path.join(self.root, newurl) + '.md'
    # normalize root path (just in case somebody defined it absolute,
    # having some '../' inside) to correctly compare it to the target
    root = os.path.normpath(self.root)
    # get root path longest common prefix with normalized target path
    common = os.path.commonprefix((root, os.path.normpath(target)))
    # common prefix length must be at least as root length is
    # otherwise there are probably some '..' links in target path leading
    # us outside defined root directory
    if len(common) < len(root):
      raise RuntimeError(
        'Possible write attempt outside content directory: '
        '%s' % newurl)
    # create folder if it does not exist yet
    folder = os.path.dirname(target)
    if not os.path.exists(folder):
      os.makedirs(folder)
    os.rename(source, target)
    return newurl

  def delete(self, url):
    path = self.path(url)
    if not self.exists(url):
      return False
    os.remove(path)
    return True

  def index(self):
    """
    Builds up a list of all the available pages.

    :returns: a list of all the wiki pages
    :rtype: list
    """
    pages = self.loadPagesCache()
    return sorted(pages, key=lambda x: x.title.lower())

  def index_by(self, key):
    """
    Get an index based on the given key.

    Will use the metadata value of the given key to group
    the existing pages.

    :param str key: the attribute to group the index on.

    :returns: Will return a dictionary where each entry holds
              a list of pages that share the given attribute.
    :rtype: dict
    """
    pages = {}
    for page in self.index():
      value = getattr(page, key)
      pre = pages.get(value, [])
      pages[value] = pre.append(page)
    return pages

  #def get_by_title(self, title):
  #  pages = self.index(attr='title')
  #  return pages.get(title)

  def get_tags(self):
    pages = self.index()
    tags = {}
    for page in pages:
      pagetags = page.tags.split(',')
      for tag in pagetags:
        tag = tag.strip()
        if tag == '':
          continue
        elif tags.get(tag):
          tags[tag].append(page)
        else:
          tags[tag] = [page]
    return tags

  def index_by_tag(self, tag):
    pages = self.index()
    tagged = []
    for page in pages:
      if tag in page.tags:
        tagged.append(page)
    return sorted(tagged, key=lambda x: x.title.lower())

  def search(self, term, ignore_case=True, attrs=('title', 'tags', 'body')):
    pages = self.index()
    regex = re.compile(term, re.IGNORECASE if ignore_case else 0)
    matched = []
    for page in pages:
      for attr in attrs:
        if regex.search(getattr(page, attr)):
          matched.append(page)
          break
    return matched

  def removePagesCache(self) :
    if os.path.exists(self.pagesCache) : os.remove(self.pagesCache)

  def loadPagesCache(self) :
    pages = []
    if os.path.exists(self.pagesCache) :
      with open(self.pagesCache, 'rb') as pickelFile :
        pages = pickle.load(pickelFile)
        print(" * Loaded pages cache")
    return pages

  def rebuildPagesCache(self) :
    print(" * Rebuilding pages cache")

    # start by loading all of the pages
    #
    pages = []
    pagesMap = {}
    root = os.path.abspath(self.root)
    for cur_dir, _, files in os.walk(root):
      # get the url of the current directory
      cur_dir_url = cur_dir[len(root) + 1:]
      for cur_file in files:
        path = os.path.join(cur_dir, cur_file)
        if cur_file.endswith('.md'):
          url = clean_url(os.path.join(cur_dir_url, cur_file[:-3]))
          try:
            page = Page(path, url)
            pages.append(page)
            pagesMap[page.url] = page
          except InvalidFileException:
            # for now we just ignore files that are invalid
            # entirely
            pass
    #
    # now build the link maps
    #
    maps = {}
    for aPage in pages :
      for aLink in aPage.links :
        sourcePage = pagesMap[aLink['source']]
        if aLink['target'] not in pagesMap :
          print(f" * BROKEN LINK: {aLink['source']} -> {aLink['target']}")
          continue
        targetPage = pagesMap[aLink['target']]
        modifier   = aLink['modifier']
      
        pageTags = {}
        for aTag in sourcePage.tags.split(',') : pageTags[aTag.strip()] = True
        for aTag in targetPage.tags.split(',') : pageTags[aTag.strip()] = True
        pageTags['theVortex'] = True
        for aTag in pageTags :
          if aTag not in maps : maps[aTag] = {
            'nodes' : {},
            'links' : {}
          }
          tagMap = maps[aTag]
          tagMap['nodes'][sourcePage.url] = True
          tagMap['nodes'][targetPage.url] = True
          if sourcePage.url not in tagMap['links'] :
            tagMap['links'][sourcePage.url] = {}
          srcMap = tagMap['links'][sourcePage.url]
          if targetPage.url not in srcMap :
            srcMap[targetPage.url] = {}
          srcMap[targetPage.url][modifier] = True
    #
    # now save the pages cache
    #
    tmpName = None
    try :
      with NamedTemporaryFile(
        dir=os.path.abspath(self.root), delete=False
      ) as tmpFile :
        tmpName = tmpFile.name
        pickle.dump(pages, tmpFile)
      os.replace(tmpName, self.pagesCache)
      print(f" * Saved pagesCache to {self.pagesCache}")
    finally :
      try : os.remove(tmpName)
      except (TypeError, OSError) :
        pass
    #
    # now write out each link map
    #
    for aTag, aMap in maps.items() :
      theMap = { 'nodes' : [], 'links' : []}
      links  = theMap['links']
      nodes  = theMap['nodes']
      for aNode in aMap['nodes'] :
        aNode = {
          'id'       : pagesMap[aNode].url,
          'path'     : pagesMap[aNode].url,
          'nodeType' : 'default'
        }
        for aKey, aValue in self.nodeMapping['default'].items() :
          aNode[aKey] = aValue
        nodes.append(aNode)
      for aSource in aMap['links'] :
        for aTarget in aMap['links'][aSource] :
          for aModifier in aMap['links'][aSource][aTarget] :
            aLink = {
              'source'   : pagesMap[aSource].url,
              'target'   : pagesMap[aTarget].url,
              'linkType' : aModifier
            }
            linkModifier = aModifier
            if linkModifier not in self.linkMapping : 
              linkModifier = 'default'
            for aKey, aValue in self.linkMapping[linkModifier].items() :
              aLink[aKey] = aValue
            links.append(aLink)
      tagFileName = None
      try :
        with NamedTemporaryFile(
          dir=os.path.abspath(self.root), delete=False  
        ) as tagFile :
          tagFileName = tagFile.name
          #jsonStr = json.dumps(theMap, indent=2)
          jsonStr = json.dumps(theMap)
          tagFile.write(jsonStr.encode())
          tagFile.write(b"\n")
        os.replace(tagFileName, os.path.abspath(os.path.join(self.root, f"{aTag}.json")))
      finally :
        try : os.remove(tagFileName)
        except (TypeError, OSError) :
          pass
