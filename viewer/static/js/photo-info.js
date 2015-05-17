// This file manages all the photo information.
// Some of this comes in via lat-lons.js.
// Some is requested via XHR.

// Maps photo_id -> { title: ..., date: ..., library_url: ... }
var photo_id_to_info = {};

var SITE = 'http://oldnyc.github.io';
var JSON_BASE = SITE + '/by-location';

// The callback is called with the photo_ids that were just loaded, after the
// UI updates.  The callback may assume that infoForPhotoId() will return data
// for all the newly-available photo_ids.
function loadInfoForLatLon(lat_lon) {
  var url;
  if (lat_lon == 'pop') {
    url = SITE + '/popular.json';
  } else {
    url = JSON_BASE + '/' + lat_lon.replace(',', '') + '.json';
  }

  return $.getJSON(url).then(function(response_data, status, xhr) {
    // Add these values to the cache.
    $.extend(photo_id_to_info, response_data);
    var photo_ids = [];
    for (var k in response_data) {
      photo_ids.push(k);
    }
    if (lat_lon != 'pop') {
      lat_lon_to_name[lat_lon] = extractName(response_data);
    }
    return photo_ids;
  });
}

// Returns a {title: ..., date: ..., library_url: ...} object.
// If there's no information about the photo yet, then the values are all set
// to the empty string.
function infoForPhotoId(photo_id) {
  return photo_id_to_info[photo_id] ||
      { title: '', date: '', library_url: '' };
}

// Would it make more sense to incorporate these into infoForPhotoId?
function descriptionForPhotoId(photo_id) {
  var info = infoForPhotoId(photo_id);
  var desc = info.title;
  if (desc) desc += ' ';
  var date = info.date.replace(/n\.d\.?/, 'No Date');
  if (!date) date = 'No Date';
  desc += date;
  return desc;
}

function libraryUrlForPhotoId(photo_id) {
  return 'http://digitalcollections.nypl.org/items/image_id/' + photo_id.replace(/-[a-z]$/, '');
}

function backOfCardUrlForPhotoId(photo_id) {
  return 'http://images.nypl.org/?id=' + photo_id.replace('f', 'b').replace(/-[a-z]$/, '') + '&t=w';
}


var lat_lon_to_name = {};

// Does this lat_lon have a name, e.g. "Manhattan: 14th Street - 8th Avenue"?
function nameForLatLon(lat_lon) {
  var v = lat_lon_to_name[lat_lon] || '';
  return v.replace(/: | - | & /g, '\n');
}

function extractName(lat_lon_json) {
  // if any entries have an original_title, it's got to be a pure location.
  for (var k in lat_lon_json) {
    var v = lat_lon_json[k];
    if (v.original_title) return v.original_title;
  }
}
