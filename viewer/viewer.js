var markers = [];
var marker_icons = [];
var selected_marker_icons = [];
var marker_dates = [];
var map;
var start_date = 1850;
var end_date = 2000;

// Intended to be used as an img.onLoad handler.
function spinnerKiller() {
  $(this).css('backgroundImage', 'none');
}

function displayInfoForLatLon(lat_lon, marker) {
  var recs = lat_lons[lat_lon];
  var photo_ids = [];
  for (var i = 0; i < recs.length; i++) {
    if (recs[i][0] >= start_date && recs[i][1] <= end_date) {
      photo_ids.push(recs[i][2]);
    }
  }

  var thumb_panes = $.map(photo_ids, function(photo_id, idx) {
    var thumb_id = 'thumb-' + photo_id;
    //var img_path = 'http://sf-viewer.appspot.com/thumb/' + photo_id + '.jpg';
    var img_path = 'http://s3-us-west-1.amazonaws.com/oldsf/thumb/' + photo_id + '.jpg';

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
  selected_marker = marker;
  selected_icon = marker.getIcon();
  marker.setIcon(selected_marker_icons[photo_ids.length > 100 ? 100 : photo_ids.length]);
  marker.setZIndex(100000 + zIndex);

  loadInfoForPhotoIds(photo_ids);
  loadPictures();
  updateHash();
}

// TODO(danvk): possible to just use the event?
function makeCallback(lat_lon, marker) {
  return function(e) {
    displayInfoForLatLon(lat_lon, marker);
  };
}

function initialize_map() {
  // Give them something to look at while the map loads:
  init_lat_lon = "37.771393,-122.428618";

  var latlng = new google.maps.LatLng(37.79216, -122.41753);
  var opts = {
    zoom: 14,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    streetViewControl: true,
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
  
  map = new google.maps.Map($('#map').get(), opts);
  //google.maps.event.addListener(map, 'center_changed', updateHash);
  //google.maps.event.addListener(map, 'zoom_changed', updateHash);

  // Create markers for each number.
  marker_icons.push(null);  // it's easier to be 1-based.
  selected_marker_icons.push(null);
  for (var i = 0; i < 100; i++) {
    var num = i + 1;
    var size = (num == 1 ? 9 : (num < 10 ? 13 : (num < 100 ? 25 : 39)));
    marker_icons.push(new google.maps.MarkerImage(
      'dots/sprite.png',
      new google.maps.Size(size, size),
      new google.maps.Point((i%10)*39, Math.floor(i/10)*39),
      new google.maps.Point((size - 1) / 2, (size - 1)/2)
    ));
    selected_marker_icons.push(new google.maps.MarkerImage(
      'dots/selected-sprite.png',
      new google.maps.Size(size, size),
      new google.maps.Point((i%10)*39, Math.floor(i/10)*39),
      new google.maps.Point((size - 1) / 2, (size - 1)/2)
    ));
  }

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
    loadFromHash();
  }

  if (!stateFromHash().hasOwnProperty('ll')) {
    setCount(total);
    makeCallback(init_lat_lon, init_marker)();
  }
}

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
  $('#date_range').html(date1 + '&ndash;' + date2);
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
      updateHash();
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

  // var carousel = el('carousel');
  // var imgs = carousel.getElementsByTagName('img');
  // var bottom_edge = carousel.scrollTop + carousel.offsetHeight;
  var bottom_edge = $carousel.scrollTop() + $carousel.height();
  var padding = 100;
  $('#carousel img').each(function(i, imgEl) {
    var $img = $(imgEl);
    if ($img.offset().top - padding < bottom_edge &&
        !$img.attr('src')) {
      var thumb_id = $img.parent().attr('photo_id');
      var img_path = $img.attr('path');

      // can probably use jQuery to fix this.
      var img = new Image();
      img.onload = spinnerKiller;
      img.src = img_path;
      $img.attr('src', img_path);
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
    .attr(is_visible ? 'src' : 'future-src',
        'http://s3-us-west-1.amazonaws.com/oldsf/images/' + photo_id + '.jpg')
    .attr('width', img_width)
    .load(spinnerKiller);

  fillPhotoPane(photo_id, $holder);
  return $holder;
}


function showExpanded(id) {
  $('#expanded').hide();

  var photo_ids =
    $('#rightpanel .thumbnail-pane')
    .map(function() { return $(this).attr('photo_id'); })
    .get();

  var selected_idx = 0;
  var expanded_images = $.map(photo_ids, function(photo_id, idx) {
    var $thumb_img = $('#thumb-' + photo_id + ' img');
    var img_width = 400.0 / $thumb_img.height() * $thumb_img.width();

    if (photo_id == id) selected_idx = idx;

    // TODO(danvk): show prev/next as well
    return buildHolder(photo_id, img_width, photo_id == id).get();
  });

  /*
  var twitter = document.createElement('div');
  twitter.id = 'expanded-twitter';
  twitter.innerHTML = el('twitter').innerHTML;
  el('expanded-image-holder').appendChild(twitter);
  */

  $('#expanded-carousel ul')
    .empty()
    .append($(expanded_images).show());

  $('#expanded-carousel')
    .jcarousel({
      scroll: 1,
      center: true
    })

  $('#expanded').show();
  expanded_photo_id = id;
  $('#expanded-carousel')
    .jcarousel('scroll', selected_idx, false /* no animation */);

  $(document).bind('keyup', function(e) {
    // handle cursor keys
    // TODO(danvk): hitting left/right quickly results in dropped scrolls.
    if (event.keyCode == 37) {
      scrollExpanded('-=1');  // go left
    } else if (event.keyCode == 39) {
      scrollExpanded('+=1');  // go right
    }
  });

  updateHash();
}

function hideExpanded() {
  $('#expanded').hide();
  $(document).unbind('keyup');
  updateHash();
}

function scrollExpanded(target) {
  $('#expanded-carousel')
    .jcarousel('scroll', target);
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
}

$(function() {
  $('#curtains').click(hideExpanded);

  $('#expanded-carousel')
    .delegate('li', 'itemtargetin.jcarousel', function(event, carousel) {
      // "this" refers to the item element
      // "carousel" is the jCarousel instance
      // If the image element has zero width, then let's correct that.
      var els = $('#expanded-carousel li');
      var this_idx = $(els).index(this);
      if (this_idx == -1) throw 'eh?';
      for (var i = 0; i < 2; i++) {
        if (!els[this_idx + i]) continue;
        var $img = $(els[this_idx + i]).find('img');
        if (!$img.attr('src')) {
          $img
            .attr('src', $img.attr('future-src'))
            .removeAttr('future-src');
        }
        if ($img.width() == 0) {
          $img.attr('width', null);
        }
      }
    })
    .delegate('li', 'itemtargetin.jcarousel', function(event, carousel) {
      // Set a "current" class on the target element but no others.
      $('#expanded-carousel li').removeClass('current');
      $(this).addClass('current');
    });
});
