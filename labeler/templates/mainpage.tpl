<!DOCTYPE html>
<html>
<head>
  <title>SF Image Geocoding Game</title>

  <link rel="stylesheet" type="text/css" href="/jquery/star-rating/jquery.rating.css" />
  <link rel="stylesheet" type="text/css" href="/geocode.css" />

  <!-- jQuery star rating plugin -->
  <script type="text/javascript" src="/jquery/jquery-1.5.min.js"></script>
  <script type="text/javascript" src="/jquery/star-rating/jquery.rating.js"></script>

  <!-- Google Maps API -->
  <script type="text/javascript"
      src="http://maps.google.com/maps/api/js?sensor=false">
  </script>

  <script type="text/javascript">
    function el(id) {
      return document.getElementById(id);
    }

    var marker;
    var map;
    var geocoder;

    function initialize_map() {
      var latlng = new google.maps.LatLng(37.77493, -122.419416);
      var opts = {
        zoom: 13,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: true
      };
      map = new google.maps.Map(el("map"), opts);

      marker = new google.maps.Marker({
        position: latlng, 
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP
      });

      geocoder = new google.maps.Geocoder();

      google.maps.event.addListener(marker, 'drag', function(pos) {
        updatePos(pos.latLng);
      });

      google.maps.event.addListener(map, 'dblclick', function(pos) {
        marker.setPosition(pos.latLng);
        updatePos(pos.latLng);
      });
    }

    function updatePos(ll) {
      el("lat").value = ll.lat();
      el("lon").value = ll.lng();
      updateButtons();
    }

    function resize(img) {
      var orig_width = img.width;
      if (orig_width > 500) {
        // This automatically adjusts the height of the image as well.
        img.width = 500;
        img.parentNode.style.width = 500 + 'px';
        // img.height = img.height * (500.0 / orig_width);
      } else {
        img.parentNode.style.width = orig_width + 'px';
      }
    }

    function resetlatlon() {
      el("lat").value = '';
      el("lon").value = '';
      var latlng = new google.maps.LatLng(37.77493, -122.419416);
      marker.setPosition(latlng);
      var opts = {
        zoom: 13,
        center: latlng
      };
      map.setOptions(opts);
      updateButtons();
    }

    function updateButtons() {
      var ok = (el('lat').value != '' && el('lon').value != '');
      if (ok) {
        el('success').disabled = false;
      } else {
        el('success').disabled = true;
      }
    }

    function updateLatLon(event) {
      var lat = parseFloat(el('lat').value);
      var lon = parseFloat(el('lon').value);
      // TODO(danvk): validate range
      if (lat && lon) {
        var latlng = new google.maps.LatLng(lat, lon);
        marker.setPosition(latlng);
        marker.setAnimation(google.maps.Animation.DROP);
        map.setCenter(latlng);
        updateButtons();
      }
      return false;
    }

    function search() {
      var txt = document.getElementById("search").value;
      var req = {
        address: txt,
        latLng: new google.maps.LatLng(37.77493, -122.419416),
        bounds: new google.maps.LatLngBounds(
          new google.maps.LatLng(37.554376, -122.61875),  // sw
          new google.maps.LatLng(37.879460, -122.28779)   // ne
        ),
        language: 'en'
      };

      geocoder.geocode(req, function(results, status) {
        var search_error = el('search_error');
        if (status == google.maps.GeocoderStatus.OK) {
          search_error.style.display = 'none';
          var latLng = results[0].geometry.location;
          map.setCenter(latLng);
          map.setZoom(16);
          marker.setPosition(latLng);
          marker.setAnimation(google.maps.Animation.DROP);
          updatePos(latLng);
        } else {
          if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
            status = "no results";
          }
          search_error.innerHTML = status;
          search_error.style.display = 'block';
        }
      });
    }

    function expandComments() {
      var cb = el('comment_box');
      if (cb.rows == 1) {
        cb.rows=5;
        cb.value='';
        cb.removeAttribute('readonly');
        cb.style.color='black';
      }
    }

    function maybeContractComments() {
      var cb = el('comment_box');
      if (cb.value == '') {
        cb.rows=1;
        cb.value='Any other comments? Those go here.';
        cb.readonly="readonly";
        cb.style.color='gray';
      }
    }
  </script>
</head>
<body onload="initialize_map()">
<div id="carousel">
  <div class="dotdotdot">
    .<br/>
    .<br/>
    .
  </div>
  {% for item in carousel %}
  <div class="carousel-image{% if item.current %} current-image{% endif %}">
    {% if not item.current %}<a href="/?id={{item.id}}">{% endif %}
    <img class="carousel-image-img" border=0 src="/image?id={{item.id}}" height=64 />
    {% if not item.current %}</a>{% endif %}
  </div>
  {% endfor %}
  <div class="dotdotdot">
    .<br/>
    .<br/>
    .
  </div>
</div>

<div id="record">
<h2 class="title">We have the photo&hellip;</h2>
<h2 class="in-frame">Photo</h2>

<div class="image">
<img id="image" src="/image?id={{image.id}}" onload='resize(this)' />
</div>

<p id="title">{{ image.title }}</p>

Date: {{ image.date }}

{% if image.note %}<p>{{ image.note|linebreaks }}</p>{% endif %}
<p>{{ image.folder }}</p>
<p style='font-size: small;'>View the <a href="{{ image.library_url }}">original record</a> at the San Francisco Historical Photograph Collection site.</p>

<div class="ratings-div">
  <input name="rating" type="radio" class="star" value="1" />
  <input name="rating" type="radio" class="star" value="2" />
  <input name="rating" type="radio" class="star" value="3" />
  <input name="rating" type="radio" class="star" value="4" />
  <input name="rating" type="radio" class="star" value="5" />
  &nbsp;
  <b>Rate this photo</b>
</div>

</div>

<div id="geocode">
<h2 class="title">&hellip; but where was it taken?</h2>
<h2 class="in-frame">Location</h2>

<div id="map" style="width: 500px; height: 350px;"></div>
<b>Search:</b>
  <input type=text id="search" size="60" onChange="search()" />
  <input type=button value="Search" onClick="search()" /> <br/>
  <div id="search_error" style="display:none;"></div>

<!--
<p class="instructions">Double-click on the map or drag-and-drop the pin to locate the photo.<br/>
Alternatively, you can search for:
<ul class="instructions">
  <li>Cross streets: <i>4th and Market</i> or <i>Polk &amp; Union</i>
  <li>Location names: <i>Dolores Park</i> or <i>Mark Hopkins Hotel</i>
  <li>Coordinates: <i>37.791558°N 122.410364°W</i> (copy/paste from Wikipedia)
</ul>
</p>
-->

<form action="/geocode" method="post">
<input type=hidden name="cookie" value="{{cookie}}" />
<input type=hidden name="id" value="{{image.id}}" />
<input type="hidden" id="lat" name="lat" />
<input type="hidden" id="lon" name="lon" />

<div style='margin-top: 30px;'>
<textarea id="comment_box" name="comments" rows=1 cols=60 onClick="expandComments()" readonly style="color: gray;" onblur="maybeContractComments()">
Any other comments? Those go here.
</textarea>
</div>

<!-- spacer -->
<div style='margin-bottom: 150px;'>&nbsp;</div>

<table width=500 style='bottom: 0px;'>
<tr><td align=left>
  <button type="submit" name="skip" style='height:40px;'>Skip this one</button>
</td>
<td align=right>
  <button type="submit" id="success" name="success" style='height: 40px;' disabled=true>Success! Next image, please.</button>
</td></tr>
</table>

</form>
</div>

</body>
</html>
