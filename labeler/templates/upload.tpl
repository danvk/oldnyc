<html>
<head>
  <title>SF Image Geocoding Game</title>
</head>
<body>
<h2>SF Image Geocoding Game</h2>
<p>Your cookie: <b>{{ cookie }}</b></p>

<form enctype="multipart/form-data" action="/upload" method="post">
ID: <input type=text name="id" size=20 /><br/>
Title: <input type=text name="title" size=50 /><br/>
Date: <input type=text name="date" size=30 /><br/>
Location: <input type=text name="location" size=50 /><br/>
Thumbnail URL: <input type=text name="thumbnail_url" size=50 /><br/>
Image: <input type=file name="image" /><br/>
Description: <br/>
<textarea name="description" rows=10 cols=50>
</textarea>

<p>
<input type="submit" value="Upload" />
</p>
</form>

</body>
</html>
