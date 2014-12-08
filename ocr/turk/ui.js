// d3 state
var topLeft = {x: 500, y: 2200};
var bottomRight = {x: 3400, y: 2600};
var numLines = 10;
var numCols = 80;
// var pixelsPerLine = 67.5;
// var pixelsPerColumn = 40.8;
var pixelsPerColumn, pixelsPerLine;
var showColumns = false;
var epsilon = 1e-10;
var rotateDeg = 0.0;

function drawLines() {
  pixelsPerLine = (bottomRight.y - topLeft.y) / numLines;
  pixelsPerColumn = (bottomRight.x - topLeft.x) / numCols;

  var svg = d3.select('svg');
  var g = svg.select('g');
  var zoom = detectZoom.device();

  g.style('transform', 'rotate(' + rotateDeg + 'deg)');

  var horizontalYs = d3.range(topLeft.y, bottomRight.y + epsilon, pixelsPerLine);
  var lines = g.selectAll('.line')
      .data(horizontalYs);

  lines
    .enter().append('line')
      .attr('class', 'line');

  lines
      .attr('x1', topLeft.x)
      .attr('y1', _.identity)
      .attr('x2', bottomRight.x)
      .attr('y2', _.identity)
      .style('stroke-width', 0.5 / zoom);

  lines.exit().remove();

  var verticalXs = d3.range(topLeft.x, bottomRight.x + epsilon, pixelsPerColumn);
  var vertLines = g.selectAll('.vline')
      .data(verticalXs);

  vertLines
    .enter().append('line')
      .attr('class', 'vline');

  vertLines
      .attr('x1', _.identity)
      .attr('y1', topLeft.y)
      .attr('x2', _.identity)
      .attr('y2', bottomRight.y)
      .style('stroke-width', 0.5 / zoom)
      .style('visibility', (showColumns ? 'visible' : 'hidden'));

  vertLines.exit().remove();

  positionDots();
  setHiddenForm();
}

function makeDots() {
  var g = d3.select('g');

  var mode = function() {
    return $('#move').is(':checked') ? 'move' : 'rotate';
  };

  var calcRotation = function(a, b) {
    return Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
  };
  var offsetEventCoord = function(base, mouseStart) {
    var coord = {x: d3.event.sourceEvent.pageX, y: d3.event.sourceEvent.pageY};
    var dx = coord.x - startRotateCoord.x,
        dy = coord.y - startRotateCoord.y;
    return {x: startBR.x + dx, y: startBR.y + dy};
  };

  var startRotation, startRotateDeg;
  var startRotateCoord;
  var startTL = _.clone(topLeft), startBR = _.clone(bottomRight);
  var dragTL = d3.behavior.drag()
    .origin(function() { return startTL })
    .on('drag', function() {
      if (mode() == 'move') {
        topLeft = {x: d3.event.x, y: d3.event.y};
      } else {
        var newRotation = calcRotation(topLeft, offsetEventCoord(startBR, startRotateCoord));
        rotateDeg = startRotateDeg - (newRotation - startRotation);
      }
      drawLines();
    }).on('dragstart', function() {
      startTL = topLeft;
      startRotation = calcRotation(topLeft, bottomRight);
      startRotateDeg = rotateDeg;
      startRotateCoord = {x: d3.event.sourceEvent.pageX, y: d3.event.sourceEvent.pageY};
      d3.event.sourceEvent.stopPropagation(); // silence other listeners
    }).on('dragend', function() {
      startTL = topLeft;
    });

  var dragBR = d3.behavior.drag()
    .origin(function() { return startBR })
    .on('drag', function() {
      if (mode() == 'move') {
        bottomRight = {x: d3.event.x, y: d3.event.y};
      } else {
        var newRotation = calcRotation(topLeft, offsetEventCoord(startBR, startRotateCoord));
        rotateDeg = startRotateDeg + (newRotation - startRotation);
      }
      drawLines();
    }).on('dragstart', function() {
      startBR = bottomRight;
      startRotation = calcRotation(topLeft, bottomRight);
      startRotateDeg = rotateDeg;
      startRotateCoord = {x: d3.event.sourceEvent.pageX, y: d3.event.sourceEvent.pageY};
      d3.event.sourceEvent.stopPropagation(); // silence other listeners
    }).on('dragend', function() {
      startBR = bottomRight;
    });

  var dotTL = g.append('circle')
      .attr('class', 'dot')
      .attr('r', 5)
      .call(dragTL);

  var dotBR = g.append('circle')
      .attr('class', 'dot')
      .attr('r', 5)
      .call(dragBR);

  positionDots();
}

