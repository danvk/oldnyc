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
  });
  const bounds = new google.maps.LatLngBounds();
  if (centroid) {
    const centroidMarker = new google.maps.Marker({
      position: {lng: centroid[0], lat: centroid[1]},
      map,
      icon: selected_marker_icons[10],
    });
    bounds.extend(centroidMarker.getPosition());
  }
  for (const [lng, lat] of points) {
      const marker = new google.maps.Marker({
          position: {lng, lat},
          map: map,
          icon: marker_icons[1],
      });
      bounds.extend(marker.getPosition());
  }
  map.fitBounds(bounds);
  console.log(bounds.toString());
}

for (const example of examples) {
  const li = document.createElement('li');
  li.innerHTML = `
    <a href="${example.url}">${example.id}</a>: ${example.title}
  `;
  document.getElementById('examples').appendChild(li);
}
