function initMap() {
  const latLngFromSite = geolocation ? {lat: geolocation[0], lng: geolocation[1]} : null;
  const geocoder = new google.maps.Geocoder();
  var map = new google.maps.Map(document.getElementById('map'), {
    center: latLngFromSite || {lat: 40.74421, lng: -73.9737},
    zoom: latLngFromSite ? 15 : 13
  });
  var marker = null;
  var card = document.getElementById('pac-card');
  var input = document.getElementById('pac-input');

  function updateHiddenFieldWithLatLng(latLng) {
    var latLngStr = latLng.lat() + ',' + latLng.lng();
    var json = JSON.stringify({"latLng": latLngStr});
    document.getElementById('latLng').setAttribute('value', json);
    document.getElementById('loc-yes').setAttribute('checked', true);
  }

  function setMarkerLatLng(latLng) {
    marker.setPosition(latLng);
    marker.setMap(map);
    updateHiddenFieldWithLatLng(latLng);
  }

  map.controls[google.maps.ControlPosition.TOP_RIGHT].push(card);

  var autocomplete = new google.maps.places.Autocomplete(input);

  google.maps.event.addDomListener(input, 'keydown', function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
    }
  });

  // Bind the map's bounds (viewport) property to the autocomplete object,
  // so that the autocomplete requests use the current map bounds for the
  // bounds option in the request.
  autocomplete.bindTo('bounds', map);

  var infowindow = new google.maps.InfoWindow();
  var infowindowContent = document.getElementById('infowindow-content');
  infowindow.setContent(infowindowContent);

  marker = new google.maps.Marker({
    map: null,  // Hidden initially
    position: latLngFromSite || map.getCenter(),
    draggable: true,
    animation: google.maps.Animation.DROP
  });

  google.maps.event.addListener(marker, 'dragend', function() {
    updateHiddenFieldWithLatLng(marker.getPosition());
  });

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

    // If the place has a geometry, then present it on a map.
    if (place.geometry.viewport) {
      map.fitBounds(place.geometry.viewport);
    } else {
      map.setCenter(place.geometry.location);
      map.setZoom(17);  // Why 17? Because it looks good.
    }
    setMarkerLatLng(place.geometry.location);
  });

  document.querySelector('#loc-yes').addEventListener('change', () => {
    marker.setMap(map);
  });
  document.querySelector('#loc-maybe').addEventListener('change', () => {
    marker.setMap(null);
  });
  document.querySelector('#loc-no').addEventListener('change', () => {
    marker.setMap(null);
  })
}

(function() {
  // Hide empty bullets.
  const lis = document.querySelectorAll('#metadata li');
  for (const li of lis) {
    if (li.textContent === '') {
      li.parentNode.removeChild(li);
    }
    li.textContent = li.textContent.replace("Photographic views of New York City, 1870's-1970's", 'Photographic Views');
  }

  const metadata = document.querySelector('#metadata');
  for (const [k, v] of Object.entries(subject)) {
    if (v.length === 0) continue;
    const li = document.createElement('li');
    li.innerHTML = `subject/${k}`;
    const ul = document.createElement('ul');
    li.appendChild(ul);
    for (const item of v) {
      const li = document.createElement('li');
      li.innerHTML = item;
      ul.appendChild(li);
    }
    metadata.appendChild(li);
  }
})();

document.getElementById('submit').addEventListener('click', (event) => {
  const geolocatableIsSet = [
      ...document.querySelectorAll('#geolocatable-radio > input')
  ].reduce((acc, curr) => (acc ? acc : curr.checked), false);
  if (!geolocatableIsSet) {
    document.getElementById('loc-yes')
      .setCustomValidity('Must record whether this photo is geocodable or not.');
  } else {
    document.getElementById('loc-yes').setCustomValidity('')
  }
});
