$(function() {
  $(window)
    .on('showGrid', function(e, pos) {
      console.log('showGrid', pos);
    }).on('hideGrid', function() {
      console.log('hideGrid');
    }).on('showPhotoPreview', function(e, photo_id) {
      console.log('showPhotoPreview', photo_id);
    }).on('closePreviewPanel', function() {
      console.log('closePreviewPanel');
    }).on('openPreviewPanel', function() {
      console.log('openPreviewPanel');
    });
});
