var markers = [];
var marker_icons = [];
var lat_lon_to_marker = {};
var selected_marker_icons = [];
var selected_marker, selected_icon;
var map;
var start_date = 1850;
var end_date = 2000;
var LOG_HISTORY_EVENTS = false;

var mapPromise = $.Deferred();

function thumbnailImageUrl(photo_id) {
  return 'http://images.oldnyc.org/thumb/' + photo_id + '.jpg';
}

function expandedImageUrl(photo_id) {
  return 'http://images.oldnyc.org/600px/' + photo_id + '.jpg';
}

// lat_lon is a "lat,lon" string.
function makeStaticMapsUrl(lat_lon) {
  return 'http://maps.googleapis.com/maps/api/staticmap?center=' + lat_lon + '&zoom=15&size=150x150&maptype=roadmap&markers=color:red%7C' + lat_lon;
}

// Make the given marker the currently selected marker.
// This is purely UI code, it doesn't touch anything other than the marker.
function selectMarker(marker, numPhotos) {
  var zIndex = 0;
  if (selected_marker) {
    zIndex = selected_marker.getZIndex();
    selected_marker.setIcon(selected_icon);
  }

  if (marker) {
    selected_marker = marker;
    selected_icon = marker.getIcon();
    marker.setIcon(selected_marker_icons[numPhotos > 100 ? 100 : numPhotos]);
    marker.setZIndex(100000 + zIndex);
  }
}

// The callback gets fired when the info for all lat/lons at this location
// become available (i.e. after the /info RPC returns).
function displayInfoForLatLon(lat_lon, marker, opt_selectCallback) {
  var photo_ids = lat_lons[lat_lon];

  selectMarker(marker, photo_ids.length);

  loadInfoForPhotoIds(photo_ids).done(function() {
    var selectedId = null;
    if (photo_ids.length <= 10) {
      selectedId = photo_ids[0];
    }
    showExpanded(lat_lon, photo_ids, selectedId);
    if (opt_selectCallback && selectedId) {
      opt_selectCallback(selectedId);
    }
  }).fail(function() {
  });
}

function handleClick(e) {
  var lat_lon = e.latLng.lat().toFixed(6) + ',' + e.latLng.lng().toFixed(6)
  var marker = lat_lon_to_marker[lat_lon];
  displayInfoForLatLon(lat_lon, marker, function(photo_id) {
    $(window).trigger('openPreviewPanel');
    $(window).trigger('showPhotoPreview', photo_id);
  });
  $(window).trigger('showGrid', lat_lon);
}

function initialize_map() {
  var latlng = new google.maps.LatLng(40.74421, -73.97370);
  var opts = {
    zoom: 15,
    maxZoom: 18,
    minZoom: 10,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false,
    streetViewControl: true,
    panControl: false,
    zoomControlOptions: {
      position: google.maps.ControlPosition.LEFT_TOP
    },
    styles: [
        {
          featureType: "administrative.land_parcel",
          stylers: [
            { visibility: "off" }
          ]
        },{
          featureType: "landscape.man_made",
          stylers: [
            { visibility: "off" }
          ]
        },{
          featureType: "transit",
          stylers: [
            { visibility: "off" }
          ]
        },{
          featureType: "road.highway",
          elementType: "labels",
          stylers: [
            { visibility: "off" }
          ]
        },{
          featureType: "poi.business",
          stylers: [
            { visibility: "off" }
          ]
        }
      ]
  };
  
  map = new google.maps.Map($('#map').get(0), opts);

  // This shoves the navigation bits down by a CSS-specified amount
  // (see the .spacer rule). This is surprisingly hard to do.
  var map_spacer = $('<div/>').append($('<div/>').addClass('spacer')).get(0);
  map_spacer.index = -1;
  map.controls[google.maps.ControlPosition.TOP_LEFT].push(map_spacer);

  // The OldSF UI just gets in the way of Street View.
  // Even worse, it blocks the "exit" button!
  var streetView = map.getStreetView();
  google.maps.event.addListener(streetView, 'visible_changed',
      function() {
        $('.streetview-hide').toggle(!streetView.getVisible());
      });

  // Create marker icons for each number.
  marker_icons.push(null);  // it's easier to be 1-based.
  selected_marker_icons.push(null);
  for (var i = 0; i < 100; i++) {
    var num = i + 1;
    var size = (num == 1 ? 9 : 13);
    var selectedSize = (num == 1 ? 15 : 21);
    marker_icons.push(new google.maps.MarkerImage(
      'sprite-2014-08-29.png',
      new google.maps.Size(size, size),
      new google.maps.Point((i%10)*39, Math.floor(i/10)*39),
      new google.maps.Point((size - 1) / 2, (size - 1)/2)
    ));
    selected_marker_icons.push(new google.maps.MarkerImage(
      'selected-2014-08-29.png',
      new google.maps.Size(selectedSize, selectedSize),
      new google.maps.Point((i%10)*39, Math.floor(i/10)*39),
      new google.maps.Point((selectedSize - 1) / 2, (selectedSize - 1)/2)
    ));
  }

  // Adding markers is expensive -- it's important to defer this when possible.
  var idleListener = google.maps.event.addListener(map, 'idle', function() {
    google.maps.event.removeListener(idleListener);
    addNewlyVisibleMarkers();
    mapPromise.resolve(map);
  });

  google.maps.event.addListener(map, 'bounds_changed', function() {
    addNewlyVisibleMarkers();
  });
}

