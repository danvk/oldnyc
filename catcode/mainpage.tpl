<!DOCTYPE html>
<html>
<head>
  <title>Category Geocoder</title>
  <!-- Google Maps API -->
  <script type="text/javascript"
      src="http://maps.google.com/maps/api/js?sensor=false">
  </script>

  <script type="text/javascript">
    var marker;
    var map;
    var geocoder;

    function el(id) {
      return document.getElementById(id);
    }

    function initialize_map() {
      // var latlng = new google.maps.LatLng(37.77493, -122.419416);
      var latlng = new google.maps.LatLng(40.74421, -73.97370);

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

    function do_search() {
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

    function updateButtons() {
      var ok = (el('lat').value != '' && el('lon').value != '');
      if (ok) {
        el('success').disabled = false;
      } else {
        el('success').disabled = true;
      }
    }

  </script>
</head>
<body onload="initialize_map()">
  <p>Category: <b>{{ category }}</b></p>
  <p>Examples<br/>
  {% for example_url in examples %}
    <a href="{{ example_url }}">{{forloop.counter}}</a>
  {% endfor %}
  </p>
  <div id="map" style="width: 800px; height: 500px;"></div>
  <div id="stats" style="position: absolute; left: 850px; top: 50px;">
  Total done: <b>{{ total_done }}</b>
  </div>
  <b>Search:</b>
    <input type=text id="search" size="90" onChange="do_search()" />
    <input type=button value="Search" onClick="do_search()" /> <br/>
    <div id="search_error" style="display:none;"></div>

  <form action="/" method="post">
  <input type="hidden" id="lat" name="lat" />
  <input type="hidden" id="lon" name="lon" />
  <p>Apply to pattern: <input type=text name=cat size=60 value="{{ category }}" />
  </p>

<table width=800 style='bottom: 0px;'>
<tr><td align=left>
  <button type="submit" name="not" style='height:40px;'>Infeasible</button>
</td>
<td align=right>
  <button type="submit" id="success" name="success" value="success" style='height: 40px;' disabled=true>Success!</button>
</td></tr>
</table>
  </form>
</body>
</html>
