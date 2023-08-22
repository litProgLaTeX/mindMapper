# -*- coding: utf-8 -*-
"""
    Wiki utils
    ~~~~~~~~~~
"""

import re

class InvalidFileException(Exception):
  """
  This exception is raised when wiki encounters a
  markdown file that it cannot handle.
  """
  pass

def clean_url(url):
  """
  Cleans the url and corrects various errors. Removes multiple
  spaces and all leading and trailing spaces. Changes spaces
  to underscores and makes all characters lowercase. Also
  takes care of Windows style folders use.

  :param str url: the url to clean

  :returns: the cleaned url
  :rtype: str
  """
  url = re.sub('[ ]{2,}', ' ', url).strip()
  url = url.replace(' ', '_')
  #url = url.lower().replace(' ', '_')
  url = url.replace('\\\\', '/').replace('\\', '/')
  return url
