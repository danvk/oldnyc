// d3 state
var topLeft = {x: 100, y: 100};
var bottomRight = {x: 200, y: 200};
var pixelsPerLine = 8;
var pixelsPerColumn = 5;
var showColumns = false;
var epsilon = 1e-10;

function drawLines() {
  var svg = d3.select('svg');
  var zoom = detectZoom.device();

  var horizontalYs = d3.range(topLeft.y, bottomRight.y + epsilon, pixelsPerLine);
  var lines = svg.selectAll('.line')
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
  var vertLines = svg.selectAll('.vline')
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
  var svg = d3.select('svg');

  var dragTL = d3.behavior.drag()
    .origin(function() { return topLeft })
    .on('drag', function() {
        topLeft = {x: d3.event.x, y: d3.event.y};
        drawLines();
    });

  var dragBR = d3.behavior.drag()
    .origin(function() { return bottomRight })
    .on('drag', function() {
        bottomRight = {x: d3.event.x, y: d3.event.y};
        drawLines();
    });

  var dotTL = svg.append('circle')
      .attr('class', 'dot')
      .attr('r', 5)
      .call(dragTL);

  var dotBR = svg.append('circle')
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
}

$('img').on('load', function() {
  var width = $('img').width(),
      height = $('img').height();
  var svg = d3.select('#container').append('svg')
      .attr('width', width)
      .attr('height', height)

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
  $('#show-cols').prop('checked', showColumns);
  drawLines();
}

$(document).on('keydown', null, 'up', function(e) {
  topLeft.y -= 0.1;
  bottomRight.y -= 0.1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'down', function(e) {
  topLeft.y += 0.1;
  bottomRight.y += 0.1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'left', function(e) {
  topLeft.x -= 0.1;
  bottomRight.x -= 0.1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'right', function(e) {
  topLeft.x += 0.1;
  bottomRight.x += 0.1;
  updateUI();
  e.preventDefault();
}).on('keydown', null, 'h', function(e) {
  pixelsPerColumn -= 0.01;
  updateUI();
}).on('keydown', null, 'l', function(e) {
  pixelsPerColumn += 0.01;
  updateUI();
}).on('keydown', null, 'j', function(e) {
  pixelsPerLine += 0.05;
  updateUI();
}).on('keydown', null, 'k', function(e) {
  pixelsPerLine -= 0.05;
  updateUI();
}).on('keydown', null, 'x', function(e) {
  showColumns = !showColumns;
  updateUI();
});

var zoom = detectZoom.device();
$(window).resize(function() {
  var zoomNew = detectZoom.device();
  if (zoom != zoomNew) {
    // zoom has changed
    drawLines();

    zoom = zoomNew
  }
});
