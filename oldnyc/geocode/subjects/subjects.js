function initMap() {
  // Create marker icons for each number.
  const marker_icons = [];
  const selected_marker_icons = [];
  marker_icons.push(null); // it's easier to be 1-based.
  selected_marker_icons.push(null); // it's easier to be 1-based.

  for (let i = 0; i < 100; i++) {
    const num = i + 1;
    const size = num == 1 ? 9 : 13;
    const selectedSize = num == 1 ? 15 : 21;
    marker_icons.push({
      url: 'sprite-2014-08-29.png',
      size: new google.maps.Size(size, size),
      origin: new google.maps.Point((i % 10) * 39, Math.floor(i / 10) * 39),
      anchor: new google.maps.Point((size - 1) / 2, (size - 1) / 2),
    });
    selected_marker_icons.push({
      url: 'selected-2014-08-29.png',
      size: new google.maps.Size(selectedSize, selectedSize),
      origin: new google.maps.Point((i % 10) * 39, Math.floor(i / 10) * 39),
      anchor: new google.maps.Point(
        (selectedSize - 1) / 2,
        (selectedSize - 1) / 2,
      ),
    });
  }

  const map = new google.maps.Map(document.getElementById("map"), {
      center: {lat: 40.74421, lng: -73.9737},
      zoom: centroid ? 17 : 13,
      gestureHandling: 'greedy',
  });
  let centroidMarker = new google.maps.Marker({
    position: {lat: 40.74421, lng: -73.9737},
    map: null,
    icon: selected_marker_icons[10],
    draggable: true,
    animation: google.maps.Animation.DROP
  });
  function setMarkerLatLng(latLng /* [lng, lat] */) {
    if ('lat' in latLng) {
      latLng = [latLng.lng(), latLng.lat()];
    }
    centroidMarker.setPosition({lng: latLng[0], lat: latLng[1]});
    centroidMarker.setMap(map);
    document.getElementById('latlng').setAttribute('value', JSON.stringify(latLng));
  }
  if (centroid) {
    setMarkerLatLng(centroid);
  }
  google.maps.event.addListener(centroidMarker, 'dragend', function() {
    const pos = marker.getPosition();
    document.getElementById('latlng').setAttribute('value', JSON.stringify([pos.lng(), pos.lat()]));
  });

  let bounds;
  for (const example of examples) {
      const {geocode} = example;
      if (!geocode) continue;
      // TODO: group by lng/lat and use appropriate marker icon.
      const [lng, lat] = geocode;
      const marker = new google.maps.Marker({
          position: {lng, lat},
          map: map,
          icon: marker_icons[1],
          title: example.id,
      });
      bounds ||= new google.maps.LatLngBounds();
      bounds.extend(marker.getPosition());
      google.maps.event.addListener(marker, 'click', function() {
        console.log(example.id);
        document.querySelectorAll('.selected').forEach((el) => el.classList.remove('selected'));
        document.querySelector(`[data-id="${example.id}"]`).classList.add('selected');
      });
  }
  if (bounds) {
    map.fitBounds(bounds);
  }

  const input = document.getElementById('pac-input');
  const autocomplete = new google.maps.places.Autocomplete(input);
  input.addEventListener('keydown', function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
    }
  });
  autocomplete.bindTo('bounds', map);
  var infowindow = new google.maps.InfoWindow();
  var infowindowContent = document.getElementById('infowindow-content');
  infowindow.setContent(infowindowContent);
  autocomplete.addListener('place_changed', function() {
    infowindow.close();
    var place = autocomplete.getPlace();
    if (!place.geometry) {
      // User entered the name of a Place that was not suggested and
      // pressed the Enter key, or the Place Details request failed.
      geocoder.geocode({
        address: place.name,
        componentRestrictions: {
          country: 'US',
          administrativeArea: 'NY',
          locality: 'New York City'
        }
      }, function(results, status) {
        console.log(status, results);
        const geometry = results[0].geometry;
        if (geometry) {
          setMarkerLatLng(geometry.location);
          map.fitBounds(geometry.viewport);
        }
      });
      // window.alert("No details available for input: '" + place.name + "'");
      return;
    }
    console.log(place);

    // If the place has a geometry, then present it on a map.
    if (place.geometry.viewport) {
      map.fitBounds(place.geometry.viewport);
    } else {
      map.setCenter(place.geometry.location);
      map.setZoom(17);  // Why 17? Because it looks good.
    }
    setMarkerLatLng(place.geometry.location);
  });
}

for (const example of examples) {
  const li = document.createElement('li');
  li.innerHTML = `
    <a href="${example.url}">${example.id}</a>: ${example.title}
  `;
  li.setAttribute('data-id', example.id);
  if (example.geocode) {
    li.classList.add('geocoded');
  }
  document.getElementById('examples').appendChild(li);
}
