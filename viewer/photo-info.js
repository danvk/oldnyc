// This file manages all the photo information.
// Some of this comes in via lat-lons.js.
// Some is requested via XHR.

// Maps photo_id -> { title: ..., date: ..., library_url: ... }
var photo_id_to_info = {};

// The callback is called with the photo_ids that were just loaded, after the
// UI updates.  The callback may assume that infoForPhotoId() will return data
// for all the newly-available photo_ids.
function loadInfoForPhotoIds(photo_ids, opt_callback) {
  var data = ''
  for (var i = 0; i < photo_ids.length; i++) {
    data += (i ? '&' : '') + 'id=' + photo_ids[i];
  }

  return $.post('/info', data, function(response_data, status, xhr) {
    // Add these values to the cache.
    $.extend(photo_id_to_info, response_data);
  }, 'json');
}

// Returns a {title: ..., date: ..., library_url: ...} object.
// If there's no information about the photo yet, then the values are all set
// to the empty string.
function infoForPhotoId(photo_id) {
  return photo_id_to_info[photo_id] ||
      { title: '', date: '', library_url: '' };
}

// Would it make more sense to incorporate this into infoForPhotoId?
function descriptionForPhotoId(photo_id) {
  var info = infoForPhotoId(photo_id);
  return info.title + '<br/>' + info.date;
}
