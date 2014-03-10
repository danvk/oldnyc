var marker_icons = [];
var selected_marker_icons = [];
var map;
var start_date = 1850;
var end_date = 2000;
var polygons = {};
var neighborhood_to_markers = {};

function isOldNycImage(photo_id) {
  // NYC images have IDs like '123f' or '345f-b'.
  return /f(-[a-z])?$/.test(photo_id);
}

// Multiplex between OldSF and OldNYC
function thumbnailImageUrl(photo_id) {
  if (isOldNycImage(photo_id)) {
    // return 'http://images.nypl.org/index.php?id=' + photo_id + '&t=r';
    // return 'http://dv.nyc:8000/' + photo_id + '.jpg';
    // return 'http://localhost:8001/thumb/' + photo_id + '.jpg';
    // return 'http://192.168.1.7:8001/thumb/' + photo_id + '.jpg';
    // return 'http://localhost:8001/milstein-thumb/' + photo_id + '.jpg';
    return 'https://s3.amazonaws.com/oldnyc/thumb/' + photo_id + '.jpg';
  } else {
    return 'http://s3-us-west-1.amazonaws.com/oldsf/thumb/' + photo_id + '.jpg';
  }
}

function expandedImageUrl(photo_id) {
  return 'https://s3.amazonaws.com/oldnyc/600px/' + photo_id + '.jpg';
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
function displayInfoForLatLon(recs, marker, opt_callback) {
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
    showExpanded(photo_ids);
  }).fail(function() {
  });
}

function opacityForNumPhotos(num) {
  if (num == 0) return 0.0;
  if (num <= 20) return 0.2;
  if (num <= 50) return 0.3;
  if (num <= 100) return 0.4;
  if (num <= 200) return 0.5;
  if (num <= 500) return 0.6;
  if (num <= 1000) return 0.7;
  return 0.8;
}

// TODO(danvk): possible to just use the event?
function makeCallback(lat_lon, marker) {
  return function(e) {
    displayInfoForLatLon(lat_lons[lat_lon], marker);
    stateWasChanged();
  };
}

function initialize_map() {
  // google.maps.visualRefresh = true;

  // Give them something to look at while the map loads:
  init_lat_lon = "37.771393,-122.428618";

  // var latlng = new google.maps.LatLng(37.79216, -122.41753);
  var latlng = new google.maps.LatLng(40.74421, -73.97370);
  var opts = {
    zoom: 14,
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

  for (var neighborhood in neighborhood_polygons) {
    var photos = neighborhood_photos[neighborhood];
    if (!photos || photos.length == 0) continue;

    var coords = neighborhood_polygons[neighborhood];
    var gmap_coords = $.map(coords, function(lat_lon) {
      return new google.maps.LatLng(lat_lon[1], lat_lon[0]);
    });

    var polygon = new google.maps.Polygon({
      path: gmap_coords,
      geodesic: true,
      strokeColor: '#FFFFFF',
      strokeOpacity: 1.0,
      strokeWeight: 2,
      fillColor: '#000000',
      fillOpacity: opacityForNumPhotos(neighborhood_photos[neighborhood].length)
    });

    polygon.setMap(map);
    polygons[neighborhood] = polygon;
    google.maps.event.addListener(polygon, 'click', (function(neighborhood) {
      return function() {
        handleNeighorhoodClick(neighborhood);
        stateWasChanged();
      };
    })(neighborhood));
  }

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

  // When the map is idle, check if we should expand/collapse polygons.
  // Thresholds:
  // zoom level 0-12: only show polygons
  // zoom level 15+: only show individual points
  google.maps.event.addListener(map, 'idle', function() {
    var mapBounds = map.getBounds();
    $.each(polygons, function(neighborhood, polygon) {
      if (polygon.getBounds().intersects(mapBounds)) {
        var isManhattan = neighborhood.substr(-11) == ', Manhattan';
        if (map.getZoom() >= 15) {
          showIndividualPhotosForNeighborhood(neighborhood);
        } else {
          collapseNeighborhood(neighborhood);
        }
      }
    });
  });
}

// Hides the neighborhood polygons and show markers for each location.
function handleNeighorhoodClick(neighborhood) {
  // The sequence:
  // 1. Show points for this neighborhood.
  // 2. Zoom to the neighborhood.
  // (deferred) Show polygons for other visible neighborhoods.

  showIndividualPhotosForNeighborhood(neighborhood);

  // This will fire event listeners which will expand the other neighborhoods,
  // as needed.
  var polygon = polygons[neighborhood];
  var centroid = GetCentroid(polygon.getPath());
  map.setCenter(centroid);
  map.setZoom(15);
}

function showIndividualPhotosForNeighborhood(neighborhood) {
  var polygon = polygons[neighborhood];
  if (polygon.getMap() == null) {
    return;  // We're already showing individual photos for this neighborhood
  }

  polygon.setMap(null);  // hide the polygon
  var markers = neighborhood_to_markers[neighborhood];
  if (!markers) {
    // First click: figure out which markers are in this neighborhood.
    var records = neighborhood_photos[neighborhood];
    var ids = {};
    $.each(records, function(_, rec) {
      ids[rec[2]] = true;
    });
    markers = [];
    for (var lat_lon in lat_lons) {
      var ll_recs = lat_lons[lat_lon];
      var id = ll_recs[0][2];
      if (!(id in ids)) continue;
      var ll = lat_lon.split(',');

      var marker = new google.maps.Marker({
        position: new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1])),
        map: map,
        flat: true,
        visible: true,
        icon: marker_icons[ll_recs.length > 100 ? 100 : ll_recs.length],
        title: lat_lon
      });
      markers.push(marker);
      google.maps.event.addListener(marker, 'click', makeCallback(ll, marker));
    }
    neighborhood_to_markers[neighborhood] = markers;
  } else {
    $.each(markers, function(_, marker) {
      marker.setMap(map);
    });
  }
}