function addNewlyVisibleMarkers() {
  var bounds = map.getBounds();

  for (var lat_lon in lat_lons) {
    if (lat_lon in lat_lon_to_marker) continue;

    var pos = parseLatLon(lat_lon);
    if (!bounds.contains(pos)) continue;

    createMarker(lat_lon, pos);
  }
}

function parseLatLon(lat_lon) {
  var ll = lat_lon.split(",");
  return new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1]));
}

function createMarker(lat_lon, latLng) {
  var recs = lat_lons[lat_lon];
  var marker = new google.maps.Marker({
    position: latLng,
    map: map,
    flat: true,
    visible: true,
    icon: marker_icons[recs.length > 100 ? 100 : recs.length],
    title: lat_lon
  });
  markers.push(marker);
  lat_lon_to_marker[lat_lon] = marker;
  google.maps.event.addListener(marker, 'click', handleClick);
  return marker;
}


// NOTE: This can only be called when the info for all photo_ids at the current
// position have been loaded (in particular the image widths).
// key is used to construct URL fragments.
function showExpanded(key, photo_ids, opt_selected_id) {
  map.set('keyboardShortcuts', false);
  $('#expanded').show().data('grid-key', key);
  var images = $.map(photo_ids, function(photo_id, idx) {
    var info = infoForPhotoId(photo_id);
    return $.extend({
      id: photo_id,
      largesrc: expandedImageUrl(photo_id),
      src: thumbnailImageUrl(photo_id),
      width: 600,   // these are fallbacks
      height: 400
    }, info);
  });
  $('#preview-map').attr('src', makeStaticMapsUrl(key));
  $('#grid-container').expandableGrid({
    rowHeight: 200,
    speed: 200 /* ms for transitions */
  }, images);
  if (opt_selected_id) {
    $('#grid-container').expandableGrid('select', opt_selected_id);
  }
}

function hideExpanded() {
  $('#expanded').hide();
  $(document).unbind('keyup');
  map.set('keyboardShortcuts', true);
}

// This fills out details for either a thumbnail or the expanded image pane.
function fillPhotoPane(photo_id, $pane) {
  // This could be either a thumbnail on the right-hand side or an expanded
  // image, front and center.
  $('.description', $pane).html(descriptionForPhotoId(photo_id));

  var info = infoForPhotoId(photo_id);
  $('.library-link', $pane).attr('href', libraryUrlForPhotoId(photo_id));

  var canonicalUrl = getCanonicalUrlForPhoto(photo_id);

  if (photo_id.match('[0-9]f')) {
    $pane.find('.more-on-back > a').attr(
        'href', backOfCardUrlForPhotoId(photo_id));
    $pane.find('.more-on-back').show();
  } else {
    $pane.find('.more-on-back').hide();
  }

  var $comments = $pane.find('.comments');
  var width = $comments.parent().width();
  $comments.empty().append(
      $('<fb:comments numPosts="5" colorscheme="light"/>')
          .attr('width', width)
          .attr('href', canonicalUrl))
  FB.XFBML.parse($comments.get(0));

  twttr.widgets.createShareButton(
      document.location.href,
      $pane.find('.tweet').get(0), {
        count: 'none',
        text: info.title + ' - ' + info.date,
        via: 'Old_NYC'
      });

  var $fb_holder = $pane.find('.facebook-holder');
  $fb_holder.empty().append($('<fb:like>').attr({
      'href': canonicalUrl,
      'layout': 'button',
      'action': 'like',
      'show_faces': 'false',
      'share': 'true'
    }));
  FB.XFBML.parse($fb_holder.get(0));
}

function photoIdFromATag(a) {
  return $(a).attr('href').replace('/#', '');
}

function getPopularPhotoIds() {
  return $('.popular-photo:visible a').map(function(_, a) {
    return photoIdFromATag(a);
  }).toArray();
}

// User selected a photo in the "popular" grid. Update the static map.
function updateStaticMapsUrl(photo_id) {
  var key = 'New York City';
  var lat_lon = findLatLonForPhoto(photo_id);
  if (lat_lon) key = lat_lon;
  $('#preview-map').attr('src', makeStaticMapsUrl(key));
}

