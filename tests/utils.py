from io import open
import os
import shutil
from tempfile import mkdtemp
# from tempfile import mkstemp
from unittest import TestCase

import mindMapper.wiki
import mindMapper.web

#: the default configuration
CONFIGURATION = u"""
PRIVATE = false
TITLE = 'test'
DEFAULT_SEARCH_IGNORE_CASE = false
DEFAULT_AUTHENTICATION_METHOD = 'hash'
"""

class WikiBaseTestCase(TestCase):
    #: The contents of the ``config.py`` file.
    config_content = CONFIGURATION

    def setUp(self):
        """
            Creates a content directory for the wiki to use
            and adds a configuration file with some example content.
        """
        self._wiki = None
        self._app = None
        self.baseDir = mkdtemp()
        self.rootdir = os.path.abspath(os.path.join(self.baseDir, 'content'))
        self.configPath = os.path.abspath(os.path.join(self.baseDir, '.mindMapper.toml'))
        self.cachePath  = os.path.abspath(os.path.join(self.baseDir, '.mindMapper.cache'))
        os.mkdir(self.rootdir)
        self.create_file(u'../.mindMapper.toml', self.config_content)

    @property
    def wiki(self):
        if not self._wiki:
            self._wiki = mindMapper.wiki.Wiki(self.rootdir, self.configPath, self.cachePath)
        return self._wiki

    @property
    def app(self):
        if not self._app:
            ctxMeta = {
                'directory'  : self.rootdir,
                'configPath' : self.configPath,
                'cachePath'  : self.cachePath,
                'host'       : 'localhost.localdomain',
                'port'       : '5000'
            }
            self._app = mindMapper.web.create_app(ctxMeta).test_client()
        return self._app

    def create_file(self, name, content=u'', folder=None):
        """
            Easy way to create a file.

            :param unicode name: the name of the file to create
            :param unicode content: content of the file (optional)
            :param unicode folder: the folder where the file should be
                created, defaults to the temporary directory

            :returns: the absolute path of the newly created file
            :rtype: unicode
        """
        if folder is None:
            folder = self.rootdir

        path = os.path.join(folder, name)

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        with open(path, 'w', encoding='utf-8') as fhd:
            fhd.write(content)

        return path

    def tearDown(self):
        """
            Will remove the root directory and all contents if one
            exists.
        """
        if self.rootdir and os.path.exists(self.rootdir):
            shutil.rmtree(self.rootdir)
