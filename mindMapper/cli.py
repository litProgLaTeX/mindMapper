# -*- coding: utf-8 -*-
"""CLI"""

import operator
import os
import sys

import click
from mindMapper.web import create_app

@click.group()
@click.option('--directory', type=click.Path(exists=True), default=None,
  help="the directory in which to run the wiki. [default: the current directory]."
)
@click.option("--config", type=click.Path(exists=True), default='../.mindMapper.toml',
  help="the configuration file for this project [default: '../.mindMapper.toml']"
)
@click.pass_context
def main(ctx, directory, config):
  """Base setup for all the following commands."""

  configPath = os.path.abspath(config)
  if not directory:
    directory = os.getcwd()
  dirPath = os.path.abspath(click.format_filename(directory))

  if configPath.startswith(dirPath) :
    print("The config file MUST NOT be located in the wiki directory!")
    print(f"    wiki path: {dirPath}")
    print(f"  config path: {configPath}")
    sys.exit(-1)
  
  ctx.meta['directory'] = dirPath
  ctx.meta['config']    = configPath

@main.command()
@click.option('--debug/--no-debug', envvar='WIKI_DEBUG', default=False,
  help="whether or not to run the web app in debug mode."
)
@click.option('--host', envvar='WIKI_HOST', default=None,
  help="Set the host to 0.0.0.0 to connect from outside. The default is 127.0.0.1."
)
@click.option('--port', envvar='WIKI_PORT', default=None, type=int,
  help="Set the listening port. The default is 5000."
)
@click.pass_context
def web(ctx, debug, host, port):
  """Run the web app."""

  app = create_app(ctx.meta['directory'], ctx.meta['config'])

  app.config['DEBUG'] = debug

  if 'SERVER_NAME' in app.config and app.config['SERVER_NAME'] :
    #print(f"using server name {app.config['SERVER_NAME']}")
    sHost, sPort = app.config['SERVER_NAME'].split(':')
    if sHost : app.config['HOST'] = sHost
    if sPort : app.config['PORT'] = sPort

  if host :
    #print(f"using command line host {host}")
    app.config['HOST'] = host
  if port :
    #print(f"using command line port {port}")
    app.config['PORT'] = port

  if 'HOST' not in app.config :
    #print(f"using default host")
    app.config['HOST'] = '127.0.0.1'
  if 'PORT' not in app.config :
    #print(f"using default port")
    app.config['PORT'] = 5000

  if debug :
    configStr = repr(app.config).removeprefix('<Config {').removesuffix('}>')
    configFields = list(map(str.strip, configStr.split(',')))
    configFields.sort()
    print("----------------------------------------------------------")
    print("app.config:")
    for aField in configFields :
      print(f"  {aField}")
    print("----------------------------------------------------------")
  app.run(debug=debug, host=app.config['HOST'], port=app.config['PORT'])
  print("RUNNING APP")

# adapted from https://dev.to/rhymes/flask-list-of-routes-4hph
@main.command()
@click.pass_context
def routes(ctx):
  'Display registered routes'

  app = create_app(ctx.meta['directory'], ctx.meta['config'])
  rules = []
  for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods))
    rules.append((rule.endpoint, methods, str(rule)))

  sort_by_rule = operator.itemgetter(2)
  for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
    route = '{:25s} {:25s} {}'.format(endpoint, methods, rule)
    print(route)
