var markers = [];
var marker_icons = [];
var selected_marker_icons = [];
var marker_dates = [];
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
    return 'http://localhost:8001/thumb/' + photo_id + '.jpg';
    // return 'http://localhost:8001/milstein-thumb/' + photo_id + '.jpg';
    // return 'https://s3.amazonaws.com/oldnyc/thumb/' + photo_id + '.jpg';
  } else {
    return 'http://s3-us-west-1.amazonaws.com/oldsf/thumb/' + photo_id + '.jpg';
  }
}

function expandedImageUrl(photo_id) {
  if (isOldNycImage(photo_id)) {
    // return 'http://images.nypl.org/index.php?id=' + photo_id + '&t=w';
    return 'http://localhost:8001/600px/' + photo_id + '.jpg';
    // return 'http://localhost:8001/milstein-600/' + photo_id + '.jpg';
    // return 'https://s3.amazonaws.com/oldnyc/600px/' + photo_id + '.jpg';
  } else {
    return 'http://s3-us-west-1.amazonaws.com/oldsf/images/' + photo_id + '.jpg'
  }
}

// Intended to be used as an img.onLoad handler.
function spinnerKiller() {
  $(this).css('backgroundImage', 'none');
}

// The callback gets fired when the info for all lat/lons at this location
// become available (i.e. after the /info RPC returns).
function displayInfoForLatLon(recs, marker, opt_callback) {
  // var recs = lat_lons[lat_lon];
  var photo_ids = [];
  for (var i = 0; i < recs.length; i++) {
    if (recs[i][0] >= start_date && recs[i][1] <= end_date) {
      photo_ids.push(recs[i][2]);
    }
  }

  var thumb_panes = $.map(photo_ids, function(photo_id, idx) {
    var img_path = thumbnailImageUrl(photo_id);

    var $pane =
      $('#thumbnail-template')
      .clone()
      .removeAttr('id')
      .attr('photo_id', photo_id);

    $('img', $pane).attr('path', img_path);

    if (idx == photo_ids.length - 1) {
      $('hr', $pane).hide();
    }
    return $pane.get();
  });

  $('#carousel')
    .scrollTop(0)
    .empty()
    .append($(thumb_panes).show());

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

  loadInfoForPhotoIds(photo_ids, opt_callback);
  loadPictures();
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

  // This event fires when a pan/zoom operation has completed and the map is no
  // longer in motion. It reduces the number of URL parameter updates we do.
  // google.maps.event.addListener(map, 'idle', stateWasChanged);
  // ... but it's still annoying.


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
      fillOpacity: 0.25
    });

    polygon.setMap(map);
    polygons[neighborhood] = polygon;
    google.maps.event.addListener(polygon, 'click', (function(neighborhood) {
      return function() {
        displayInfoForLatLon(neighborhood_photos[neighborhood]);
        explodeNeighborhood(neighborhood);
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
}

// Hide a polygon and show markers for the locations in that neighborhood.
function explodeNeighborhood(neighborhood) {
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
  }

  polygons[neighborhood].setMap(null);  // hide the polygon
  $.each(markers, function(marker) {
    marker.setMap(map);
  });
}

// Hide all the markers for a neighborhood and show the polygon.
function collapseNeighborhood(neighborhood) {
}

  /*

  var total = 0;
  var init_marker = null;
  for (var lat_lon in lat_lons) {
    var ll = lat_lon.split(",");
    var recs = lat_lons[ll];
    marker = new google.maps.Marker({
      position: new google.maps.LatLng(parseFloat(ll[0]), parseFloat(ll[1])),
      map: map,
      flat: true,
      visible: true,
      icon: marker_icons[recs.length > 100 ? 100 : recs.length],
      title: lat_lon
    });
    markers.push(marker);
    google.maps.event.addListener(marker, 'click', makeCallback(ll, marker));
    // google.maps.event.addListener(marker, 'mouseover', makePreloadCallback(ll));

    total += recs.length;

    if (lat_lon == init_lat_lon) init_marker = marker;
  }

  if (location.hash) {
    setUIFromUrlHash();
  }
  if (!hashToState(location.hash).hasOwnProperty('ll')) {
    setCount(total);
    makeCallback(init_lat_lon, init_marker)();
  }
}
  */

function updateVisibleMarkers(date1, date2) {
  var total = 0;
  for (var i = 0; i < markers.length; i++) {
    var marker = markers[i];
    var ll = marker.getTitle();
    var vis = marker.getVisible();
    var icon = marker.getIcon();
    var count = 0;
    var recs = lat_lons[ll];
    for (var j = 0; j < recs.length; j++) {
      if (recs[j][0] >= date1 && recs[j][1] <= date2) count += 1;
    }
    if (count == 0) {
      if (vis) marker.setVisible(false);
    } else {
      total += count;
      if (!vis) marker.setVisible(true);
      var new_icon = marker_icons[count > 100 ? 100 : count];
      if (marker == selected_marker) {
        new_icon = selected_marker_icons[count > 100 ? 100 : count];
      }
      if (icon != new_icon) marker.setIcon(new_icon);
    }
  }
  start_date = date1;
  end_date = date2;
  setCount(total);
}

function setCount(total) {
  total += '';
  var rgx = /(\d+)(\d{3})/;
  while (rgx.test(total)) {
    total = total.replace(rgx, '$1' + ',' + '$2');
  }
  
  $('#count').html(total);
}

function slide(event, ui) {
  var dates = null
  if (typeof(ui) != 'undefined') {
    dates = ui.values;
  } else {
    dates = $('#slider').slider('values');
  }
  var date1 = dates[0];
  var date2 = dates[1];
  $('#date_range_years').html(date1 + '&ndash;' + date2);
  updateVisibleMarkers(date1, date2);
}

function createSlider() {
  $('#slider').slider({
    range: true,
    values: [1850, 2000],
    min: 1850,
    max: 2000,
    slide: slide,
    change: function(event, ui) {
      // TODO(danvk): on slow browsers, the update should actually happen here
      stateWasChanged();
    }
  });

  for (var year = 1850; year <= 2000; year += 10) {
    var pct = (year - 1850) / (2000 - 1850) * 100;
    var html = '<div class=tick style="left:' + pct + '%;"></div>';
    if (year % 50 == 0) {
      html += '<div class=tick_text style="left:' + pct + '%;">' + year + '</div>';
    }
    document.getElementById('slider_ticks').innerHTML += html;
  }
}

// The thumbnails div has scrolled or changed. Maybe we should load some
// pictures.
function loadPictures() {
  var $carousel = $('#carousel');

  var padding = 100;
  var bottom_edge = $carousel.scrollTop() + $carousel.height() + padding;
  $('#carousel img').each(function(i, imgEl) {
    var $img = $(imgEl);
    if ($img.offset().top < bottom_edge && !$img.attr('src')) {
      $img
        .attr('src', $img.attr('path'))
        .load(spinnerKiller);
    }
  });
}


// This creates the holder "pane" for an expanded image.
// The expanded image slideshow consists of many of these.
// id 
function buildHolder(photo_id, img_width, is_visible) {
  var info = infoForPhotoId(photo_id);
  var $holder = $('#expanded-image-holder-template').clone().removeAttr('id');
  $holder.find('img')
    .attr(is_visible ? 'src' : 'future-src', expandedImageUrl(photo_id))
    .attr('width', img_width)
    .load(spinnerKiller);

  $holder.find('.description')
    .css('max-width', img_width + 'px');

  fillPhotoPane(photo_id, $holder);
  return $holder;
}


// NOTE: This can only be called when the info for all photo_ids at the current
// position have been loaded (in particular the image widths).
function showExpanded(id) {
  $('#expanded').hide();

  var photo_ids =
    $('#rightpanel .thumbnail-pane')
    .map(function() { return $(this).attr('photo_id'); })
    .get();

  var selected_idx = 0;
  var expanded_images = $.map(photo_ids, function(photo_id, idx) {
    var info = infoForPhotoId(photo_id);
    var img_width = info.width;

    if (photo_id == id) {
      selected_idx = idx;
    }

    // TODO(danvk): show prev/next as well
    return buildHolder(photo_id, img_width, photo_id == id).get();
  });

  if (expanded_images.length > 1) {
    expanded_images.push($('<div class=expanded-right-gutter />').get(0));
  }

  $('#expanded-carousel ul')
    .empty()
    .append($(expanded_images).show());

  $('#expanded-carousel')
    .jcarousel({
      scroll: 1,
      center: true
    })

  $('#expanded').show();
  $('#expanded-carousel')
    .jcarousel('scroll', selected_idx, false /* no animation */);

  $(document).bind('keyup', function(e) {
    // handle cursor keys
    // TODO(danvk): hitting left/right quickly results in dropped scrolls.
    if (e.keyCode == 37) {
      scrollExpanded('-=1');  // go left
    } else if (e.keyCode == 39) {
      scrollExpanded('+=1');  // go right
    } else if (e.keyCode == 27) {  // escape
      hideExpanded();
    }
  });

  stateWasChanged();
}

function hideExpanded() {
  $('#expanded').hide();
  $('#expanded-carousel').jcarousel('destroy');
  $(document).unbind('keyup');
  stateWasChanged();
}

function scrollExpanded(target) {
  $('#expanded-carousel').jcarousel('scroll', target);
}

// This fills out details for either a thumbnail or the expanded image pane.
function fillPhotoPane(photo_id, $pane, opt_info) {
  // This could be either a thumbnail on the right-hand side or an expanded
  // image, front and center.
  $('.description', $pane).html(descriptionForPhotoId(photo_id));

  var info = opt_info || infoForPhotoId(photo_id);
  // TODO(danvk): this is kinda gross
  $('.thumb a', $pane)
      .attr('href', "javascript:showExpanded('" + photo_id + "')");
  $('.library-link', $pane)
    .attr('href', info.library_url);
  $pane.attr('photo_id', photo_id);
}

$(function() {
  $('#curtains').click(hideExpanded);

  $('#expanded-carousel')
    .delegate('li', 'itemtargetin.jcarousel', function(event, carousel) {
      // Load the next/previous images.
      // "this" refers to the item element
      // "carousel" is the jCarousel instance
      var els = $('#expanded-carousel li');
      var this_idx = $(els).index(this);
      if (this_idx == -1) throw 'eh?';
      for (var i = -1; i < 2; i++) {
        if (!els[this_idx + i]) continue;
        var $el = $(els[this_idx + i]);
        var $img = $el.find('img');
        if (!$img.attr('src')) {
          $img
            .attr('src', $img.attr('future-src'))
            .removeAttr('future-src');
        }
      }
    })
    .delegate('li', 'itemtargetin.jcarousel', function(event, carousel) {
      // Set a "current" class on the target element but no others.
      $('#expanded-carousel li').removeClass('current');
      $(this).addClass('current');
      stateWasChanged();
    });
  $('#expanded-carousel').on('scroll.jcarousel', function(event, carousel, target, animate) {
    // Why does $(carousel) not work here? It gives initialization errors.
    var $carousel = $('#expanded-carousel');

    // Drop attempts to scroll to the right-most element in multi-element lists.
    // This is a "fake" element which is added to help with centering.
    if (target == '+=1') {
      var $items = $carousel.jcarousel('items');
      var idx = $items.index($carousel.jcarousel('target'));
      if (idx == $items.length - 2) {
        return false;
      }
    }

    return true;
  });

  $('#date_range').click(function(e) {
    e.preventDefault();
    $('#slider-container').toggle();
  });

  // $('#expanded-carousel')
  //   .delegate('img', 'load', function() {
  //   });
});
