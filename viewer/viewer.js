var markers = [];
var marker_icons = [];
var selected_marker_icons = [];
var marker_dates = [];
var map;
var start_date = new Date("1850/01/01");
var end_date = new Date("2000/01/01");

function el(id) {
  return document.getElementById(id);
}

var selected_marker = null;
var selected_icon = 0;

// Intended to be used as an img.onLoad handler.
function createSpinnerKiller(id) {
  return function() {
    el(id).style.backgroundImage = 'none';
  }
}

function displayInfoForLatLon(lat_lon, should_display, marker) {
  var recs = lat_lons[lat_lon];
  var photo_ids = [];
  for (var i = 0; i < recs.length; i++) {
    if (recs[i][0] >= start_date && recs[i][1] <= end_date) {
      photo_ids.push(recs[i][2]);
    }
  }

  var html = '';
  for (var i = 0; i < photo_ids.length; i++) {
    var photo_id = photo_ids[i];
    var thumb_id = 'thumb-' + photo_id;
    var img_path = 'http://sf-viewer.appspot.com/thumb/' + photo_id + '.jpg';
    var img = new Image();
    img.onload = createSpinnerKiller(thumb_id);
    img.src = img_path;

    html += '<div id="' + thumb_id + '" class="thumb">';
    html += '<img border=0 path="' + img_path + '" /></div>\n';
    html += '<div class="description" id="description-' + photo_id + '">';
    html += 'Loading&hellip;</div>\n';
    if (i != photo_ids.length - 1) html += '<hr/>'
  }
  el('carousel').scrollTop = 0;
  el('carousel').innerHTML = html;

  var zIndex = 0;
  if (selected_marker) {
    zIndex = selected_marker.getZIndex();
    selected_marker.setIcon(selected_icon);
  }
  selected_marker = marker;
  selected_icon = marker.getIcon();
  marker.setIcon(selected_marker_icons[photo_ids.length > 100 ? 100 : photo_ids.length]);
  marker.setZIndex(100000 + zIndex);

  getDescription(photo_ids, should_display);
  loadPictures();
}

function makeCallback(lat_lon, marker) {
  return function(e) {
    displayInfoForLatLon(lat_lon, true, marker);
  };
}

function getDescription(photo_ids, should_display) {
  var req = new XMLHttpRequest();
  var caller = this;
  req.onreadystatechange = function () {
    if (req.readyState == 4) {
      if (req.status == 200 ||  // Normal http
          req.status == 0) {    // Chrome w/ --allow-file-access-from-files
        var info_map = eval('(' + req.responseText + ')');
        if (should_display) {
          for (var i = 0; i < photo_ids.length; i++) {
            var id = photo_ids[i];
            var info = info_map[id];
            if (!el("description-" + id)) continue;
            el("description-" + id).innerHTML =
              info.title + '<br/>' +
              info.date + '<br/>';
            if (!el("thumb-" + id)) continue;
            el("thumb-" + id).innerHTML = 
                '<a href="javascript:showExpanded(\'' + id + '\')">' +
                el("thumb-" + id).innerHTML + '</a>';
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

  var latlng = new google.maps.LatLng(37.77493, -122.419416);
  var opts = {
    zoom: 13,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    streetViewControl: true
  };
  map = new google.maps.Map(el("map"), opts);

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

    // TODO(danvk): use timestamps?
    for (var i = 0; i < recs.length; i++) {
      recs[i][0] = new Date(recs[i][0] + '/01/01');
      recs[i][1] = new Date(recs[i][1] + '/12/31');
      total += 1;
    }

    if (lat_lon == init_lat_lon) init_marker = marker;
  }
  setCount(total);
  makeCallback(init_lat_lon, init_marker)();
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

function createSlider() {
  $('#slider').slider({
    range: true,
    values: [1850, 2000],
    min: 1850,
    max: 2000,
    slide: function(event, ui) {
      el("date_range").innerHTML = ui.values[0] + '&ndash;' + ui.values[1];
      date1 = ui.values[0];
      date2 = ui.values[1];
      updateVisibleMarkers(new Date(date1 + "/01/01"), new Date(date2 + "/12/31"));
    },
    change: function(event, ui) {
      // TODO(danvk): on slow browsers, the update should actually happen here
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
  var padding = 500;
  for (var i = 0; i < imgs.length; i++) {
    if (imgs[i].offsetTop - padding < bottom_edge && imgs[i].src == '') {
      imgs[i].src = imgs[i].getAttribute('path');
    }
  }
}

function showExpanded(id) {
  // There should be a way to center the div that's less hacky.
  var expanded = el('expanded');
  expanded.style.display = 'none';
  var map = el('map');
  var img = el('thumb-' + id).getElementsByTagName('img')[0];
  var div_width = 10 + 400.0 / img.height * img.width;
  var div_height = 80 + 400;

  expanded.style.left = map.offsetLeft + map.offsetWidth / 2 - div_width / 2 + 'px';
  expanded.style.top = map.offsetTop + map.offsetHeight / 2 - div_height / 2 + 'px';
  expanded.style.width = div_width + 'px';
  expanded.style.minHeight = div_height + 'px';

  var img = document.createElement('img');
  img.className = 'thumb';  // makes the spinner appear
  img.src = 'http://webbie1.sfpl.org/multimedia/sfphotos/' + id + '.jpg';
  img.width = div_width;
  img.height = 400;
  img.id = 'expanded-image';
  el('expanded-image-holder').innerHTML = '';
  el('expanded-image-holder').appendChild(img);

  var img_obj = new Image();
  img.onload = createSpinnerKiller(img.id);
  img_obj.src = img.src;

  el('expanded-desc').innerHTML = el('description-' + id).innerHTML;
  expanded.style.display = '';
  // TODO(danvk): add in library URL here.
}

function hideExpanded() {
  el('expanded').style.display = 'none';
}
