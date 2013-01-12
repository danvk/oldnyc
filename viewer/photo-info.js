// This file manages all the photo information.
// Some of this comes in via lat-lons.js.
// Some is requested via XHR.

// Maps photo_id -> { title: ..., date: ..., library_url: ... }
var photo_id_to_info = {};

function loadInfoForPhotoIds(photo_ids) {
  var data = ''
  for (var i = 0; i < photo_ids.length; i++) {
    data += (i ? '&' : '') + 'id=' + photo_ids[i];
  }

  $.getJSON('/info', data, function(data, status, xhr) {
    // Add these values to the cache.
    $.extend(photo_id_to_info, data);

    // Update any on-screen elements.
    $.each(data, function(photo_id, info) {
      // This could be either a thumbnail on the right-hand side or an expanded
      // image, front and center.
      var $pane = $('[photo_id=' + photo_id + ']');
      $('.description', $pane).html(descriptionForPhotoId(photo_id));

      // TODO(danvk): this is kinda gross
      $('.thumb', $pane)
        .html('<a href="javascript:showExpanded(\'' + photo_id + '\')">' +
          $('.thumb', $pane).html() + '</a>');
      $('.library-link', $pane)
        .attr('href', info.library_url);
    });
  });
}

// Returns a {title: ..., date: ..., library_url: ...} object.
// If there's no information about the photo yet, then the values are all set
// to the empty string.
function infoForPhotoId(photo_id) {
  return photo_id_to_info[photo_id] ||
      { title: '', date: '', library_url: '' };
}

function descriptionForPhotoId(photo_id) {
  var info = infoForPhotoId(photo_id);
  return info.title + '<br/>' + info.date;
}
