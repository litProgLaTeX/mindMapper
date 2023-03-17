# mapping the tangled mess that is in my mind

A tool to help mind map a wicked *web* of ideas....

We overlay [D3.js relationship tools](https://d3js.org/) on top of the
beautifully simple Python based wiki
[wiki2](https://pypi.org/project/wiki2/) as updated by
[tieugene/wiki](https://github.com/tieugene/wiki).

I attempted to overlay the mindMapper additions as essentially a
"sub-class" of the original Flask app. Making only the small changes
required to get mindMapper working. Unfortunately, I was unable to find a
clean way to "sub-class" Flask apps ("more's the pity"). So, since I am
taking the original code in a rather different direction, I decided to
simply copy the code and keep the previous license.

The original code for *this* project was taken from commit
`2938cf910847a43603f6615ff7486d95c8e939dd` of
[tieugene/wiki](https://github.com/tieugene/wiki) commited on 22/March/21.

-----

## About
As I wanted a wiki that just uses plain markdown files as backend, that is easy
to use and that is written in python, to enable me to easily hack around,
but found nothing, I just wrote this down. I hope that it might help others ,too.

## Features

* Markdown Syntax Editing
* Tags
* Regex Search
* Random URLs
* Web Editor
* Pages can also be edited manually, possible uses are:
	* use the cli
	* use your favorite editor
	* sync with dropbox
	* and many more

### Planned

* Re-introduce support for customizing the theme
* Speed Improvements
	* Code Optimizations
	* Caching
* Settings via the webinterface


## Setup
You can install wiki using:

	pip install wiki2


Afterwards you can create or change into your content directory and create a `config.py` file in it, that contains at least the following:

	# encoding: <your encoding (probably utf-8)
	SECRET_KEY='a unique and long key'
	TITLE='Wiki' # Title Optional

## Usage
Afterwards you can just run `wiki web` in your content directory to start the server.

## Development
If you plan on helping with the development of this project you can clone the repository, open the newly created directory in a terminal and run `pip install -e .`, after which both the tests and the wiki cli will be available to you.

## Contributors

Thank you very much to my two top contributers @walkerh and @traeblain. You two have posted so many issues and especially solved them with so many pull requests, that I sometimes lose track of it! :)
