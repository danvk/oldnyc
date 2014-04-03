var markers = [];
var marker_icons = [];
var lat_lon_to_marker = {};
var selected_marker_icons = [];
var selected_marker;
var map;
var start_date = 1850;
var end_date = 2000;
var markers_set_for_zoom;

function isOldNycImage(photo_id) {
  // NYC images have IDs like '123f' or '345f-b'.
  return /f(-[a-z])?$/.test(photo_id);
}

// Multiplex between OldSF and OldNYC
function thumbnailImageUrl(photo_id) {
  return 'http://oldnyc.s3.amazonaws.com/thumb/' + photo_id + '.jpg';
  if (isOldNycImage(photo_id)) {
    // return 'http://images.nypl.org/index.php?id=' + photo_id + '&t=r';
    // return 'http://dv.nyc:8000/' + photo_id + '.jpg';
    // return 'http://localhost:8001/thumb/' + photo_id + '.jpg';
    // return 'http://192.168.1.7:8001/thumb/' + photo_id + '.jpg';
    // return 'http://localhost:8001/milstein-thumb/' + photo_id + '.jpg';
    // return 'https://s3.amazonaws.com/oldnyc/thumb/' + photo_id + '.jpg';
    return 'http://oldnyc.s3.amazonaws.com/thumb/' + photo_id + '.jpg';
  } else {
    return 'http://s3-us-west-1.amazonaws.com/oldsf/thumb/' + photo_id + '.jpg';
  }
}

function expandedImageUrl(photo_id) {
  // return 'https://s3.amazonaws.com/oldnyc/600px/' + photo_id + '.jpg';
  return 'http://oldnyc.s3.amazonaws.com/600px/' + photo_id + '.jpg';
  // return 'http://192.168.1.7:8001/600px/' + photo_id + '.jpg';
  if (isOldNycImage(photo_id)) {
    // return 'http://images.nypl.org/index.php?id=' + photo_id + '&t=w';
    // return 'http://localhost:8001/600px/' + photo_id + '.jpg';
    return 'http://192.168.1.7:8001/600px/' + photo_id + '.jpg';
    // return 'http://localhost:8001/milstein-600/' + photo_id + '.jpg';
  } else {
    return 'http://s3-us-west-1.amazonaws.com/oldsf/images/' + photo_id + '.jpg'
  }
}

// The callback gets fired when the info for all lat/lons at this location
// become available (i.e. after the /info RPC returns).
function displayInfoForLatLon(lat_lon, marker, opt_callback) {
  var recs = lat_lons[lat_lon];
  var photo_ids = [];
  for (var i = 0; i < recs.length; i++) {
    if (recs[i][0] >= start_date && recs[i][1] <= end_date) {
      photo_ids.push(recs[i][2]);
    }
  }

  var zIndex = 0;
  if (selected_marker) {
    zIndex = selected_marker.getZIndex();
    selected_marker.setIcon(selected_icon);
  }

  if (marker) {
    selected_marker = marker;
    selected_icon = marker.getIcon();
    marker.setIcon(selected_marker_icons[photo_ids.length > 100 ? 100 : photo_ids.length]);
    marker.setZIndex(100000 + zIndex);
  }

  loadInfoForPhotoIds(photo_ids, opt_callback).done(function() {
    var selectedId = null;
    if (photo_ids.length <= 10) {
      selectedId = photo_ids[0];
    }
    showExpanded(lat_lon.join(','), photo_ids, selectedId);
  }).fail(function() {
  });
}

