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
        title: "Photo",
        draggable: true,
        animation: google.maps.Animation.DROP
      });

      function updatePos(pos) {
        var ll = pos.latLng;
        el("lat").value = ll.lat();
        el("lon").value = ll.lng();
        updateButtons();
      }
      google.maps.event.addListener(marker, 'drag', function(pos) {
        updatePos(pos);
      });
      google.maps.event.addListener(map, 'dblclick', function(pos) {
        marker.setPosition(pos.latLng);
        updatePos(pos);
      });
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
<div id="map" style="width: 500px; height: 350px;"></div>
<b>Lat:</b> <input type=text id="lat" name="lat" size="30" onkeypress="updateButtons()" />
<b>Lon:</b> <input type=text id="lon" name="lon" size="30" onkeypress="updateButtons()" />
<input type=button value="reset" onclick="reset()" />

<table width=500><tr><td valign=top width=150>
<p><b>Setting</b><br/>
<input type="radio" id="indoors" name="setting"><label for="indoors"> Indoors<br/>
<input type="radio" id="outdoors" name="setting"><label for="outdoors"> Outdoors
</p>

</td><td valign=top>

<p><b>How interesting is this photo?</b><br/>
<input name="star1" type="radio" class="star" />
<input name="star1" type="radio" class="star" />
<input name="star1" type="radio" class="star" />
<input name="star1" type="radio" class="star" />
<input name="star1" type="radio" class="star" />
</p>
</td></tr></table>

<table width=500>
<tr><td valign=top>
<input type="submit" id="impossible" name="impossible" value="This image can't be located on a map." /><br/>
<input type="submit" id="notme" name="notme" value="This image might be located, but I can't do it." />
</td>
<td valign=middle><center>
<input type="submit" id="success" name="success" value="Success! Next image, please." disabled=true />
</center></td></tr>
</table>

</div>

</body>
</html>
