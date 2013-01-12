var markers = [];
var marker_icons = [];
var selected_marker_icons = [];
var marker_dates = [];
var map;
var start_date = 1850;
var end_date = 2000;

function el(id) {
  return document.getElementById(id);
}

var selected_marker = null;
var selected_icon = 0;
var expanded_photo_id = null;

// There are four bits of state:
// 1. Selected date range
// 2. Selected dot
// 3. Expanded image
// 4. Map position
function currentState() {
  var years = $('#slider').slider('values');
  if (years[0] == 1850 && years[1] == 2000) years = null;
  var selected_lat_lon = selected_marker ? selected_marker.title : null;
  if (selected_lat_lon == init_lat_lon) selected_lat_lon = null;
  var expanded = null;
  if (el('expanded').style.display != 'none') {
    expanded = expanded_photo_id + ',' + el('expanded-image').width;
  }

  var center = map.getCenter();
  var map_state = center.lat().toFixed(5) + ',' + center.lng().toFixed(5) + ',' + map.getZoom();
  if (map_state == '37.79216,-122.41753,14') map_state = null;

  var state = {};
  if (years) state.y = years[0] + '-' + years[1];
  if (selected_lat_lon) state.ll = selected_lat_lon;
  if (expanded) state.e = expanded;
  if (map_state) state.m = map_state;
  return state;
}

var block_update = false;  // used when loading from a hash
var current_hash = null;
function updateHash() {
  if (block_update) return;
  var state = currentState();
  var hash = '';
  for (var k in state) {
    if (hash) hash += ',';
    hash += k + ':' + state[k].replace(/,/g, '|');
  }
  current_hash = hash;
  location.hash = hash;
}

function stateFromHash() {
  if (!location.hash) return {};

  var hash = '' + location.hash;
  if (hash.indexOf('%7') >= 0) {
    // twitter links come through as 'foo%7Cbar', not 'foo|bar'.
    hash = unescape(hash);
  }

  var parts = hash.substr(1).split(',');
  var state = {};
  for (var i = 0; i < parts.length; i++) {
    var kv = parts[i].split(':');
    var v = kv[1];
    if (v.indexOf('|') != -1) v = v.split('|');
    state[kv[0]] = v;
  }
  return state;
}

function loadFromHash() {
  var state = stateFromHash();
  block_update = true;
  if (state.hasOwnProperty('m')) {
    var ll = new google.maps.LatLng(parseFloat(state.m[0]), parseFloat(state.m[1]));
    var zoom = parseInt(state.m[2]);
    map.setCenter(ll);
    map.setZoom(parseInt(zoom));
  }
  if (state.hasOwnProperty('y')) {
    var ys = state.y.split('-');
    ys = [parseInt(ys[0]), parseInt(ys[1])];
    $('#slider').slider('values', ys);
    slide();
  }
  if (state.hasOwnProperty('ll')) {
    var marker = null;
    for (var i = 0; i < markers.length; i++) {
      if (markers[i].title == state.ll) {
        marker = markers[i];
        break;
      }
    }
    if (marker) {
      displayInfoForLatLon(state.ll, marker);
    }
  }
  if (state.hasOwnProperty('e')) {
    var id = state.e[0];
    var w = parseInt(state.e[1]);
    showExpanded(id, w);
  }
  block_update = false;
}

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

    $pane.find('.thumb').attr('id', thumb_id);
    $pane.find('img').attr('path', img_path);
    $pane.find('.description').attr('id', 'description-' + photo_id);
    $pane.find('.library-link').attr('id', 'library_url-' + photo_id);

    if (idx == photo_ids.length - 1) {
      $pane.find('hr').hide();
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

  getDescription(photo_ids);
  loadPictures();
  updateHash();
}

function makeCallback(lat_lon, marker) {
  return function(e) {
    displayInfoForLatLon(lat_lon, marker);
  };
}

function getDescription(photo_ids) {
  var req = new XMLHttpRequest();
  var caller = this;
  req.onreadystatechange = function () {
    if (req.readyState == 4) {
      if (req.status == 200 ||  // Normal http
          req.status == 0) {    // Chrome w/ --allow-file-access-from-files
        var info_map = eval('(' + req.responseText + ')');

        for (var i = 0; i < photo_ids.length; i++) {
          var id = photo_ids[i];
          var info = info_map[id];
          var html = info.title + '<br/>' + info.date;

          if (el("description-" + id)) {
            el("description-" + id).innerHTML = html;
            if (!el("thumb-" + id)) continue;
            el("thumb-" + id).innerHTML = 
                '<a href="javascript:showExpanded(\'' + id + '\')">' +
                el("thumb-" + id).innerHTML + '</a>';
          }

          var library_html =
              '<a target=_blank href="' + info.library_url + '">&rarr; Library</a>';
          if (el("library_url-" + id)) {
            el("library_url-" + id).innerHTML = library_html;
          }

          if (el("expanded-desc-" + id)) {
            el("expanded-desc-" + id).innerHTML = html;
          }
          if (el("expanded-library_url-" + id)) {
            el("expanded-library_url-" + id).innerHTML = library_html;
          }
        }
      }
    }
  };

  var url = '/info';
  var data = ''
  for (var i = 0; i < photo_ids.length; i++) {
    data += (i ? '&' : '') + 'id=' + photo_ids[i];
  }

  req.open("POST", url, true);
  req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  req.send(data);
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
  
  map = new google.maps.Map(el("map"), opts);
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
  
  el("count").innerHTML = total;
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
  el("date_range").innerHTML = date1 + '&ndash;' + date2;
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

// The thumbnails div has scrolled or changed. Maybe we should load some pictures.
function loadPictures() {
  var carousel = el('carousel');
  var imgs = carousel.getElementsByTagName('img');
  var bottom_edge = carousel.scrollTop + carousel.offsetHeight;
  var padding = 100;
  for (var i = 0; i < imgs.length; i++) {
    if (imgs[i].offsetTop - padding < bottom_edge && imgs[i].src == '') {
      var thumb_id = imgs[i].parentNode.id;
      var img_path = imgs[i].getAttribute('path');

      var img = new Image();
      img.onload = spinnerKiller;
      img.src = img_path;
      imgs[i].src = img_path;
    }
  }
}


function buildHolder(id, img_width) {
  var $holder = $('#expanded-image-holder-template').clone().removeAttr('id');
  $holder.find('img')
    .attr('src',
        'http://s3-us-west-1.amazonaws.com/oldsf/images/' + id + '.jpg')
    .attr('width', img_width)
    .load(spinnerKiller);

  // TODO(danvk): get rid of this use of IDs.
  $holder.find('.description')
    .html(el('description-' + id).innerHTML)
    .attr('id', 'expanded-desc-' + id);

  $holder.find('.library-link')
    .attr('id', 'expanded-library_url-' + id)
    .html(el('library_url-' + id).innerHTML);

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

    return buildHolder(photo_id, img_width).get();
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
      // initCallback: mycarousel_initCallback,
      // This tells jCarousel NOT to autobuild prev/next buttons
      // buttonNextHTML: null,
      // buttonPrevHTML: null
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
  el('expanded').style.display = 'none';
  $(document).unbind('keyup');
  updateHash();
}

function scrollExpanded(target) {
  $('#expanded-carousel')
    .jcarousel('scroll', target);
}

function killSplash() {
  el('backdrop').style.display = 'none';
}

/* From quirksmode */
function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else var expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}


// This enables pasting hashed URLs
$(window).hashchange(function(){
  if (current_hash == location.hash.substr(1)) return;
  loadFromHash();
});

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
        var $img = $(els[this_idx + i]).find('img');
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