// TODO(danvk): possible to just use the event?
function makeCallback(lat_lon, marker) {
  return function(e) {
    // lat_lon = e.latLng.lat().toFixed(6) + ',' + e.latLng.lng().toFixed(6)
    // marker = ...
    displayInfoForLatLon(lat_lon, marker);
  };
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
    var size = (num == 1 ? 9 : (num < 10 ? 13 : (num < 100 ? 25 : 39)));
    marker_icons.push(new google.maps.MarkerImage(
      'dots/sprite-2013-01-14.png',
      new google.maps.Size(size, size),
      new google.maps.Point((i%10)*39, Math.floor(i/10)*39),
      new google.maps.Point((size - 1) / 2, (size - 1)/2)
    ));
    selected_marker_icons.push(new google.maps.MarkerImage(
      'dots/selected-2013-01-14.png',
      new google.maps.Size(size, size),
      new google.maps.Point((i%10)*39, Math.floor(i/10)*39),
      new google.maps.Point((size - 1) / 2, (size - 1)/2)
    ));
  }

  for (var lat_lon in lat_lons) {
    var recs = lat_lons[lat_lon];
    var ll = lat_lon.split(",");
    marker = new google.maps.Marker({
      position: new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1])),
      map: map,
      flat: true,
      visible: true,
      icon: marker_icons[recs.length > 100 ? 100 : recs.length],
      title: lat_lon
    });
    markers.push(marker);
    lat_lon_to_marker[lat_lon] = marker;
    google.maps.event.addListener(marker, 'click', makeCallback(ll, marker));
  }

  markers_set_for_zoom = opts.zoom;
  google.maps.event.addListener(map, 'zoom_changed', setMarkerIcons);

  setUIFromUrlHash();
}


function clamp(x, min, max) {
  return Math.min(max, Math.max(min, x));
}


// Called in response to a zoom event.
function setMarkerIcons() {
  var oldFactor = Math.min(1, Math.pow(4, markers_set_for_zoom - 15));
  var scaleFactor = Math.min(1, Math.pow(4, map.getZoom() - 15));

  if (oldFactor == scaleFactor) return;

  for (var lat_lon in lat_lons) {
    var marker = lat_lon_to_marker[lat_lon];
    var numPoints = lat_lons[lat_lon].length;
    var oldIdx = clamp(Math.floor(numPoints * oldFactor), 1, 100);
    var newIdx = clamp(Math.floor(numPoints * scaleFactor), 1, 100);
    if (oldIdx != newIdx) {
      marker.setIcon(marker_icons[newIdx]);
    }
  }
  markers_set_for_zoom = map.getZoom();
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
  $('#grid-container').expandableGrid({
    rowHeight: 200
  }, images);
  if (opt_selected_id) {
    $('#grid-container').expandableGrid('select', opt_selected_id);
  }

  stateWasChanged();
}

function hideExpanded() {
  $('#expanded').hide();
  $(document).unbind('keyup');
  map.set('keyboardShortcuts', true);
  stateWasChanged();
}

// This fills out details for either a thumbnail or the expanded image pane.
function fillPhotoPane(photo_id, $pane) {
  // This could be either a thumbnail on the right-hand side or an expanded
  // image, front and center.
  $('.description', $pane).html(descriptionForPhotoId(photo_id));

  var info = infoForPhotoId(photo_id);
  $('.library-link', $pane).attr('href', libraryUrlForPhotoId(photo_id));

  var $comments = $pane.find('.comments');
  var width = $comments.parent().width();
  $comments.empty().append(
      $('<fb:comments numPosts="5" colorscheme="light"/>')
          .attr('width', width)
          .attr('href', getCanonicalUrlForPhoto(photo_id)))
  FB.XFBML.parse($comments.get(0));
}

function photoIdFromATag(a) {
  return $(a).attr('href').replace('/#', '');
}

function getPopularPhotoIds() {
  return $('.popular-photo a').map(function(_, a) {
    return photoIdFromATag(a);
  }).toArray();
}

$(function() {
  // Clicks on the background or "exit" button should leave the slideshow.
  // Clicks on the strip itself should only exit if they're not on an image.
  $('#curtains, #exit-slideshow').click(hideExpanded);

  $('#grid-container').on('og-select', 'li', function(e, div) {
    var id = $(this).data('image-id');
    $(div).empty().append(
        $('#image-details-template').clone().removeAttr('id').show());
    fillPhotoPane(id, $(div));
    stateWasChanged(id);
  })
  .on('og-deselect', function() {
    stateWasChanged(null);
  })
  .on('click', '.og-fullimg', function() {
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
  });

  $('.popular-photo').on('click', 'a', function(e) {
    e.preventDefault();
    var selectedPhotoId = photoIdFromATag(this);
    var photoIds = getPopularPhotoIds();

    loadInfoForPhotoIds(photoIds).done(function() {
      showExpanded('pop', photoIds, selectedPhotoId);
    }).fail(function() {
    });
  });
});
