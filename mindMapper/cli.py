# -*- coding: utf-8 -*-
"""CLI"""

import operator
import os
import signal
import sys
import time
import yaml

import click
from mindMapper.web import create_app, current_wiki

@click.group()
@click.option('--directory', type=click.Path(exists=True), default=None,
  help="the directory in which to run the wiki. [default: the current directory]."
)
@click.option("--config", type=click.Path(exists=True), default='../.mindMapper.toml',
  help="the configuration file for this project [default: '../.mindMapper.toml']"
)
@click.option('--host', envvar='WIKI_HOST', default=None,
  help="Set the host to 0.0.0.0 to connect from outside. The default is 127.0.0.1."
)
@click.option("--cache", type=click.Path(), default='../.mindMapper.cache',
  help="the cache file for this project [default: '../.mindMapper.cache']"
)
@click.option('--port', envvar='WIKI_PORT', default=None, type=int,
  help="Set the listening port. The default is 5000."
)
@click.pass_context
def main(ctx, directory, config, cache, host, port):
  """Base setup for all the following commands."""

  if not directory:
    directory = os.getcwd()
  dirPath = os.path.abspath(click.format_filename(directory))

  configPath = os.path.abspath(os.path.expanduser(config))
  if configPath.startswith(dirPath) :
    print("The config file MUST NOT be located in the wiki directory!")
    print(f"    wiki path: {dirPath}")
    print(f"  config path: {configPath}")
    sys.exit(-1)
  
  cachePath = os.path.abspath(os.path.expanduser(cache))
  if cachePath.startswith(dirPath) :
    print("The cache file MUST NOT be located in the wiki directory!")
    print(f"    wiki path: {dirPath}")
    print(f"   cache path: {cachePath}")
    sys.exit(-1)
  
  ctx.meta['directory']  = dirPath
  ctx.meta['configPath'] = configPath
  ctx.meta['cachePath']  = cachePath
  ctx.meta['host']       = host
  ctx.meta['port']       = port

@main.command()
@click.option('--debug/--no-debug', envvar='WIKI_DEBUG', default=False,
  help="whether or not to run the web app in debug mode."
)
@click.pass_context
def web(ctx, debug):
  """Run the web app."""

  app = create_app(ctx.meta)
  with app.app_context() :
    app.config['DEBUG'] = debug

    # report our configuration if in debug mode
    if debug :
      configStr = repr(app.config).removeprefix('<Config {').removesuffix('}>')
      configFields = list(map(str.strip, configStr.split(',')))
      configFields.sort()
      print("----------------------------------------------------------")
      print("app.config:")
      for aField in configFields :
        print(f"  {aField}")
      print("----------------------------------------------------------")

    # ensure the pages cache has been removed and rebuilt for the first time
    current_wiki.removePagesCache()
    current_wiki.rebuildPagesCache()

    # start the web server
    app.run(debug=debug, host=app.config['HOST'], port=app.config['PORT'])

    current_wiki.removePagesCache()

    print("")

# adapted from https://dev.to/rhymes/flask-list-of-routes-4hph
@main.command()
@click.pass_context
def routes(ctx):
  'Display registered routes'

  app = create_app(ctx.meta)
  rules = []
  for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods))
    rules.append((rule.endpoint, methods, str(rule)))

  sort_by_rule = operator.itemgetter(2)
  for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
    route = '{:25s} {:25s} {}'.format(endpoint, methods, rule)
    print(route)

@main.command()
@click.pass_context
def buildCache(ctx) :
  'Rebuild the pages cache'
  app = create_app(ctx.meta)
  with app.app_context() :
    wiki = current_wiki
    wiki.rebuildPagesCache()
    #pages = wiki.loadPagesCache()
    #print(yaml.dump(pages))