$(function() {
  $(window)
    .on('showGrid', function(e, pos) {
      console.log('showGrid', pos);
    }).on('hideGrid', function() {
      console.log('hideGrid');
    })
});
