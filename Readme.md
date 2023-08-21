# mapping the tangled mess that is in my mind

A tool to help mind map a wicked *web* of ideas....

We overlay [D3.js relationship tools](https://d3js.org/) on top of the
beautifully simple Python based wiki
[wiki2](https://pypi.org/project/wiki2/) as updated by
[tieugene/wiki](https://github.com/tieugene/wiki).

## Usage

To run the mindMapping tool (in your local browser and with all of the
defaults) `cd` into the directory which contains your notes and then type:

```
  mindMapper web
```

Then "open the link" provided by your (python waitress) Waitress.

Since this tool is meant to be run locally on `localhost` we have
*disabled* the login. However, at the moment the login page still appears,
so simply humour the system by providing any userid and password you like.

To stop the server, type: `Ctrl-C`

While you can create, move and edit pages directly in the web based
interface, you can also edit any files you like in your "notes" directory.

For other options you can type:

```
  mindMapper --help
```

## Some history...

I attempted to overlay the mindMapper additions as essentially a
"sub-class" of the original Flask app. Making only the small changes
required to get mindMapper working. Unfortunately, I was unable to find a
clean way to "sub-class" Flask apps ("more's the pity"). So, since I am
taking the original code in a rather different direction, I decided to
simply copy the code and keep the previous license.

The original code for *this* project was taken from commit
`2938cf910847a43603f6615ff7486d95c8e939dd` of
[tieugene/wiki](https://github.com/tieugene/wiki) commited on 22/March/21.
