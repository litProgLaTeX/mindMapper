// MindMap java script 
//
// REQUIRES graph GLOBAL variable.
//
// the following has been modified from:
// https://bl.ocks.org/mbostock/2675ff61ea5e063ede2b5d63c08020c7
// https://bl.ocks.org/puzzler10/4438752bb93f45dc5ad5214efaa12e4a
// http://www.puzzlr.org/zoom-in-d3-v4/
// https://stackoverflow.com/a/11809868
// https://stackoverflow.com/a/39449766
//

function ticked() {
  link
    .attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

  node
    .attr("cx", function(d) { return d.x; })
    .attr("cy", function(d) { return d.y; });
}

// see: https://observablehq.com/@d3/click-vs-drag
function drag() {

  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}

function nodeClicked(d, i) {
  if (d3.event.defaultPrevented) return; // dragged

  var thisNode = d3.select(this);

  if (+thisNode.attr("r") < 4) {
    thisNode.transition()
      .attr("fill", "red")
      .attr("r",  5);
  } else {
    thisNode.transition()
      .attr("fill", "black")
      .attr("r",  2.5);
  }
}

function nodeDblClicked(d) {
  if (d3.event.defaultPrevented) return; // dragged

  window.open(d.path);  
}

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    outerSvg = svg.append("g");

function zoomActions() {
  outerSvg.attr("transform", d3.event.transform);
}

  svg.call(d3.zoom()
    .scaleExtent([1 / 4, 8])
    .on("zoom", zoomActions));

  svg.append("defs").append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 10)
      .attr("refY", 0)
      .attr("markerWidth", 8)
      .attr("markerHeight", 8)
      .attr("orient", "auto")
    .append("svg:path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("stroke", "context-stroke")
      .attr("fill", "context-fill");

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

var link = outerSvg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
      .attr("stroke", function(d) { return d.color; })
      .attr("marker-end", "url(#arrow)");

link.append("title")
  .text(function(d) { return d.linkType; });

var node = outerSvg.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
      .attr("fill", function(d) { return d.color; })
      .attr("r", 2.5)
      .call(drag())
      .on("click", nodeClicked)
      .on("dblclick", nodeDblClicked);

node.append("title")
    .text(function(d) { return d.id; });

node.append("a")
    .attr("href", function(d) { return d.path ; })
    .text(function(d) { return d.id ; });

simulation
   .nodes(graph.nodes)
   .on("tick", ticked);

simulation.force("link")
   .links(graph.links);

