var selected_marker = null;
var selected_icon = 0;

// There are four bits of state:
// 1. Selected date range
// 2. Selected dot
// 3. Expanded image
// 4. Map position & zoom
function currentState() {
  var years = $('#slider').slider('values');
  if (years[0] == 1850 && years[1] == 2000) years = null;

  var selected_lat_lon = selected_marker ? selected_marker.title : null;
  if (selected_lat_lon == init_lat_lon) selected_lat_lon = null;

  var expanded = null;
  if ($('#expanded').css('display') != 'none') {
    var photo_id = $('.current').attr('photo_id');
    var width = $('.current img').width();
    expanded = photo_id + ',' + width;
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

// Converts a state dictionary to something that can go in the URL hash.
// Returned string does not include leading '#'.
function stateToHash(state) {
  var hash = '';
  for (var k in state) {
    if (hash) hash += ',';
    hash += k + ':' + state[k].replace(/,/g, '|');
  }
  return hash;
}

// Inverse of the above.
function hashToState(url_hash) {
  if (!url_hash) return {};

  var hash = '' + url_hash;  // in case location.hash is passed in.
  if (hash.substr(0, 1) == '#') {
    hash = hash.substr(1);
  }

  if (hash.indexOf('%7') >= 0) {
    // twitter links come through as 'foo%7Cbar', not 'foo|bar'.
    hash = unescape(hash);
  }

  var parts = hash.split(',');
  var state = {};
  for (var i = 0; i < parts.length; i++) {
    var kv = parts[i].split(':');
    var v = kv[1];
    if (v.indexOf('|') != -1) v = v.replace(/\|/g, ',');
    state[kv[0]] = v;
  }
  return state;
}


function areStatesEqual(state1, state2) {
  // I'm lazy.
  return JSON.stringify(state1) == JSON.stringify(state2);
}


var block_update = false;  // used when loading from a hash
var current_state = null;  // this is a state dictionary


// Call this whenever something happens to change the state of the page.
function stateWasChanged() {
  if (block_update) return;
  var old_state = current_state;
  current_state = currentState();
  var hash = stateToHash(current_state);

  // Only save a state to the browser history when the selected dot changes.
  var saveToHistory = (!old_state || old_state.ll != current_state.ll);
  block_update = true;
  setUrlHash(hash, saveToHistory);
  block_update = false;
}


// Make the UI match the state object.
function loadFromState(state) {
  block_update = true;
  if (state.hasOwnProperty('m')) {
    var m = state['m'].split(',');
    var ll = new google.maps.LatLng(parseFloat(m[0]), parseFloat(m[1]));
    var zoom = parseInt(m[2]);
    map.setCenter(ll);
    map.setZoom(parseInt(zoom));
  }

  if (state.hasOwnProperty('y')) {
    var ys = state['y'].split('-');
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
    var e = state['e'].split(',');
    var id = e[0];
    var w = parseInt(e[1]);
    showExpanded(id, w);
  }
  block_update = false;
}


// Updates the URL hash, optionally including this URL in the browser's
// navigation history.
// |hash| should not include the leading '#'.
function setUrlHash(hash, include_in_history) {
  // Only clicks on new dots should enter the navigation history.
  if (include_in_history) {
    location.assign('#' + hash);
  } else {
    location.replace('#' + hash);
  }
}


// Updates the UI based on the current URL hash.
function setUIFromUrlHash() {
  if (block_update) return;
  var state = hashToState(location.hash);
  if (areStatesEqual(state, current_state)) return;
  loadFromState(state);
}

// This enables pasting hashed URLs
$(window).hashchange(setUIFromUrlHash);
