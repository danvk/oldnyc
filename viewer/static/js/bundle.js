// Styles for Google Maps. These de-emphasize features on the map.
var MAP_STYLE = [
    // to remove buildings
    {"stylers": [ {"visibility": "off" } ] },
    {"featureType": "water","stylers": [{"visibility": "simplified"} ] },
    {"featureType": "poi","stylers": [ {"visibility": "simplified"} ]},
    {"featureType": "transit","stylers": [{ "visibility": "off"}] },
    { "featureType": "landscape","stylers": [ { "visibility": "simplified" } ] },
    { "featureType": "road", "stylers": [{ "visibility": "simplified" } ] },
    { "featureType": "administrative",  "stylers": [{ "visibility": "simplified" } ] },
    // end remove buildings
    {
        "featureType": "administrative",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative.country",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative.province",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#e3e3e3"
            }
        ]
    },
    {
        "featureType": "landscape.natural",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "all",
        "stylers": [
            {
                "color": "#cccccc"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#FFFFFF"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "labels",
        "stylers": [
            {
                "color": "#94989C"
            },
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    }
];

function buildStaticStyle(styleStruct) {
  var style = "";
  for(var i = 0; i < styleStruct.length;i++){
    s = styleStruct[i];
    strs = [];
    if (s.featureType != null) strs.push( "feature:" + s.featureType );
    if (s.elementType != null) strs.push( "element:" + s.elementType );
    if (s.stylers != null) {
      for (var j=0;j<s.stylers.length;j++) {
        for (var key in s.stylers[j]){
          strs.push( key + ":" + s.stylers[j][key].replace(/#/, '0x') );
        }
      }
    }
    var str = "&style=" + strs.join("%7C");
    style += str;
  }
  return style;
}

var STATIC_MAP_STYLE = buildStaticStyle(MAP_STYLE);
var popular_photos = [{"date": "1910", "loc": "42nd & 5th ave", "height": 249, "id": "708760f-a", "desc": "Street scene"}, {"date": "1936", "loc": "42nd & 5th ave", "height": 145, "id": "1508783-a", "desc": "Directing traffic and trolley"}, {"date": "1912", "loc": "42nd & 5th ave", "height": 157, "id": "708795f-a", "desc": "Ground level view of street"}, {"date": "1913", "loc": "42nd & 5th ave", "height": 159, "id": "712987f-a", "desc": "Street scene"}, {"date": "1928", "loc": "42nd & 6th Avenue", "height": 246, "id": "713050f-a", "desc": "Street scene"}, {"date": "1933", "loc": "42nd & 6th Avenue", "height": 130, "id": "713043f", "desc": "Under the elevated"}, {"date": "1939", "loc": "42nd & 6th Avenue", "height": 159, "id": "709480f-a", "desc": "Elevated train demolition"}, {"date": "1930s", "loc": "42nd & 6th Avenue", "height": 198, "id": "1558013", "desc": "Street scene"}, {"date": "1936", "loc": "Central Park", "height": 160, "id": "730166f-a", "desc": "Aerial view"}, {"date": "1933", "loc": "Central Park", "height": 133, "id": "718268f-b", "desc": "Roller skating"}, {"date": "1938", "loc": "Central Park", "height": 229, "id": "718346f-a", "desc": "Feeding birds"}, {"date": "", "loc": "Central Park", "height": 298, "id": "718282f-a", "desc": "On the lake"}, {"date": "", "loc": "Central Park", "height": 160, "id": "718194f-a", "desc": "Riding under an arch"}, {"date": "1905", "loc": "Central Park", "height": 154, "id": "718242f-b", "desc": "Ice skaters"}, {"date": "", "loc": "Central Park", "height": 143, "id": "718333f-a", "desc": "Playing croquet"}, {"date": "", "loc": "Central Park", "height": 132, "id": "718280f-a", "desc": "Quiet corner"}, {"date": "1892", "loc": "Central Park", "height": 158, "id": "718272f-a", "desc": "Strolling"}, {"date": "1933", "loc": "Central Park", "height": 133, "id": "718179f-b", "desc": "Aerial View"}, {"date": "1913", "loc": "Central Park", "height": 130, "id": "718284f", "desc": "Schoolboys drilling"}, {"date": "1926", "loc": "Prospect Park", "height": 172, "id": "706346f-a", "desc": "Prospect Park Plaza"}, {"date": "1880", "loc": "Prospect Park", "height": 116, "id": "706348f-b", "desc": "Lake view"}, {"date": "1864", "loc": "Central Park", "height": 168, "id": "718385f-a", "desc": "Rustic arbor"}, {"date": "1892", "loc": "Central Park", "height": 164, "id": "718262f-a", "desc": "Fountain"}, {"date": "1933", "loc": "Roosevelt Island", "height": 158, "id": "732193f-a", "desc": "Welfare (Roosevelt) Island"}, {"date": "1934", "loc": "Brooklyn Bridge", "height": 134, "id": "730718f-c", "desc": "Aerial View"}, {"date": "1932", "loc": "86th & 3rd", "height": 130, "id": "714705f-a", "desc": "Storefronts"}, {"date": "1926", "loc": "Colonial & Nassau", "height": 154, "id": "726358f-c", "desc": "Family on porch"}, {"date": "1939", "loc": "Duane & West", "height": 136, "id": "719363f-a", "desc": "Horse-drawn cart"}, {"date": "1929", "loc": "Weehawken & Christopher", "height": 134, "id": "724321f-b", "desc": "Coca-Cola ad"}, {"date": "", "loc": "George Washington Bridge", "height": 156, "id": "1558509", "desc": ""}, {"date": "1906", "loc": "Bayard & Chrystie", "height": 159, "id": "716608f-a", "desc": "Street scene"}, {"date": "1931", "loc": "5th & 46th", "height": 159, "id": "708851f-a", "desc": "Street scene"}, {"date": "1933", "loc": "Columbus Circle", "height": 155, "id": "719145f-a", "desc": "Tribute to Columbus"}, {"date": "1910", "loc": "Pelham Parkway", "height": 146, "id": "701498f-b", "desc": "At the racetrack"}, {"date": "1936", "loc": "9th & 40th", "height": 129, "id": "732438f-b", "desc": "Food vendors"}, {"date": "1911", "loc": "Poppy Joe Island Beach", "height": 160, "id": "730622f-a", "desc": "Local muskrat hunters"}, {"date": "1890", "loc": "Wallabout Bay", "height": 102, "id": "734085f-a", "desc": "Ship in port"}, {"date": "1933", "loc": "Greenwich Village", "height": 299, "id": "730568f-a", "desc": "Art Exhibit"}, {"date": "1936", "loc": "Battery Park", "height": 134, "id": "716520f-c", "desc": "Aerial view"}, {"date": "1921", "loc": "New Chambers & Madison", "height": 141, "id": "721912f-b", "desc": "Cobblestone"}, {"date": "1918", "loc": "5th & 25th", "height": 242, "id": "731285f-a", "desc": "Victory Arch"}, {"date": "1925", "loc": "Minetta & MacDougal", "height": 168, "id": "721650f-a", "desc": "Alley"}, {"date": "1932", "loc": "Canal & Chrystie", "height": 169, "id": "718806f-a", "desc": "Construction of Sarah Delano Roosevelt Park"}, {"date": "1933", "loc": "Hudson Street", "height": 299, "id": "733360f-c", "desc": "Thanksgiving ragamuffins"}, {"date": "1917", "loc": "Queensborough Bridge", "height": 157, "id": "730942f-a", "desc": "Construction"}, {"date": "1903", "loc": "Williamsburg Bridge", "height": 129, "id": "731081f", "desc": "Under construction"}, {"date": "1890", "loc": "Mott & Park", "height": 177, "id": "721756f-a", "desc": "Street scene"}, {"date": "1900", "loc": "Broad St & Wall St", "height": 159, "id": "716841f-a", "desc": "Street scene"}, {"date": "1873", "loc": "Brooklyn Bridge", "height": 153, "id": "730663f-a", "desc": "Under construction; view of Manhattan"}, {"date": "1879", "loc": "Brooklyn Bridge", "height": 254, "id": "730665f-a", "desc": "Under construction; view of Manhattan"}, {"date": "1939", "loc": "Coney Island", "height": 129, "id": "731939f", "desc": "Beach scene"}, {"date": "1922", "loc": "Queens", "height": 152, "id": "725900f-a", "desc": "Country house (now JFK airport)"}, {"date": "1901", "loc": "Broadway & 34th", "height": 156, "id": "717404f-a", "desc": "Street scene with muddy road"}, {"date": "1921", "loc": "Broadway & 34th", "height": 158, "id": "1558433", "desc": "View of street scene from elevated tracks"}];
// The URL looks like one of these:
// /
// /#photo_id
// /#g:lat,lon
// /#photo_id,g:lat,lon

// Returns {photo_id:string, g:string}
function getCurrentStateObject() {
  if (!$('#expanded').is(':visible')) {
    return {};
  }
  var g = $('#expanded').data('grid-key');
  var selectedId = $('#grid-container').expandableGrid('selectedId');

  return selectedId ? { photo_id: selectedId, g: g } : { g: g };
}

// Converts the string after '#' in a URL into a state object,
// {photo_id:string, g:string}
// This is asynchronous because it may need to fetch ID->lat/lon info.
function hashToStateObject(hash, cb) {
  var m = hash.match(/(.*),g:(.*)/);
  if (m) {
    cb({photo_id: m[1], g: m[2]});
  } else if (hash.substr(0, 2) == 'g:') {
    cb({g: hash.substr(2)});
  } else if (hash.length > 0) {
    var photo_id = hash;
    findLatLonForPhoto(photo_id, function(g) {
      cb({photo_id: hash, g: g});
    });
  } else {
    cb({});
  }
}

function stateObjectToHash(state) {
  if (state.photo_id) {
    if (state.g == 'pop') {
      return state.photo_id + ',g:pop';
    } else {
      return state.photo_id;
    }
  }

  if (state.g) {
    return 'g:' + state.g;
  }
  return '';
}

// Change whatever is currently displayed to reflect the state in obj.
// This change may happen asynchronously.
// This won't affect the URL hash.
function transitionToStateObject(targetState) {
  var currentState = getCurrentStateObject();

  // This normalizes the state, i.e. adds a 'g' field to if it's implied.
  // (it also strips out extraneous fields)
  hashToStateObject(stateObjectToHash(targetState), function(state) {
    if (JSON.stringify(currentState) == JSON.stringify(state)) {
      return;  // nothing to do.
    }

    // Reset to map view.
    if (JSON.stringify(state) == '{}') {
      hideAbout();
      hideExpanded();
    }

    // Show a different grid?
    if (currentState.g != state.g) {
      var lat_lon = state.g;
      var count = lat_lons[lat_lon];
      if (state.g == 'pop') {
        count = getPopularPhotoIds().length;
      } else {
        // Highlight the marker, creating it if necessary.
        var marker = lat_lon_to_marker[lat_lon];
        var latLng = parseLatLon(lat_lon);
        if (!marker) {
          marker = createMarker(lat_lon, latLng);
        }
        if (marker) {
          selectMarker(marker, count);
          if (!map.getBounds().contains(latLng)) {
            map.panTo(latLng);
          }
        }
      }
      loadInfoForLatLon(lat_lon).done(function(photo_ids) {
        showExpanded(state.g, photo_ids, state.photo_id);
      });
      return;
    }

    if (currentState.photo_id && !state.photo_id) {
      // Hide the selected photo
      $('#grid-container').expandableGrid('deselect');
    } else {
      // Show a different photo
      $('#grid-container').expandableGrid('select', state.photo_id);
    }
  });
}


function findLatLonForPhoto(photo_id, cb) {
  var id4 = photo_id.slice(0, 4);
  $.ajax({
    dataType: "json",
    url: 'http://oldnyc.github.io/id4-to-location/' + id4 + '.json',
    success: function(id_to_latlon) {
      cb(id_to_latlon[photo_id])
    }
  });
}
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
function getCanonicalUrlForPhoto(photo_id) {
  var base_url = document.location.href.replace(/#[^#]*/, '') + '#';
  return base_url + photo_id;
}

function getCommentCount(photo_ids) {
  // There is a batch API:
  // https://developers.facebook.com/docs/graph-api/making-multiple-requests/
  return $.get('https://graph.facebook.com/', {
      'ids': $.map(photo_ids, function(id) {
          return getCanonicalUrlForPhoto(id);
      }).join(',')
  }).then(function(obj) {
    // obj is something like {url: {'id', 'shares', 'comments'}}
    // convert it to {id: comments}
    var newObj = {};
    $.each(obj, function(url, data) {
      newObj[url.replace(/.*#/, '')] = data['comments'] || 0;
    });
    return newObj;
  });
}
var markers = [];
var marker_icons = [];
var lat_lon_to_marker = {};
var selected_marker_icons = [];
var selected_marker, selected_icon;
var map;
var start_date = 1850;
var end_date = 2000;

var mapPromise = $.Deferred();

function thumbnailImageUrl(photo_id) {
  return 'http://oldnyc-assets.nypl.org/thumb/' + photo_id + '.jpg';
}

function expandedImageUrl(photo_id) {
  return 'http://oldnyc-assets.nypl.org/600px/' + photo_id + '.jpg';
}

// lat_lon is a "lat,lon" string.
function makeStaticMapsUrl(lat_lon) {
  url = 'http://maps.googleapis.com/maps/api/staticmap?center=' + lat_lon + '&zoom=15&size=150x150&maptype=roadmap&markers=color:red%7C' + lat_lon + '&style=' + STATIC_MAP_STYLE;
  return url;
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
  selectMarker(marker, lat_lons[lat_lon]);

  loadInfoForLatLon(lat_lon).done(function(photoIds) {
    var selectedId = null;
    if (photoIds.length <= 10) {
      selectedId = photoIds[0];
    }
    showExpanded(lat_lon, photoIds, selectedId);
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
    styles: MAP_STYLE
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
      'images/sprite-2014-08-29.png',
      new google.maps.Size(size, size),
      new google.maps.Point((i%10)*39, Math.floor(i/10)*39),
      new google.maps.Point((size - 1) / 2, (size - 1)/2)
    ));
    selected_marker_icons.push(new google.maps.MarkerImage(
      'images/selected-2014-08-29.png',
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
  var count = lat_lons[lat_lon];
  var marker = new google.maps.Marker({
    position: latLng,
    map: map,
    flat: true,
    visible: true,
    icon: marker_icons[Math.min(count, 100)],
    title: lat_lon
  });
  markers.push(marker);
  lat_lon_to_marker[lat_lon] = marker;
  google.maps.event.addListener(marker, 'click', handleClick);
  // trying to debug the friggin marker
  // google.maps.event.addListener(marker, "rightclick", function(event) {
  //   console.log(event);
  // });
  return marker;
}


// NOTE: This can only be called when the info for all photo_ids at the current
// position have been loaded (in particular the image widths).
// key is used to construct URL fragments.
function showExpanded(key, photo_ids, opt_selected_id) {
  hideAbout();
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

  // OCR'd text
  if (info.text) {
    $pane.find('.text').text(info.text);
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
        via: 'Old_NYC @NYPL'
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
  $(popularPhotos).appear({force_process:true});
  $('#popular').on('appear', '.popular-photo', function() {
    var $img = $(this).find('img[data-src]');
    loadDeferredImage($img.get(0));
  });
}

function loadDeferredImage(img) {
  var $img = $(img);
  if ($img.attr('src')) return;
  $(img)
    .attr('src', $(img).attr('data-src'))
    .removeAttr('data-src');
}

function hidePopular() {
  $('#popular').hide();
  $('.popular-link').show();
}
function showPopular() {
  $('#popular').show();
  $('.popular-link').hide();
  $('#popular').appear({force_process: true});
}

function showAbout() {
  hideExpanded();
  $('#about-page').show();
  // Hack! There's probably a way to do this with CSS
  var $container = $('#about-page .container');
  var w = $container.width();
  var mw = parseInt($container.css('max-width'), 0);
  if (w < mw) {
    $container.css('margin-left', '-' + (w / 2) + 'px');
  }
}
function hideAbout() {
  $('#about-page').hide();
}

function sendFeedback(photo_id, feedback_obj) {
  ga('send', 'event', 'link', 'feedback', { 'page': '/#' + photo_id });
  return $.ajax('/rec_feedback', {
    data: { 'id': photo_id, 'feedback': JSON.stringify(feedback_obj) },
    method: 'post'
  }).fail(function() {
    console.warn('Unable to send feedback on', photo_id)
  });
}

function deleteCookie(name) {
  document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function setCookie(name, value) {
  document.cookie = name + "=" + value + "; path=/";
}

$(function() {
  // Clicks on the background or "exit" button should leave the slideshow.
  $(document).on('click', '#expanded .curtains, #expanded .exit', function() {
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

    $(div).parent().find('.og-details-left').empty().append(
        $('#image-details-left-template').clone().removeAttr('id').show());

    var g = $('#expanded').data('grid-key');
    if (g == 'pop') {
      updateStaticMapsUrl(id);
    }
  })
  .on('click', '.og-fullimg > img', function() {
    var photo_id = $('#grid-container').expandableGrid('selectedId');
    window.open(libraryUrlForPhotoId(photo_id), '_blank');
  });

  $('#grid-container').on('click', '.rotate-image-button', function(e) {
    e.preventDefault();
    var $img = $(this).closest('li').find('.og-fullimg > img');
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
  }).on('click', '.feedback-button', function(e) {
    e.preventDefault();
    $('#grid-container .details').fadeOut();
    $('#grid-container .feedback').fadeIn();
  }).on('click', 'a.back', function(e) {
    e.preventDefault();
    $('#grid-container .feedback').fadeOut();
    $('#grid-container .details').fadeIn();
  });
  $(document).on('keyup', 'input, textarea', function(e) { e.stopPropagation(); });

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

    loadInfoForLatLon('pop').done(function(photoIds) {
      showExpanded('pop', photoIds, selectedPhotoId);
      $(window).trigger('showGrid', 'pop');
      $(window).trigger('openPreviewPanel');
      $(window).trigger('showPhotoPreview', selectedPhotoId);
    }).fail(function() {
    });
  });

  // ... it's annoying that we have to do this. jquery.appear.js should work!
  $('#popular').on('scroll', function() {
    $(this).appear({force_process: true});
  });

  // Show/hide popular images
  $('#popular .close').on('click', function() {
    setCookie('nopop', '1');
    hidePopular();
  });
  $('.popular-link a').on('click', function(e) {
    showPopular();
    deleteCookie('nopop');
    e.preventDefault();
  });
  if (document.cookie.indexOf('nopop=') >= 0) {
    hidePopular();
  }

  // Display the about page on top of the map.
  $('#about a').on('click', function(e) {
    e.preventDefault();
    showAbout();
  });
  $('#about-page .curtains, #about-page .exit').on('click', function(e) {
    hideAbout();
  });

  // Record feedback on images. Can have a parameter or not.
  var thanks = function(button) {
    return function() { $(button).text('Thanks!'); };
  };
  $('#grid-container').on('click', '.feedback button[feedback]', function() {
    var $button = $(this);
    var value = true;
    if ($button.attr('feedback-param')) {
      var $input = $button.siblings('input, textarea');
      value = $input.val();
      if (value == '') return;
      $input.prop('disabled', true);
    }
    $button.prop('disabled', true);
    var photo_id = $('#grid-container').expandableGrid('selectedId');
    var obj = {}; obj[$button.attr('feedback')] = value;
    sendFeedback(photo_id, obj).then(thanks($button.get(0)));
  });

  $('#grid-container').on('og-select', 'li', function() {
    var photo_id = $(this).data('image-id')
    $(window).trigger('showPhotoPreview', photo_id);
  }).on('og-deselect', function() {
    $(window).trigger('closePreviewPanel');
  }).on('og-openpreview', function() {
    $(window).trigger('openPreviewPanel');
  });
});
// History management service.
// Consider using this instead: https://github.com/browserstate/history.js
var History = function(hashToStateAdapter) {
  this.states = [];
  this.hashToStateAdapter = hashToStateAdapter;
};

History.prototype.initialize = function() {
  var that = this;
  $(window).on('popstate', function(e) {
    that.handlePopState(e.originalEvent.state);
  });

  // Create an artificial initial state
  var state = {initial: true};
  var didSetState = false;

  var rest = function() {
    // Blow away the current state -- it's only going to cause trouble.
    history.replaceState({}, '', document.location.href);
    this.replaceState(state, document.title, document.location.href);

    if (didSetState) {
      $(this).trigger('setStateInResponseToPageLoad', state);
    }
  }.bind(this);

  if (this.hashToStateAdapter && document.location.hash) {
    didSetState = true;
    // Need to honor any hash fragments that the user navigated to.
    this.hashToStateAdapter(document.location.hash, function(newState) {
      state = newState;
      rest();
    });
  } else {
    rest();
  }
};

History.prototype.makeState = function(obj) {
  var currentStateId = null;
  if (history.state && 'id' in history.state) {
    currentStateId = history.state.id;
  }
  return $.extend({
    length: history.length,
    previousStateId: currentStateId,
    id: Date.now() + '' + Math.floor(Math.random() * 100000000)
  }, obj);
};

History.prototype.simplifyState = function(obj) {
  var state = $.extend({}, obj);
  delete state['id'];
  // delete state['length'];
  delete state['previousStateId'];
  return state;
};

History.prototype.handlePopState = function(state) {
  // note: we don't remove entries from this.state here, since the user could
  // still go forward to them.
  if (state && 'id' in state) {
    var stateObj = this.states[this.getStateIndexById(state.id)];
    if (stateObj && stateObj.expectingBack) {
      // This is happening as a result of a call on the History object.
      delete stateObj.expectingBack;
      return;
    }
  }

  var trigger = function() {
    $(this).trigger('setStateInResponseToUser', state);
  }.bind(this);
  if (!state && this.hashToStateAdapter) {
    this.hashToStateAdapter(document.location.hash, function(newState) {
      state = newState;
      trigger();
    });
  } else {
    trigger();
  }
};

// Just like history.pushState.
History.prototype.pushState = function(stateObj, title, url) {
  var state = this.makeState(stateObj);
  this.states.push(state);
  history.pushState(state, title, url);
  document.title = title;
};

// Just like history.replaceState.
History.prototype.replaceState = function(stateObj, title, url) {
  var curState = this.getCurrentState();
  var replaceIdx = null;
  var previousId = null;
  if (curState) {
    if ('id' in curState) {
      replaceIdx = this.getStateIndexById(curState.id);
    }
    if ('previousStateId' in curState) {
      // in replacing the current state, we inherit its parent state.
      previousId = curState.previousStateId;
    }
  }

  var state = this.makeState(stateObj);
  if (previousId !== null) {
    state.previousStateId = previousId;
  }
  if (replaceIdx !== null) {
    this.states[replaceIdx] = state;
  } else {
    this.states.push(state);
  }
  history.replaceState(state, title, url);
  document.title = title;
}

History.prototype.getCurrentState = function() {
  return history.state;
};

History.prototype.getStateIndexById = function(stateId) {
  for (var i = 0; i < this.states.length; i++) {
    if (this.states[i].id == stateId) return i;
  }
  return null;
};

// Get the state object one prior to the given one.
History.prototype.getPreviousState = function(state) {
  if (!('previousStateId' in state)) return null;
  var id = state['previousStateId'];
  if (id == null) return id;

  var idx = this.getStateIndexById(id);
  if (idx !== null) {
    return this.states[idx];
  }
  throw "State out of whack!";
};

/**
 * Go back in history until the predicate is true.
 * If predicate is a string, go back until it's a key in the state object.
 * This will not result in a setStateInResponseToUser event firing.
 * Returns the number of steps back in the history that it went (possibly 0 if
 * the current state matches the predicate).
 * If no matching history state is found, the history stack will be cleared and
 * alternativeState will be pushed on.
 */
History.prototype.goBackUntil = function(predicate, alternativeState) {
  // Convenience for common case of checking if history state has a key.
  if (typeof(predicate) == "string") {
    return this.goBackUntil(
        function(state) { return predicate in state },
        alternativeState);
  }

  var state = this.getCurrentState();
  var numBack = 0;

  var lastState = null;
  while (state && !predicate(state)) {
    lastState = state;
    state = this.getPreviousState(state);
    numBack += 1;
  }
  if (state && numBack) {
    state.expectingBack = true;
    history.go(-numBack);
    return numBack;
  }
  if (numBack == 0) {
    return 0;  // current state fulfilled predicate
  } else {
    // no state fulfilled predicate. Clear the stack to just one state and
    // replace it with alternativeState.
    var stackLen = numBack;
    if (stackLen != 1) {
      lastState.expectingBack = true;
      history.go(-(stackLen - 1));
    }
    this.replaceState(alternativeState[0], alternativeState[1], alternativeState[2]);
  }
};

// Debugging method -- prints the history stack.
History.prototype.logStack = function() {
  var state = this.getCurrentState();
  var i = 0;
  while (state) {
    console.log((i > 0 ? '-' : ' ') + i, this.simplifyState(state));
    state = this.getPreviousState(state);
    i++;
  }
};
// This should go in the $(function()) block below.
// It's exposed to facilitate debugging.
h = new History(function(hash, cb) {
  hashToStateObject(hash.substr(1), cb);
});

// Ping Google Analytics with the current URL (e.g. after history.pushState).
// See http://stackoverflow.com/a/4813223/388951
function trackAnalyticsPageView() {
  var url = location.pathname + location.search  + location.hash;
  ga('send', 'pageview', { 'page': url });
}

var LOG_HISTORY_EVENTS = false;
// var LOG_HISTORY_EVENTS = true;

$(function() {
  // Relevant UI methods:
  // - transitionToStateObject(obj)
  //
  // State/URL manipulation:
  // - stateObjectToHash()
  // - hashToStateObject()
  //
  // State objects look like:
  // {photo_id:string, g:string}

  // Returns URL fragments like '/#g:123'.
  var fragment = function(state) {
    return '/#' + stateObjectToHash(state);
  };

  var title = function(state) {
    var old_nyc = 'Old NYC';
    if ('photo_id' in state) {
      return old_nyc + ' - Photo ' + state.photo_id;
    } else if ('g' in state) {
      // TODO: include cross-streets in the title
      return old_nyc + ' - Grid';
    } else {
      return old_nyc;
    }
  };

  $(window)
    .on('showGrid', function(e, pos) {
      var state = {g:pos};
      h.pushState(state, title(state), fragment(state));
      trackAnalyticsPageView();
    }).on('hideGrid', function() {
      var state = {initial: true};
      h.goBackUntil('initial', [state, title(state), fragment(state)]);
    }).on('openPreviewPanel', function() {
      // This is a transient state -- it should immediately be replaced.
      var state = {photo_id: true};
      h.pushState(state, title(state), fragment(state));
    }).on('showPhotoPreview', function(e, photo_id) {
      var g = $('#expanded').data('grid-key');
      var state = {photo_id:photo_id};
      if (g == 'pop') state.g = 'pop';
      h.replaceState(state, title(state), fragment(state));
      trackAnalyticsPageView();
    }).on('closePreviewPanel', function() {
      var g = $('#expanded').data('grid-key');
      var state = {g: g};
      h.goBackUntil('g', [state, title(state), fragment(state)]);
    });

  // Update the UI in response to hitting the back/forward button,
  // a hash fragment on initial page load or the user editing the URL.
  $(h).on('setStateInResponseToUser setStateInResponseToPageLoad',
  function(e, state) {
    // It's important that these methods only configure the UI.
    // They must not trigger events, or they could cause a loop!
    transitionToStateObject(state);
  });

  $(h).on('setStateInResponseToPageLoad', function(e, state) {
    trackAnalyticsPageView();  // hopefully this helps track social shares
  });

  if (LOG_HISTORY_EVENTS) {
    $(window)
      .on('showGrid', function(e, pos) {
        console.log('showGrid', pos);
      }).on('hideGrid', function() {
        console.log('hideGrid');
      }).on('showPhotoPreview', function(e, photo_id) {
        console.log('showPhotoPreview', photo_id);
      }).on('closePreviewPanel', function() {
        console.log('closePreviewPanel');
      }).on('openPreviewPanel', function() {
        console.log('openPreviewPanel');
      });
    $(h).on('setStateInResponseToUser', function(e, state) {
      console.log('setStateInResponseToUser', state);
    }).on('setStateInResponseToPageLoad', function(e, state) {
      console.log('setStateInResponseToPageLoad', state);
    });
  }

  // To load from a URL fragment, the map object must be ready.
  mapPromise.done(function() {
    h.initialize();
  });

});
/* Modernizr 2.6.2 (Custom Build) | MIT & BSD
 * Build: http://modernizr.com/download/#-csstransitions-shiv-cssclasses-prefixed-testprop-testallprops-domprefixes-load
 */
;window.Modernizr=function(a,b,c){function x(a){j.cssText=a}function y(a,b){return x(prefixes.join(a+";")+(b||""))}function z(a,b){return typeof a===b}function A(a,b){return!!~(""+a).indexOf(b)}function B(a,b){for(var d in a){var e=a[d];if(!A(e,"-")&&j[e]!==c)return b=="pfx"?e:!0}return!1}function C(a,b,d){for(var e in a){var f=b[a[e]];if(f!==c)return d===!1?a[e]:z(f,"function")?f.bind(d||b):f}return!1}function D(a,b,c){var d=a.charAt(0).toUpperCase()+a.slice(1),e=(a+" "+n.join(d+" ")+d).split(" ");return z(b,"string")||z(b,"undefined")?B(e,b):(e=(a+" "+o.join(d+" ")+d).split(" "),C(e,b,c))}var d="2.6.2",e={},f=!0,g=b.documentElement,h="modernizr",i=b.createElement(h),j=i.style,k,l={}.toString,m="Webkit Moz O ms",n=m.split(" "),o=m.toLowerCase().split(" "),p={},q={},r={},s=[],t=s.slice,u,v={}.hasOwnProperty,w;!z(v,"undefined")&&!z(v.call,"undefined")?w=function(a,b){return v.call(a,b)}:w=function(a,b){return b in a&&z(a.constructor.prototype[b],"undefined")},Function.prototype.bind||(Function.prototype.bind=function(b){var c=this;if(typeof c!="function")throw new TypeError;var d=t.call(arguments,1),e=function(){if(this instanceof e){var a=function(){};a.prototype=c.prototype;var f=new a,g=c.apply(f,d.concat(t.call(arguments)));return Object(g)===g?g:f}return c.apply(b,d.concat(t.call(arguments)))};return e}),p.csstransitions=function(){return D("transition")};for(var E in p)w(p,E)&&(u=E.toLowerCase(),e[u]=p[E](),s.push((e[u]?"":"no-")+u));return e.addTest=function(a,b){if(typeof a=="object")for(var d in a)w(a,d)&&e.addTest(d,a[d]);else{a=a.toLowerCase();if(e[a]!==c)return e;b=typeof b=="function"?b():b,typeof f!="undefined"&&f&&(g.className+=" "+(b?"":"no-")+a),e[a]=b}return e},x(""),i=k=null,function(a,b){function k(a,b){var c=a.createElement("p"),d=a.getElementsByTagName("head")[0]||a.documentElement;return c.innerHTML="x<style>"+b+"</style>",d.insertBefore(c.lastChild,d.firstChild)}function l(){var a=r.elements;return typeof a=="string"?a.split(" "):a}function m(a){var b=i[a[g]];return b||(b={},h++,a[g]=h,i[h]=b),b}function n(a,c,f){c||(c=b);if(j)return c.createElement(a);f||(f=m(c));var g;return f.cache[a]?g=f.cache[a].cloneNode():e.test(a)?g=(f.cache[a]=f.createElem(a)).cloneNode():g=f.createElem(a),g.canHaveChildren&&!d.test(a)?f.frag.appendChild(g):g}function o(a,c){a||(a=b);if(j)return a.createDocumentFragment();c=c||m(a);var d=c.frag.cloneNode(),e=0,f=l(),g=f.length;for(;e<g;e++)d.createElement(f[e]);return d}function p(a,b){b.cache||(b.cache={},b.createElem=a.createElement,b.createFrag=a.createDocumentFragment,b.frag=b.createFrag()),a.createElement=function(c){return r.shivMethods?n(c,a,b):b.createElem(c)},a.createDocumentFragment=Function("h,f","return function(){var n=f.cloneNode(),c=n.createElement;h.shivMethods&&("+l().join().replace(/\w+/g,function(a){return b.createElem(a),b.frag.createElement(a),'c("'+a+'")'})+");return n}")(r,b.frag)}function q(a){a||(a=b);var c=m(a);return r.shivCSS&&!f&&!c.hasCSS&&(c.hasCSS=!!k(a,"article,aside,figcaption,figure,footer,header,hgroup,nav,section{display:block}mark{background:#FF0;color:#000}")),j||p(a,c),a}var c=a.html5||{},d=/^<|^(?:button|map|select|textarea|object|iframe|option|optgroup)$/i,e=/^(?:a|b|code|div|fieldset|h1|h2|h3|h4|h5|h6|i|label|li|ol|p|q|span|strong|style|table|tbody|td|th|tr|ul)$/i,f,g="_html5shiv",h=0,i={},j;(function(){try{var a=b.createElement("a");a.innerHTML="<xyz></xyz>",f="hidden"in a,j=a.childNodes.length==1||function(){b.createElement("a");var a=b.createDocumentFragment();return typeof a.cloneNode=="undefined"||typeof a.createDocumentFragment=="undefined"||typeof a.createElement=="undefined"}()}catch(c){f=!0,j=!0}})();var r={elements:c.elements||"abbr article aside audio bdi canvas data datalist details figcaption figure footer header hgroup mark meter nav output progress section summary time video",shivCSS:c.shivCSS!==!1,supportsUnknownElements:j,shivMethods:c.shivMethods!==!1,type:"default",shivDocument:q,createElement:n,createDocumentFragment:o};a.html5=r,q(b)}(this,b),e._version=d,e._domPrefixes=o,e._cssomPrefixes=n,e.testProp=function(a){return B([a])},e.testAllProps=D,e.prefixed=function(a,b,c){return b?D(a,b,c):D(a,"pfx")},g.className=g.className.replace(/(^|\s)no-js(\s|$)/,"$1$2")+(f?" js "+s.join(" "):""),e}(this,this.document),function(a,b,c){function d(a){return"[object Function]"==o.call(a)}function e(a){return"string"==typeof a}function f(){}function g(a){return!a||"loaded"==a||"complete"==a||"uninitialized"==a}function h(){var a=p.shift();q=1,a?a.t?m(function(){("c"==a.t?B.injectCss:B.injectJs)(a.s,0,a.a,a.x,a.e,1)},0):(a(),h()):q=0}function i(a,c,d,e,f,i,j){function k(b){if(!o&&g(l.readyState)&&(u.r=o=1,!q&&h(),l.onload=l.onreadystatechange=null,b)){"img"!=a&&m(function(){t.removeChild(l)},50);for(var d in y[c])y[c].hasOwnProperty(d)&&y[c][d].onload()}}var j=j||B.errorTimeout,l=b.createElement(a),o=0,r=0,u={t:d,s:c,e:f,a:i,x:j};1===y[c]&&(r=1,y[c]=[]),"object"==a?l.data=c:(l.src=c,l.type=a),l.width=l.height="0",l.onerror=l.onload=l.onreadystatechange=function(){k.call(this,r)},p.splice(e,0,u),"img"!=a&&(r||2===y[c]?(t.insertBefore(l,s?null:n),m(k,j)):y[c].push(l))}function j(a,b,c,d,f){return q=0,b=b||"j",e(a)?i("c"==b?v:u,a,b,this.i++,c,d,f):(p.splice(this.i++,0,a),1==p.length&&h()),this}function k(){var a=B;return a.loader={load:j,i:0},a}var l=b.documentElement,m=a.setTimeout,n=b.getElementsByTagName("script")[0],o={}.toString,p=[],q=0,r="MozAppearance"in l.style,s=r&&!!b.createRange().compareNode,t=s?l:n.parentNode,l=a.opera&&"[object Opera]"==o.call(a.opera),l=!!b.attachEvent&&!l,u=r?"object":l?"script":"img",v=l?"script":u,w=Array.isArray||function(a){return"[object Array]"==o.call(a)},x=[],y={},z={timeout:function(a,b){return b.length&&(a.timeout=b[0]),a}},A,B;B=function(a){function b(a){var a=a.split("!"),b=x.length,c=a.pop(),d=a.length,c={url:c,origUrl:c,prefixes:a},e,f,g;for(f=0;f<d;f++)g=a[f].split("="),(e=z[g.shift()])&&(c=e(c,g));for(f=0;f<b;f++)c=x[f](c);return c}function g(a,e,f,g,h){var i=b(a),j=i.autoCallback;i.url.split(".").pop().split("?").shift(),i.bypass||(e&&(e=d(e)?e:e[a]||e[g]||e[a.split("/").pop().split("?")[0]]),i.instead?i.instead(a,e,f,g,h):(y[i.url]?i.noexec=!0:y[i.url]=1,f.load(i.url,i.forceCSS||!i.forceJS&&"css"==i.url.split(".").pop().split("?").shift()?"c":c,i.noexec,i.attrs,i.timeout),(d(e)||d(j))&&f.load(function(){k(),e&&e(i.origUrl,h,g),j&&j(i.origUrl,h,g),y[i.url]=2})))}function h(a,b){function c(a,c){if(a){if(e(a))c||(j=function(){var a=[].slice.call(arguments);k.apply(this,a),l()}),g(a,j,b,0,h);else if(Object(a)===a)for(n in m=function(){var b=0,c;for(c in a)a.hasOwnProperty(c)&&b++;return b}(),a)a.hasOwnProperty(n)&&(!c&&!--m&&(d(j)?j=function(){var a=[].slice.call(arguments);k.apply(this,a),l()}:j[n]=function(a){return function(){var b=[].slice.call(arguments);a&&a.apply(this,b),l()}}(k[n])),g(a[n],j,b,n,h))}else!c&&l()}var h=!!a.test,i=a.load||a.both,j=a.callback||f,k=j,l=a.complete||f,m,n;c(h?a.yep:a.nope,!!i),i&&c(i)}var i,j,l=this.yepnope.loader;if(e(a))g(a,0,l,0);else if(w(a))for(i=0;i<a.length;i++)j=a[i],e(j)?g(j,0,l,0):w(j)?B(j):Object(j)===j&&h(j,l);else Object(a)===a&&h(a,l)},B.addPrefix=function(a,b){z[a]=b},B.addFilter=function(a){x.push(a)},B.errorTimeout=1e4,null==b.readyState&&b.addEventListener&&(b.readyState="loading",b.addEventListener("DOMContentLoaded",A=function(){b.removeEventListener("DOMContentLoaded",A,0),b.readyState="complete"},0)),a.yepnope=k(),a.yepnope.executeStack=h,a.yepnope.injectJs=function(a,c,d,e,i,j){var k=b.createElement("script"),l,o,e=e||B.errorTimeout;k.src=a;for(o in d)k.setAttribute(o,d[o]);c=j?h:c||f,k.onreadystatechange=k.onload=function(){!l&&g(k.readyState)&&(l=1,c(),k.onload=k.onreadystatechange=null)},m(function(){l||(l=1,c(1))},e),i?k.onload():n.parentNode.insertBefore(k,n)},a.yepnope.injectCss=function(a,c,d,e,g,i){var e=b.createElement("link"),j,c=i?h:c||f;e.href=a,e.rel="stylesheet",e.type="text/css";for(j in d)e.setAttribute(j,d[j]);g||(n.parentNode.insertBefore(e,n),m(c,0))}}(this,document),Modernizr.load=function(){yepnope.apply(window,[].slice.call(arguments,0))};/*
 * jQuery appear plugin
 *
 * Copyright (c) 2012 Andrey Sidorov
 * licensed under MIT license.
 *
 * https://github.com/morr/jquery.appear/
 *
 * Version: 0.3.3
 */
(function($) {
  var selectors = [];

  var check_binded = false;
  var check_lock = false;
  var defaults = {
    interval: 250,
    force_process: false
  }
  var $window = $(window);

  var $prior_appeared;

  function process() {
    check_lock = false;
    for (var index = 0; index < selectors.length; index++) {
      var $appeared = $(selectors[index]).filter(function() {
        return $(this).is(':appeared');
      });

      $appeared.trigger('appear', [$appeared]);

      if ($prior_appeared) {
        var $disappeared = $prior_appeared.not($appeared);
        $disappeared.trigger('disappear', [$disappeared]);
      }
      $prior_appeared = $appeared;
    }
  }

  // "appeared" custom filter
  $.expr[':']['appeared'] = function(element) {
    var $element = $(element);
    if (!$element.is(':visible')) {
      return false;
    }

    var window_left = $window.scrollLeft();
    var window_top = $window.scrollTop();
    var offset = $element.offset();
    var left = offset.left;
    var top = offset.top;

    if (top + $element.height() >= window_top &&
        top - ($element.data('appear-top-offset') || 0) <= window_top + $window.height() &&
        left + $element.width() >= window_left &&
        left - ($element.data('appear-left-offset') || 0) <= window_left + $window.width()) {
      return true;
    } else {
      return false;
    }
  }

  $.fn.extend({
    // watching for element's appearance in browser viewport
    appear: function(options) {
      var opts = $.extend({}, defaults, options || {});
      var selector = this.selector || this;
      if (!check_binded) {
        var on_check = function() {
          if (check_lock) {
            return;
          }
          check_lock = true;

          setTimeout(process, opts.interval);
        };

        $(window).scroll(on_check).resize(on_check);
        check_binded = true;
      }

      if (opts.force_process) {
        setTimeout(process, opts.interval);
      }
      selectors.push(selector);
      return $(selector);
    }
  });

  $.extend({
    // force elements's appearance check
    force_appear: function() {
      if (check_binded) {
        process();
        return true;
      };
      return false;
    }
  });
})(jQuery);
/*
* debouncedresize: special jQuery event that happens once after a window resize
*
* latest version and complete README available on Github:
* https://github.com/louisremi/jquery-smartresize/blob/master/jquery.debouncedresize.js
*
* Copyright 2011 @louis_remi
* Licensed under the MIT license.
*/
var $event = $.event,
$special,
resizeTimeout;


function clientRectIntersect(a, b) {
  var left = Math.max(a.left, b.left);
  var right = Math.min(a.right, b.right);
  var top = Math.max(a.top, b.top);
  var bottom = Math.min(a.bottom, b.bottom);
  return {
    left: left,
    right: Math.max(left, right),
    top: top,
    bottom: Math.max(bottom, top),
    width: Math.max(right - left, 0),
    height: Math.max(bottom - top, 0)
  };
}


// We check for visblity within:
// 1. The window
// 2. Containing scrollable elements
function isElementInViewport(el) {
  // special bonus for those using jQuery
  if (el instanceof jQuery) {
    el = el[0];
  }

  var elRect = el.getBoundingClientRect();
  var windowRect = {
    top: 0,
    left: 0,
    bottom: $(window).height(),
    right: $(window).width(),
    height: $(window).height(),
    width: $(window).width()
  };

  elRect = clientRectIntersect(elRect, windowRect);
  if (elRect.width * elRect.height == 0) return false;

  var $scrollParents = scrollableParents(el);
  for (var i = 0; i < $scrollParents.length; i++) {
    var scrollParent = $scrollParents.get(i);
    var scrollParentRect = scrollParent.getBoundingClientRect();
    elRect = clientRectIntersect(elRect, scrollParentRect);
    if (elRect.width * elRect.height == 0) return false;
  }

  return true;
}

function isElementScrollable(el) {
  return el.scrollHeight > el.clientHeight;
}

function scrollableParents(node) {
  var $parents = $(node).parents().filter(function(_, e) {
    return isElementScrollable(e);
  });
  return ($parents.length > 0 ? $parents : $('body'));
}

$special = $event.special.debouncedresize = {
  setup: function() {
    $( this ).on( "resize", $special.handler );
  },
  teardown: function() {
    $( this ).off( "resize", $special.handler );
  },
  handler: function( event, execAsap ) {
    // Save the context
    var context = this,
      args = arguments,
      dispatch = function() {
        // set correct event type
        event.type = "debouncedresize";
        $event.dispatch.apply( context, args );
      };

    if ( resizeTimeout ) {
      clearTimeout( resizeTimeout );
    }

    execAsap ?
      dispatch() :
      resizeTimeout = setTimeout( dispatch, $special.threshold );
  },
  threshold: 250
};

/*
 * throttledresize: special jQuery event that happens at a reduced rate compared to "resize"
 *
 * latest version and complete README available on Github:
 * https://github.com/louisremi/jquery-smartresize
 *
 * Copyright 2012 @louis_remi
 * Licensed under the MIT license.
 *
 * This saved you an hour of work? 
 * Send me music http://www.amazon.co.uk/wishlist/HNTU0468LQON
 */
(function($) {

var $event = $.event,
	$special,
	dummy = {_:0},
	frame = 0,
	wasResized, animRunning;

$special = $event.special.throttledresize = {
	setup: function() {
		$( this ).on( "resize", $special.handler );
	},
	teardown: function() {
		$( this ).off( "resize", $special.handler );
	},
	handler: function( event, execAsap ) {
		// Save the context
		var context = this,
			args = arguments;

		wasResized = true;

		if ( !animRunning ) {
			setInterval(function(){
				frame++;

				if ( frame > $special.threshold && wasResized || execAsap ) {
					// set correct event type
					event.type = "throttledresize";
					$event.dispatch.apply( context, args );
					wasResized = false;
					frame = 0;
				}
				if ( frame > 9 ) {
					$(dummy).stop();
					animRunning = false;
					frame = 0;
				}
			}, 30);
			animRunning = true;
		}
	},
	threshold: 0
};

})(jQuery);

var Grid = function() {

    // list of items
  var $grid = null,  // $grid is the <ul>
    // the items
    $items = null,  // these are the <li>s
    // current expanded item's index
    current = -1,
    // position (top) of the expanded item
    // used to know if the preview will expand in a different row
    previewPos = -1,
    // extra amount of pixels to scroll the window
    scrollExtra = 0,
    // extra margin when expanded (between preview overlay and the next items)
    marginExpanded = 10,
    $window = $(window), winsize,
    $body = null,
    // transitionend events
    transEndEventNames = {
      'WebkitTransition' : 'webkitTransitionEnd',
      'MozTransition' : 'transitionend',
      'OTransition' : 'oTransitionEnd',
      'msTransition' : 'MSTransitionEnd',
      'transition' : 'transitionend'
    },
    transEndEventName = transEndEventNames[Modernizr.prefixed('transition')],
    // support for csstransitions
    support = Modernizr.csstransitions,
    // default settings
    settings = {
      minHeight: 500,
      maxHeight: 750,
      speed: 350,
      easing: 'ease'
    };

  function init(grid, config) {
    $grid = $(grid);
    $items = $grid.children('li');
    $body = $('html, body');

    // the settings..
    settings = $.extend(true, {}, settings, config);

    // save item's size and offset
    saveItemInfo(true);
    // get window's size
    getWinSize();
    // initialize some events
    initEvents();
  }

  // add more items to the grid.
  // the new items need to appended to the grid.
  // after that call Grid.addItems(theItems);
  function addItems($newitems) {
    $items = $items.add( $newitems );

    $newitems.each(function() {
      var $item = $(this);
      $item.data({
        offsetTop: $item.offset().top,
        height: $item.height()
      });
    });

    initItemsEvents($newitems);
  }

  // saves the item´s offset top and height (if saveheight is true)
  function saveItemInfo(saveheight) {
    $items.each(function() {
      var $item = $(this);
      $item.data('offsetTop', $item.offset().top);
      if( saveheight ) {
        $item.data('height', $item.height());
      }
    });
  }

  function initEvents() {
    // when clicking an item, show the preview with the item´s info and large
    // image.
    // close the item if already expanded.
    // also close if clicking on the item´s cross
    initItemsEvents($items);
    
    // on window resize get the window´s size again
    // reset some values..
    $window.on('debouncedresize', function() {
      scrollExtra = 0;
      previewPos = -1;
      // save item´s offset
      saveItemInfo();
      getWinSize();
      var preview = $.data($grid, 'preview');
      if (typeof preview != 'undefined') {
        hidePreview();
      }
    });
  }

  function initItemsEvents($items) {
    $items.on('click', 'span.og-close', function() {
      hidePreview();
      $(this).trigger('og-deselect');
      return false;
    }).children('a').on('click', function(e) {
      var $li = $(this).parent();
      // check if item already opened
      if (current === $li.index()) {
        hidePreview()
        $li.trigger('og-deselect');
      } else {
        var previousSelection = current;
        showPreview($li);
        if (previousSelection == -1) {
          $grid.trigger('og-openpreview');
        }
        $li.trigger('og-select');
      }
      return false;
    });
  }

  function getWinSize() {
    winsize = { width : $window.width(), height : $window.height() };
  }

  function showPreview($item) {
    var preview = $.data($grid, 'preview'),
      // item´s offset top
      position = $item.data('offsetTop');

    scrollExtra = 0;

    // if a preview exists and previewPos is different (different row) from
    // item's top then close it
    if (typeof preview != 'undefined') {
      // not in the same row
      if (previewPos !== position) {
        // if position > previewPos then we need to take te current preview's
        // height in consideration when scrolling the window
        if (position > previewPos) {
          scrollExtra = preview.height;
        }
        hidePreview();
      } else {
        // same row 
        preview.update($item);
        return false;
      }
    }

    // update previewPos
    previewPos = position;
    // initialize new preview for the clicked item
    preview = $.data($grid, 'preview', new Preview($item));
    // expand preview overlay
    preview.open();
  }

  function hidePreview() {
    current = -1;
    var preview = $.data($grid, 'preview');
    preview.close();
    $.removeData($grid, 'preview');
  }

  // the preview obj / overlay
  function Preview($item) {
    this.$item = $item;
    this.expandedIdx = this.$item.index();
    this.create();
    this.update();
  }

  Preview.prototype = {
    create : function() {
      // create Preview structure:
      this.$details = $( '<div class="og-details" />' );
      this.$loading = $( '<div class="og-loading"></div>' );
      this.$fullimage = $( '<div class="og-fullimg"></div>' ).append( this.$loading ).append($('<div class="og-details-left" style="display:none">'));
      this.$closePreview = $( '<span class="og-close"></span>' );
      this.$previewInner = $( '<div class="og-expander-inner"></div>' ).append( this.$closePreview, this.$fullimage, this.$details );
      this.$previewLeft = $('<div class="og-previous"></div>');
      this.$previewRight = $('<div class="og-next"></div>');
      this.$previewEl = $( '<div class="og-expander"></div>' ).append( this.$previewInner, this.$previewLeft, this.$previewRight );
      // append preview element to the item
      this.$item.append(this.getEl());
      // set the transitions for the preview and the item
      if (support) {
        this.setTransition();
      }
    },

    update : function( $item ) {
      if( $item ) {
        this.$item = $item;
      }
      
      // if already expanded remove class "og-expanded" from current item and add it to new item
      // $('.og-grid li').removeClass('og-expanded');
      if( current !== -1 ) {
        var $currentItem = $items.eq(current);
        $currentItem.removeClass('og-expanded');
        this.$item.addClass('og-expanded');
        // position the preview correctly
        this.positionPreview();
      }

      // update current value
      current = this.$item.index();

      // update preview´s content
      var $itemEl = this.$item.children('a'),
        eldata = {
          largesrc: $itemEl.data('largesrc'),
        };

      this.$details.empty();
      this.$fullimage.find('.og-details-left').empty();
      $(this.$item).trigger('og-fill', this.$details);

      var self = this;
      
      // remove the current image in the preview
      if (typeof self.$largeImg != 'undefined') {
        self.$largeImg.remove();
      }

      // preload large image and add it to the preview
      // for smaller screens we don´t display the large image (the media query will hide the fullimage wrapper)
      if (self.$fullimage.is(':visible')) {
        this.$loading.show();
        $('<img/>').load(function() {
          var $img = $(this);
          if ($img.attr('src') === self.$item.children('a').data('largesrc')) {
            var $fullimage = self.$fullimage;
            self.$loading.hide();
            $fullimage.find('.og-loading img').remove();
            self.$largeImg = $img.fadeIn(settings.speed);
            $fullimage.append([
                self.$largeImg,
                self.$fullimage.find('.og-details-left').show()]);
          }
        }).attr('src', eldata.largesrc);
      }
    },

    // Open the preview pane
    open: function() {
      setTimeout($.proxy(function() {  
        // set the height for the preview and the item
        var self = this;
        this.setHeights().then(function() {
          // scroll to position the preview in the right place
          self.positionPreview();
        });
      }, this), 25);

      var self = this;
      var goLeft = function() {
        if (current > 0) {
          var $li = $items.eq(current - 1);
          showPreview($li);
          $li.trigger('og-select');
        }
      };
      var goRight = function() {
        if (current < $items.length) {
          var $li = $items.eq(current + 1);
          showPreview($li);
          $li.trigger('og-select');
        }
      };
      $('.og-previous, .og-next').on('click', function() {
        if ($(this).is('.og-previous')) {
          goLeft();
        } else {
          goRight();
        }
      });
      $(document).on('keyup.og', function(e) {
        if (e.keyCode == 37) {
          goLeft();
        } else if (e.keyCode == 39) {
          goRight();
        } else if (e.keyCode == 27) {  // escape
          self.close();
          $grid.trigger('og-deselect');
        }
      });
    },

    // Close the preview pane
    close : function() {
      $('.og-previous, .og-next').off('click');
      $(document).off('keyup.og');

      var self = this,
        onEndFn = function() {
          self.$item.removeClass( 'og-expanded' );
          self.$item.css('height', '');
          self.$previewEl.remove();
        };

      setTimeout($.proxy(function() {
        if (typeof this.$largeImg !== 'undefined') {
          this.$largeImg.fadeOut('fast');
        }
        this.$previewEl.css('height', 0);
        // the current expanded item (might be different from this.$item)
        var $expandedItem = $items.eq(this.expandedIdx);
        $expandedItem.css('height', $expandedItem.data('height')).one(transEndEventName, onEndFn);

        if (!support) {
          onEndFn.call();
        }
      }, this), 25);
      
      return false;
    },

    // TODO: document, rename all these horrible variables.
    // this.$previewEl is the gray area
    // this.$item is the <li>, so its height must include the thumbnail's height!
    calcHeight: function() {
      var maxMargin = 100;  // image height + margin == previewHeight
      var scrollParents = scrollableParents($grid),
          $scrollParent = $(scrollParents.get(0)),
          scrollParentHeight = Math.min($scrollParent.height(), $(window).height()),
          thumbnailHeight = this.$item.data('height'),
          previewHeight = scrollParentHeight - thumbnailHeight - 50;

      if (previewHeight > settings.maxHeight) {
        previewHeight = settings.maxHeight;
      }

      this.previewHeight = previewHeight;  // this.$item.data('eg-height');  // height of image

      this.itemHeight = previewHeight + thumbnailHeight + 10;
    },

    setHeights: function() {
      var deferred = $.Deferred();
      var self = this,
        onEndFn = function() {
          self.$item.addClass('og-expanded');
          deferred.resolve({});
        };

      this.calcHeight();
      this.$previewEl.css('height', this.previewHeight);
      this.$item
        .css('height', this.itemHeight)
        .one(transEndEventName, onEndFn);

      if (!support) {
        onEndFn.call();
      }
      return deferred;
    },

    positionPreview: function() {
      // Scroll the newly-selected item to the top of the page.
      var $item = this.$item;
      var scrollParents = scrollableParents($grid),
          $scrollParent = $(scrollParents.get(0)),
          parentTop = $item.parent().position().top;
      if ($scrollParent.get(0).tagName == 'BODY') {
        parentTop = 0;  // .position() already accounts for <body>
      }
      $scrollParent.animate(
          {scrollTop: $item.position().top - parentTop},
          settings.speed);
    },

    setTransition: function() {
      this.$previewEl.css('transition', 'height ' + settings.speed + 'ms ' + settings.easing);
      this.$item.css('transition', 'height ' + settings.speed + 'ms ' + settings.easing);
    },

    getEl : function() {
      return this.$previewEl;
    }
  }

  return { 
    init: init,
    addItems: addItems,
    showPreview: showPreview,
    hidePreview: hidePreview
  };
};

(function($) {

  var imageMargin = 12;  // TODO(danvk): measure this.

// Returns an array of { height: XXX, images: [] }
// Each entry in images should have a height/width data field.
// TODO(danvk): could just return {height, startIndex, limitIndex} objects.
function partitionIntoRows(images, containerWidth, maxRowHeight) {
  var rows = [];
  var currentRow = [];
  $.each(images, function(i, image) {
    currentRow.push(image);
    var denom = 0;
    $.each(currentRow, function(_, image) {
      denom += $(image).data('eg-width') / $(image).data('eg-height');
    });
    var height = (containerWidth - imageMargin * currentRow.length) / denom;
    if (height < maxRowHeight) {
      rows.push({ height: height, images: currentRow });
      currentRow = [];
    }
  });
  if (currentRow.length > 0) {
    rows.push({ height: maxRowHeight, images: currentRow });
  }
  return rows;
}


function reflow($container) {
  var options = $container.data('og-options');
  var $ul = $container.find('ul.og-grid');
  flowImages($ul.find('li'), $ul.width(), options.rowHeight);
}


function flowImages(lis, width, maxRowHeight) {
  var rows = partitionIntoRows(lis, width, maxRowHeight);
  $.each(rows, function(_, row) {
    var height = Math.round(row.height);
    $.each(row.images, function(_, li) {
      var imgW = $(li).data('eg-width'),
          imgH = $(li).data('eg-height');
      $(li).find('img').attr({
        'width': Math.floor(imgW * (height / imgH)),
        'height': height
      });
    });
    // line wrap happens naturally here.
  });
}


// The image thumbnails all start hidden (by setting data-src instead of src).
// This shows the ones which are above the fold by transferring attributes.
function loadVisibleImages($container) {
  $container.find('img[data-src]').each(function(i, imgEl) {
    var $img = $(imgEl);
    if (isElementInViewport($img)) {
      $img
        .attr('src', $img.attr('data-src'))
        .removeAttr('data-src');
    }
  });
}

/**
 * options = {
 *   rowHeight: NNN
 * }
 * images = [ { src: "", width: M, height: N, largesrc: "", id: "" }, ... ]
 */
$.fn.expandableGrid = function(arg1) {
  var meth = null;
  if ($.type(arg1) === 'object') {
    meth = createExpandableGrid;
  } else if ($.type(arg1) === 'string') {
    if (arg1 === 'select') {
      meth = selectImage;
    } else if (arg1 == 'deselect') {
      meth = deselect;
    } else if (arg1 == 'selectedId') {
      meth = selectedId;
    }
  }
  if (!meth) {
    throw "Invalid expandableGrid call";
  }
  return meth.apply(this, arguments);
};

var createExpandableGrid = function(options, images) {
  var lis = $.map(images, function(image) {
    var $li = $('<li><a><img /></a></li>');
    $li.find('img').attr({
      'data-src': image.src
    });
    $li.find('a').attr({
      'data-largesrc': image.largesrc,
      'href': '#'
    });
    if (image.hasOwnProperty('id')) {
      $li.data('image-id', image.id);
    }
    $li.data({
      'eg-width': image.width,
      'eg-height': image.height
    });
    return $li.get(0);
  });

  $(this).data('og-options', options);

  var $ul = $('<ul class=og-grid>').append($(lis).hide());
  $ul.appendTo(this.empty());
  reflow(this);
  $(lis).show();
  loadVisibleImages(this);
  var container = this;
  $([this.get(0), document]).on('scroll', function() {
    loadVisibleImages($(container));  // new images may have become visible.
  });
  this.on('og-deselect', function() {
    // hack to load new images through the transition.
    var interval = window.setInterval(function() {
      loadVisibleImages($(container));
    }, 100);
    window.setTimeout(function() {
      window.clearInterval(interval);
    }, 400);
  });

  // This should really be an object...
  g = Grid();
  g.init($ul.get(0), options);
  $(this).data('og-grid', g);

  // The initial display may have resulted in new scroll bars.
  // It would be nice to avoid this.
  reflow(this);

  return this;
};

var deselect = function(_) {
  $(this).data('og-grid').hidePreview();
};

var selectImage = function(_, id) {
  var $li = null;
  $(this).find('li').each(function(_, li) {
    if ($(li).data('image-id') == id) {
      $li = $(li);
      return false;
    }
  });
  if (!$li) {
    return false;
  }

  $(this).data('og-grid').showPreview($li);
  return true;
};

var selectedId = function() {
  return $(this).find('li.og-expanded').data('image-id');
};

$(window).on('resize', function( event ) {
  $('ul.og-grid').each(function(_, ul) {
    reflow($(ul).parent());
  });
});

})(jQuery);
