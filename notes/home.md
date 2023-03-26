title: Overview
tags: 

The mind mapper tool is a simple tool based upon the [Python wiki tool](https://github.com/tieugene/wiki) and [D3.js](https://d3js.org/).

We associate a concept map to each tag. The links in all tags can be found in [`TheVortex`](http://localhost.localdomain:5004/maps/theVortex/) concept map (linked in the main menu above).

Each concept map consists of the pages with a given tag together with any "wikilinks" between pages.

This collection of links provides a web of links which are displayed using the D3.js [spring force display](https://github.com/d3/d3-force/blob/v3.0.0/README.md#forceSimulation).

Individual nodes in this display can be pulled about to help focus upon sub-parts of the given concept map.

Hovering over any node will provide you with the page's title.

Clicking on any sucession of nodes will turn it each node red.

Double clicking on any node will open that page in a new tab.

Double clicking outside of any node will zoom in.

Draging with the mouse outside of any node will pull the whole graph to a different center.
