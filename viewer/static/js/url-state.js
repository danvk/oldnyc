// The URL looks like one of these:
// /
// /#photo_id
// /#g:lat,lon
// /#photo_id,g:lat,lon

// Returns {photo_id:string, g:string}
function getCurrentStateObject() {
  if (!$('#expanded').is(':visible')) {
    return {};
  }
  var g = $('#expanded').data('grid-key');
  var selectedId = $('#grid-container').expandableGrid('selectedId');

  return selectedId ? { photo_id: selectedId, g: g } : { g: g };
}

// Converts the string after '#' in a URL into a state object,
// {photo_id:string, g:string}
function hashToStateObject(hash) {
  var m = hash.match(/(.*),g:(.*)/);
  if (m) {
    return {photo_id: m[1], g: m[2]};
  } else if (hash.substr(0, 2) == 'g:') {
    return {g: hash.substr(2)};
  } else if (hash.length > 0) {
    var photo_id = hash;
    var g = findLatLonForPhoto(photo_id);
    return {photo_id: hash, g: g};
  } else {
    return {};
  }
}

function stateObjectToHash(state) {
  if (state.photo_id) {
    if (state.g == 'pop') {
      return state.photo_id + ',g:pop';
    } else {
      return state.photo_id;
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
    var photo_ids = lat_lons[state.g];
    if (state.g == 'pop') {
      photo_ids = getPopularPhotoIds();
    }
    loadInfoForPhotoIds(photo_ids).done(function() {
      showExpanded(state.g, photo_ids, state.id);
    });
    return;
  }

  if (currentState.id && !state.id) {
    // Hide the selected photo
    $('#grid-container').expandableGrid('deselect');
  } else {
    // Show a different photo
    $('#grid-container').expandableGrid('select', state.id);
  }
}


function findLatLonForPhoto(photo_id) {
  for (var lat_lon in lat_lons) {
    var recs = lat_lons[lat_lon];
    for (var i = 0; i < recs.length; i++) {
      if (recs[i] == photo_id) {
        return lat_lon;
      }
    }
  }
  return null;
}
