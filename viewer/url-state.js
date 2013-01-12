var selected_marker = null;
var selected_icon = 0;
var expanded_photo_id = null;

// There are four bits of state:
// 1. Selected date range
// 2. Selected dot
// 3. Expanded image
// 4. Map position
function currentState() {
  var years = $('#slider').slider('values');
  if (years[0] == 1850 && years[1] == 2000) years = null;
  var selected_lat_lon = selected_marker ? selected_marker.title : null;
  if (selected_lat_lon == init_lat_lon) selected_lat_lon = null;
  var expanded = null;
  if ($('#expanded').css('display') != 'none') {
    expanded = expanded_photo_id + ',' + $('#expanded-image').width();
  }

  var center = map.getCenter();
  var map_state = center.lat().toFixed(5) + ',' + center.lng().toFixed(5) + ',' + map.getZoom();
  if (map_state == '37.79216,-122.41753,14') map_state = null;

  var state = {};
  if (years) state.y = years[0] + '-' + years[1];
  if (selected_lat_lon) state.ll = selected_lat_lon;
  if (expanded) state.e = expanded;
  if (map_state) state.m = map_state;
  return state;
}

var block_update = false;  // used when loading from a hash
var current_hash = null;
function updateHash() {
  if (block_update) return;
  var state = currentState();
  var hash = '';
  for (var k in state) {
    if (hash) hash += ',';
    hash += k + ':' + state[k].replace(/,/g, '|');
  }
  current_hash = hash;
  location.hash = hash;
}

function stateFromHash() {
  if (!location.hash) return {};

  var hash = '' + location.hash;
  if (hash.indexOf('%7') >= 0) {
    // twitter links come through as 'foo%7Cbar', not 'foo|bar'.
    hash = unescape(hash);
  }

  var parts = hash.substr(1).split(',');
  var state = {};
  for (var i = 0; i < parts.length; i++) {
    var kv = parts[i].split(':');
    var v = kv[1];
    if (v.indexOf('|') != -1) v = v.split('|');
    state[kv[0]] = v;
  }
  return state;
}

function loadFromHash() {
  var state = stateFromHash();
  block_update = true;
  if (state.hasOwnProperty('m')) {
    var ll = new google.maps.LatLng(parseFloat(state.m[0]), parseFloat(state.m[1]));
    var zoom = parseInt(state.m[2]);
    map.setCenter(ll);
    map.setZoom(parseInt(zoom));
  }
  if (state.hasOwnProperty('y')) {
    var ys = state.y.split('-');
    ys = [parseInt(ys[0]), parseInt(ys[1])];
    $('#slider').slider('values', ys);
    slide();
  }
  if (state.hasOwnProperty('ll')) {
    var marker = null;
    for (var i = 0; i < markers.length; i++) {
      if (markers[i].title == state.ll) {
        marker = markers[i];
        break;
      }
    }
    if (marker) {
      displayInfoForLatLon(state.ll, marker);
    }
  }
  if (state.hasOwnProperty('e')) {
    var id = state.e[0];
    var w = parseInt(state.e[1]);
    showExpanded(id, w);
  }
  block_update = false;
}
