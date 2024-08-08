'use strict';

const knownCookies = {
  '54a2c38e-2dee-433f-90b9-db0741e571c1': 'DANVK'
};

var rejected_ids = [];
var review_ids = [];
var options = changes.map(function(change, idx) {
  var txt = (1 + idx) + '/' + changes.length + ': ' + change.photo_id;
  return $('<option>').val(idx).text(txt).get(0);
});
$('select').append(options);

function selectedIndex() {
  return $('select').find(':selected').index();
}

$('select').on('change', function(e) {
  buildUI(changes[selectedIndex()]);
});
$('#next').on('click', function(e) {
  var idx = selectedIndex();
  idx = (idx + 1) % changes.length;
  $('select').val(idx);
  buildUI(changes[idx]);
});
$('#prev').on('click', function(e) {
  var idx = selectedIndex();
  idx = (idx + changes.length - 1) % changes.length;
  $('select').val(idx);
  buildUI(changes[idx]);
});
$('#accept-all').on('click', function(e) {
  let idx = selectedIndex();
  const cookie = changes[idx].metadata.cookie;
  for (; idx < changes.length; idx++) {
    if (changes[idx].metadata.cookie !== cookie) {
      $('select').val(idx);
      buildUI(changes[idx]);
      break;
    }
  }
});
$('#reject-all').on('click', function(e) {
  alert('not implemented');
});

$('#reject').on('click', function(e) {
  rejected_ids.push(changes[selectedIndex()].photo_id);
  $('#next').click();
});

$('#review').on('click', function(e) {
  review_ids.push(changes[selectedIndex()].photo_id);
  $('#next').click();
});

$(window).on('keypress', function(e) {
  if (e.which == 'j'.charCodeAt(0)) {
    $('#next').click();
  } else if (e.which == 'k'.charCodeAt(0)) {
    $('#prev').click();
  } else if (e.which == 'x'.charCodeAt(0)) {
    $('#reject').click();
  } else if (e.which == 'a'.charCodeAt(0)) {
    $('#accept-all').click();
  } else if (e.which == 'r'.charCodeAt(0)) {
    $('#review').click();
  } else if (e.which == 'v'.charCodeAt(0)) {
    var url = $('#tool-link').attr('href');
    window.open(url, '_blank');
  }
});

// Returns [num, total], as in "Change 1 / 10" for this user.
function getCookieCounts(record) {
  let before = 0;
  let total = 0;
  let foundRecord = false;
  const cookie = record.metadata.cookie;
  changes.forEach(change => {
    const metadata = change.metadata;
    if (metadata.cookie !== cookie) return;

    if (!foundRecord) {
      before += 1;
    }
    if (record == change) {
      foundRecord = true;
    }
    total += 1;
  });

  return [before, total];
}

function buildUI(record) {
  var photo_id = record.photo_id;

  $('#photo-id').text(photo_id);
  $('#tool-link').attr('href', 'http://www.oldnyc.org/ocr.html#' + photo_id);

  $('#diff').empty().append(
    codediff.buildView(record.before || '', record.after, {}));

  const cookie = record.metadata.cookie;
  const user = knownCookies[cookie];
  const msg = user || 'this user';
  const [before, total] = getCookieCounts(record);
  $('#metadata').text(
      `Change ${before} / ${total} for ${msg}.\n` +
      JSON.stringify(record.metadata, null, '  '));

  $('#rejected-ids').text(rejected_ids.join(' '));
  $('#review-ids').text(review_ids.join(' '));
}

buildUI(changes[0]);