// Hide all the markers for a neighborhood and show the polygon.
function collapseNeighborhood(neighborhood) {
  var polygon = polygons[neighborhood];
  if (polygon.getMap() != null) {
    return;  // We're already showing the polygon for this neighborhood.
  }

  var markers = neighborhood_to_markers[neighborhood];
  if (!markers) {
    // this really shouldn't happen...
  } else {
    $.each(markers, function(_, marker) {
      marker.setMap(null);
    });
  }

  polygon.setMap(map);
}


// NOTE: This can only be called when the info for all photo_ids at the current
// position have been loaded (in particular the image widths).
function showExpanded(photo_ids) {
  $('#expanded').show();
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

// From https://code.google.com/p/google-maps-extensions
if (!google.maps.Polygon.prototype.getBounds) {
  google.maps.Polygon.prototype.getBounds = function(latLng) {
    var bounds = new google.maps.LatLngBounds();
    var paths = this.getPaths();
    var path;
    for (var p = 0; p < paths.getLength(); p++) {
      path = paths.getAt(p);
      for (var i = 0; i < path.getLength(); i++) {
        bounds.extend(path.getAt(i));
      }
    }
    return bounds;
  }
}

// From http://stackoverflow.com/questions/5187806/trying-to-get-the-cente-lat-lon-of-a-polygon
function GetCentroid(path) {
  var f;
  var x = 0;
  var y = 0;
  var nPts = path.length;
  var j = nPts-1;
  var area = 0;
  
  for (var i = 0; i < nPts; j=i++) {   
    var pt1 = path.getAt(i);
    var pt2 = path.getAt(j);
    f = pt1.lat() * pt2.lng() - pt2.lat() * pt1.lng();
    x += (pt1.lat() + pt2.lat()) * f;
    y += (pt1.lng() + pt2.lng()) * f;

    area += pt1.lat() * pt2.lng();
    area -= pt1.lng() * pt2.lat();        
  }
  area /= 2;
  f = area * 6;
  return new google.maps.LatLng(x/f, y/f);
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
  }).on('click', '.og-fullimg', function() {
    var photo_id = $(this).closest('li').data('image-id')
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

  var photoIdFromATag = function(a) {
    return $(a).attr('href').replace('/#', '');
  };
  $('.popular-photo').on('click', 'a', function(e) {
    e.preventDefault();
    var selectedPhotoId = photoIdFromATag(this);
    var photoIds = $('.popular-photo a').map(function(_, a) {
      return photoIdFromATag(a);
    }).toArray();

    loadInfoForPhotoIds(photoIds).done(function() {
      showExpanded(photoIds);
    }).fail(function() {
    });
  });
});