function fillPopularImagesPanel() {
  var makePanel = function(row) {
    var $panel = $('#popular-photo-template').clone().removeAttr('id');
    $panel.find('a').attr('href', '/#' + row.id);
    $panel.find('img')
        .attr('border', '0')  // For IE8
        .attr('data-src', expandedImageUrl(row.id))
        .attr('height', row.height);
    $panel.find('.desc').text(row.desc);
    $panel.find('.loc').text(row.loc);
    if (row.date) $panel.find('.date').text(' (' + row.date + ')');
    return $panel.get(0);
  };

  var popularPhotos = $.map(popular_photos, makePanel);
  $('#popular').append($(popularPhotos).show());
  loadNewlyVisibleImages($('#popular').get(0));
}

function loadNewlyVisibleImages(container) {
  $(container).find('img[data-src]').each(function(i, imgEl) {
    var $img = $(imgEl);
    if (isElementInViewport($img)) {
      $img
        .attr('src', $img.attr('data-src'))
        .removeAttr('data-src');
    }
  });
}

function hidePopular() {
  $('#popular').hide();
  $('.popular-link').show();
}
function showPopular() {
  $('#popular').show();
  $('.popular-link').hide();
}

function sendFeedback(photo_id, feedback_obj) {
  $.ajax('/rec_feedback', {
    data: { 'id': photo_id, 'feedback': JSON.stringify(feedback_obj) },
    method: 'post'
  }).fail(function() {
    console.warn('Unable to send feedback on', photo_id)
  });
  ga('send', 'event', 'link', 'feedback', { 'page': '/#' + photo_id });
}

$(function() {
  // Clicks on the background or "exit" button should leave the slideshow.
  $(document).on('click', '#curtains, .exit', function() {
    hideExpanded();
    $(window).trigger('hideGrid');
  });
  $('#grid-container, #expanded .header').on('click', function(e) {
    if (e.target == this || $(e.target).is('.og-grid')) {
      hideExpanded();
      $(window).trigger('hideGrid');
    }
  });

  // Fill in the expanded preview pane.
  $('#grid-container').on('og-fill', 'li', function(e, div) {
    var id = $(this).data('image-id');
    $(div).empty().append(
        $('#image-details-template').clone().removeAttr('id').show());
    fillPhotoPane(id, $(div));

    var g = $('#expanded').data('grid-key');
    if (g == 'pop') {
      updateStaticMapsUrl(id);
    }
  })
  .on('click', '.og-fullimg img', function() {
    var photo_id = $('#grid-container').expandableGrid('selectedId');
    window.open(libraryUrlForPhotoId(photo_id), '_blank');
  });

  $('#grid-container').on('click', '.rotate-image-button', function() {
    var $img = $(this).closest('li').find('.og-fullimg img');
    var currentRotation = $img.data('rotate') || 0;
    currentRotation += 90;
    $img
      .css('transform', 'rotate(' + currentRotation + 'deg)')
      .data('rotate', currentRotation);

    var photo_id = $('#grid-container').expandableGrid('selectedId');
    ga('send', 'event', 'link', 'rotate', {
      'page': '/#' + photo_id + '(' + currentRotation + ')'
    });
    sendFeedback(photo_id, {'rotate': currentRotation});
  });

  $('#grid-container').on('click', 'a.email-share', function(e) {
    var $social = $(this).parents('.social');
    var $form = $social.find('.email-share-form');
    $form.find('input').val(document.location.href);
    $form.toggle();
    $form.find('input').focus();
    e.preventDefault();
  }).on('click', '.email-share-form .close', function(e) {
    var $form = $(this).parents('.email-share-form');
    $form.toggle();
    e.preventDefault();
  });

  $('.popular-photo').on('click', 'a', function(e) {
    e.preventDefault();
    var selectedPhotoId = photoIdFromATag(this);
    var photoIds = getPopularPhotoIds();

    loadInfoForPhotoIds(photoIds).done(function() {
      showExpanded('pop', photoIds, selectedPhotoId);
      $(window).trigger('showGrid', 'pop');
      $(window).trigger('openPreviewPanel');
      $(window).trigger('showPhotoPreview', selectedPhotoId);
    }).fail(function() {
    });
  });

  $('#popular').on('scroll', function() {
    loadNewlyVisibleImages($('#popular').get(0));
  });

  // Show/hide popular images
  $('#popular .close').on('click', function() {
    document.cookie = 'nopop';
    hidePopular();
  });
  $('.popular-link a').on('click', function(e) {
    showPopular();
    document.cookie = '';
    e.preventDefault();
  });
  if (document.cookie.indexOf('nopop') >= 0) {
    hidePopular();
  }

  $('#grid-container').on('og-select', 'li', function() {
    var photo_id = $(this).data('image-id')
    $(window).trigger('showPhotoPreview', photo_id);
  }).on('og-deselect', function() {
    $(window).trigger('closePreviewPanel');
  }).on('og-openpreview', function() {
    $(window).trigger('openPreviewPanel');
  });
});
