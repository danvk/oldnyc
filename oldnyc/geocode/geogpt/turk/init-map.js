function initMap() {
  const geocoder = new google.maps.Geocoder();
  var map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 40.74421, lng: -73.9737},
    zoom: 13,
    gestureHandling: 'greedy'
  });
  const oldLatLng = {lat: old_lat_lng[0], lng: old_lat_lng[1]};
  const newLatLng = {lat: new_lat_lng[0], lng: new_lat_lng[1]};
  var markerOld = new google.maps.Marker({
    map,
    label: 'O',
    position: oldLatLng,
    background: '#FBBC04',
  });
  var markerNew = new google.maps.Marker({
    map,
    label: 'N',
    position: newLatLng,
  });
  const bounds = new google.maps.LatLngBounds();
  bounds.extend(oldLatLng);
  bounds.extend(newLatLng);
  map.fitBounds(bounds, 75);
}

(function() {
  document.getElementById('back-text').textContent = item_json.back_text || '';
  delete item_json.back_text;
  document.getElementById('item-json').textContent = JSON.stringify(item_json, null, 2);
  document.getElementById('gpt-before').textContent = JSON.stringify(old_gpt_json, null, 2);
  document.getElementById('gpt-after').textContent = JSON.stringify(new_gpt_json, null, 2);
})();