function positionDots() {
  var dots = d3.selectAll('.dot');

  d3.select(dots[0][0])
      .attr('cx', topLeft.x)
      .attr('cy', topLeft.y)
  d3.select(dots[0][1])
      .attr('cx', bottomRight.x)
      .attr('cy', bottomRight.y)
}

function setHiddenForm() {
  $('[name="x1"]').val(topLeft.x);
  $('[name="y1"]').val(topLeft.y);
  $('[name="x2"]').val(bottomRight.x);
  $('[name="y2"]').val(bottomRight.y);
  $('[name="pp-line"]').val(pixelsPerLine);
  $('[name="pp-col"]').val(pixelsPerColumn);
  $('[name="rotate-deg"]').val(rotateDeg);
}

$('img').on('load', function() {
  updateUI();
  var width = $('img').width(),
      height = $('img').height();
  var svg = d3.select('#container').append('svg')
      .attr('width', width)
      .attr('height', height)
  var g = svg.append('g');

  makeDots();
  drawLines();
});

$('#pp-line').on('change', function(e) {
    pixelsPerLine = parseFloat($(this).val());
    drawLines();
});
$('#pp-col').on('change', function(e) {
    pixelsPerColumn = parseFloat($(this).val());
    drawLines();
});
$('#show-cols').on('change', function(e) {
    showColumns = $(this).is(':checked');
    drawLines();
});

function updateUI() {
  $('#pp-line').val(pixelsPerLine)
  $('#pp-col').val(pixelsPerColumn)
  $('#num-lines').text(numLines)
  $('#num-cols').text(numCols)
  $('#show-cols').prop('checked', showColumns);
  drawLines();
}

$(document).on('keydown', null, 'up', function(e) {
  topLeft.y -= 1;
  bottomRight.y -= 1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'down', function(e) {
  topLeft.y += 1;
  bottomRight.y += 1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'left', function(e) {
  topLeft.x -= 1;
  bottomRight.x -= 1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'right', function(e) {
  topLeft.x += 1;
  bottomRight.x += 1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'h', function(e) {
  // pixelsPerColumn -= 0.1;
  numCols -= 1;
  updateUI();
}).on('keydown', null, 'l', function(e) {
  // pixelsPerColumn += 0.1;
  numCols += 1;
  updateUI();
}).on('keydown', null, 'j', function(e) {
  // pixelsPerLine += 0.5;
  numLines += 1;
  updateUI();
}).on('keydown', null, 'k', function(e) {
  // pixelsPerLine -= 0.5;
  numLines -= 1;
  updateUI();
}).on('keydown', null, 'x', function(e) {
  showColumns = !showColumns;
  updateUI();
}).on('keydown', null, 'r', function(e) {
  $('#rotate').click();
}).on('keydown', null, 'm', function(e) {
  $('#move').click();
})

$('button').on('click', function() {
  document.forms[0].submit();
})

var zoom = detectZoom.device();
$(window).resize(function() {
  var zoomNew = detectZoom.device();
  if (zoom != zoomNew) {
    // zoom has changed
    drawLines();

    zoom = zoomNew
  }
});

// Set the state based on the output of a previous run. Useful for debugging.
function setState(csv_line) {
  "    0,       1,     2,      3,         4, 5, 6, 7, 8";
  "image,photo_id,pp-col,pp-line,rotate-deg,x1,x2,y1,y2";
  "ocr/large-images/700078bu.jpg,700078f,40.8,67.6,0.8909002235013688,622,3448.959228515625,2453,3217.71240234375";
  var p = csv_line.split(",");
  topLeft = {x: parseFloat(p[5]), y: parseFloat(p[7])};
  bottomRight = {x: parseFloat(p[6]), y: parseFloat(p[8])};
  pixelsPerLine = parseFloat(p[3]);
  pixelsPerColumn = parseFloat(p[2]);
  rotateDeg = parseFloat(p[4]);
  updateUI();
}
