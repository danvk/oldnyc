function getCanonicalUrlForPhoto(photo_id) {
  var base_url = document.location.href.replace(/#[^#]*/, '') + '#';
  return base_url + photo_id;
}

function getCommentCount(photo_ids) {
  // There is a batch API:
  // https://developers.facebook.com/docs/graph-api/making-multiple-requests/
  return $.get('https://graph.facebook.com/', {
      'ids': $.map(photo_ids, function(id) {
          return getCanonicalUrlForPhoto(id);
      }).join(',')
  }).then(function(obj) {
    // obj is something like {url: {'id', 'shares', 'comments'}}
    // convert it to {id: comments}
    var newObj = {};
    $.each(obj, function(url, data) {
      newObj[url.replace(/.*#/, '')] = data['comments'] || 0;
    });
    return newObj;
  });
}
