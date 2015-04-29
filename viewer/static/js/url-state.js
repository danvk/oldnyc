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
// This is asynchronous because it may need to fetch ID->lat/lon info.
function hashToStateObject(hash, cb) {
  var m = hash.match(/(.*),g:(.*)/);
  if (m) {
    cb({photo_id: m[1], g: m[2]});
  } else if (hash.substr(0, 2) == 'g:') {
    cb({g: hash.substr(2)});
  } else if (hash.length > 0) {
    var photo_id = hash;
    findLatLonForPhoto(photo_id, function(g) {
      cb({photo_id: hash, g: g});
    });
  } else {
    cb({});
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
// This change may happen asynchronously.
// This won't affect the URL hash.
function transitionToStateObject(targetState) {
  var currentState = getCurrentStateObject();

  // This normalizes the state, i.e. adds a 'g' field to if it's implied.
  // (it also strips out extraneous fields)
  hashToStateObject(stateObjectToHash(targetState), function(state) {
    if (JSON.stringify(currentState) == JSON.stringify(state)) {
      return;  // nothing to do.
    }

    // Reset to map view.
    if (JSON.stringify(state) == '{}') {
      hideAbout();
      hideExpanded();
    }

    // Show a different grid?
    if (currentState.g != state.g) {
      var lat_lon = state.g;
      var count = lat_lons[lat_lon];
      if (state.g == 'pop') {
        count = getPopularPhotoIds().length;
      } else {
        // Highlight the marker, creating it if necessary.
        var marker = lat_lon_to_marker[lat_lon];
        var latLng = parseLatLon(lat_lon);
        if (!marker) {
          marker = createMarker(lat_lon, latLng);
        }
        if (marker) {
          selectMarker(marker, count);
          if (!map.getBounds().contains(latLng)) {
            map.panTo(latLng);
          }
        }
      }
      loadInfoForLatLon(lat_lon).done(function(photo_ids) {
        showExpanded(state.g, photo_ids, state.photo_id);
      });
      return;
    }

    if (currentState.photo_id && !state.photo_id) {
      // Hide the selected photo
      $('#grid-container').expandableGrid('deselect');
    } else {
      // Show a different photo
      $('#grid-container').expandableGrid('select', state.photo_id);
    }
  });
}


function findLatLonForPhoto(photo_id, cb) {
  var id4 = photo_id.slice(0, 4);
  $.ajax({
    dataType: "json",
    url: 'http://oldnyc.github.io/id4-to-location/' + id4 + '.json',
    success: function(id_to_latlon) {
      cb(id_to_latlon[photo_id])
    }
  });
}
