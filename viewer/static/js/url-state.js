// The URL looks like one of these:
// /
// /#photo_id
// /#g:lat,lon
// /#photo_id,g:lat,lon

// Returns {id:string, g:string}
function getCurrentStateObject() {
  if (!$('#expanded').is(':visible')) {
    return {};
  }
  var g = $('#expanded').data('grid-key');
  var selectedId = $('#grid-container').expandableGrid('selectedId');

  return selectedId ? { id: selectedId, g: g } : { g: g };
}

// Converts the string after '#' in a URL into a state object,
// {id:string, g:string}
function hashToStateObject(hash) {
  var m = hash.match(/(.*),g:(.*)/);
  if (m) {
    return {id: m[1], g: m[2]};
  } else if (hash.substr(0, 2) == 'g:') {
    return {g: hash.substr(2)};
  } else if (hash.length > 0) {
    var photo_id = hash;
    var g = findLatLonForPhoto(photo_id);
    return {id: hash, g: g};
  } else {
    return {};
  }
}

function stateObjectToHash(state) {
  if (state.id) {
    if (state.g == 'pop') {
      return state.id + ',g:pop';
    } else {
      return state.id;
    }
  }

  if (state.g) {
    return 'g:' + state.g;
  }
  return '';
}

// Change whatever is currently displayed to reflect the state in obj.
// This won't affect the URL hash.
function transitionToStateObject(state) {
  var currentState = getCurrentStateObject();
  if (JSON.stringify(currentState) == JSON.stringify(state)) {
    return;  // nothing to do.
  }

  // Show a different grid?
  if (currentState.g != state.g) {
    var photo_ids = $(lat_lons[state.g]).map(function(_, r) { return r[2] });
    if (state.g == 'pop') {
      photo_ids = getPopularPhotoIds();
    }
    loadInfoForPhotoIds(photo_ids).done(function() {
      showExpanded(state.g, photo_ids, state.id);
    });
    return;
  }

  // Show a different photo?
  $('#grid-container').expandableGrid('select', state.id);
}


// Updates the URL hash to reflect the new state, adding history as appropriate.
function updateHash(newState) {
  var oldState = hashToStateObject(window.location.hash.substr(1));
  var addToHistory = oldState.g !== newState.g;
  var newHash = stateObjectToHash(newState);
  hashChangesToIgnore[newHash] = true;
  if (addToHistory) {
    location.assign('#' + newHash);
  } else {
    location.replace('#' + newHash);
  }
}

function findLatLonForPhoto(photo_id) {
  for (var lat_lon in lat_lons) {
    var recs = lat_lons[lat_lon];
    for (var i = 0; i < recs.length; i++) {
      if (recs[i][2] == photo_id) {
        return lat_lon;
      }
    }
  }
  return null;
}

var selected_marker = null;
var selected_icon = 0;


var block_update = false;  // used when loading from a hash
var hashChangesToIgnore = {};


// Call this whenever something happens to change the state of the page.
function stateWasChanged(selectedId) {
  var state = getCurrentStateObject();
  state.id = selectedId;
  updateHash(state);
}

// Updates the UI based on the current URL hash.
function setUIFromUrlHash() {
  var state = hashToStateObject(location.hash.substr(1));
  transitionToStateObject(state);
}

// This enables pasting hashed URLs
// $(window).hashchange(function() {
//   var hash = location.hash.substr(1);
//   setUIFromUrlHash();
// });
