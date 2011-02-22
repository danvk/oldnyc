<!DOCTYPE html>
<html>
<head>
  <title>SF Image Geocoding Game</title>

  <link rel="stylesheet" type="text/css" href="/jquery/star-rating/jquery.rating.css" />
  <style type="text/css">
    #record {
      max-width: 500px;
      position: absolute;
      top: 50px;
      left: 5px;
    }
    #geocode {
      position: absolute;
      top: 50px;
      left: 525px;
      width: 500px;
    }
    div.rating-cancel,
    div.rating-cancel a
    {
    display:none; width:0;height:0;overflow:hidden;
    }  
  </style>

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
        mapTypeId: google.maps.MapTypeId.ROADMAP
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
        // img.height = img.height * (500.0 / orig_width);
      }
    }

    function reset() {
      el("lat").value = '';
      el("lon").value = '';
      var latlng = new google.maps.LatLng(37.77493, -122.419416);
      marker.setPosition(latlng);
      var opts = {
        zoom: 13,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
      };
      map.setOptions(opts);
      updateButtons();
    }

    function updateButtons() {
      var ok = (el('lat').value != '' && el('lon').value != '');
      if (ok) {
        el('impossible').disabled = true;
        el('notme').disabled = true;
        el('success').disabled = false;
      } else {
        el('impossible').disabled = false;
        el('notme').disabled = false;
        el('success').disabled = true;
      }
    }

    function search() {
      var txt = document.getElementById("search").value;
      console.log(txt);
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
        console.log(status);
        if (status == google.maps.GeocoderStatus.OK) {
          var latLng = results[0].geometry.location;
          map.setCenter(latLng);
          marker.setPosition(latLng);
          updatePos(latLng);
        }
      });
    }
  </script>
</head>
<body onload="initialize_map()">
<h2>SF Image Geocoding Game</h2>

<div id="record">
<img id="image" src="/image?id={{image.id}}" onload='resize(this)' />

<p>
<b>ID</b> {{ image.photo_id }}<br/>
<b>Title</b> {{ image.title }}<br/>
<b>Date</b> {{ image.date }}<br/>
<b>Location</b> {{ image.location }}<br/>
<b>Description</b><br/>
{{ image.description|linebreaks }}
</p>
</div>

<div id="geocode">

<input type=hidden name="cookie" value="{{cookie}}" />
<input type=hidden name="id" value="{{image.id}}" />

<div id="map" style="width: 500px; height: 350px;"></div>
<b>Search:</b>
  <input type=text id="search" size="60" onChange="search()" />
  <input type=button value="Search" onClick="search()" /> <br/>
  
<hr/>

<form action="/geocode" method="post">
<b>Lat:</b>
  <input type=text id="lat" name="lat" size="30"
    onkeypress="updateButtons()" />
<b>Lon:</b>
  <input type=text id="lon" name="lon" size="30"
    onkeypress="updateButtons()" />
<input type=button value="reset" onclick="reset()" />

<table width=500>
<tr><td valign=top width=150>
  <p><b>Setting</b><br/>
  <input type="radio" id="indoors" name="setting" value="indoors">
  <label for="indoors"> Indoors<br/>
  <input type="radio" id="outdoors" name="setting" value="outdoors">
  <label for="outdoors"> Outdoors
  </p>
</td>
<td valign=top>
  <p><b>How interesting is this photo?</b><br/>
  <input name="rating" type="radio" class="star" value="1" />
  <input name="rating" type="radio" class="star" value="2" />
  <input name="rating" type="radio" class="star" value="3" />
  <input name="rating" type="radio" class="star" value="4" />
  <input name="rating" type="radio" class="star" value="5" />
  </p>
</td></tr>
</table>

<table width=500>
<tr><td valign=top>
  <input type="submit" id="impossible" name="impossible"
    value="This image can't be located on a map." /><br/>
  <input type="submit" id="notme" name="notme"
    value="This image might be located, but I can't do it." />
</td>
<td valign=middle><center>
  <input type="submit" id="success" name="success" disabled=true
    value="Success! Next image, please." />
</center>
</td></tr>
</table>

</form>
</div>

</body>
</html>
