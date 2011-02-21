<html>
<head>
  <title>SF Image Geocoding Game</title>
</head>
<body>
<h2>SF Image Geocoding Game</h2>
<p>Your cookie: <b>{{ cookie }}</b></p>

<img src="/image?id={{image.photo_id}}" />

<p>
<b>ID</b> {{ image.photo_id }}<br/>
<b>Title</b> {{ image.title }}<br/>
<b>Date</b> {{ image.date }}<br/>
<b>Location</b> {{ image.location }}<br/>
<b>Description</b><br/>
{{ image.description }}
</p>

</body>
</html>
