/*
* debouncedresize: special jQuery event that happens once after a window resize
*
* latest version and complete README available on Github:
* https://github.com/louisremi/jquery-smartresize/blob/master/jquery.debouncedresize.js
*
* Copyright 2011 @louis_remi
* Licensed under the MIT license.
*/
var $event = $.event,
$special,
resizeTimeout;

$special = $event.special.debouncedresize = {
  setup: function() {
    $( this ).on( "resize", $special.handler );
  },
  teardown: function() {
    $( this ).off( "resize", $special.handler );
  },
  handler: function( event, execAsap ) {
    // Save the context
    var context = this,
      args = arguments,
      dispatch = function() {
        // set correct event type
        event.type = "debouncedresize";
        $event.dispatch.apply( context, args );
      };

    if ( resizeTimeout ) {
      clearTimeout( resizeTimeout );
    }

    execAsap ?
      dispatch() :
      resizeTimeout = setTimeout( dispatch, $special.threshold );
  },
  threshold: 250
};

/*
 * throttledresize: special jQuery event that happens at a reduced rate compared to "resize"
 *
 * latest version and complete README available on Github:
 * https://github.com/louisremi/jquery-smartresize
 *
 * Copyright 2012 @louis_remi
 * Licensed under the MIT license.
 *
 * This saved you an hour of work? 
 * Send me music http://www.amazon.co.uk/wishlist/HNTU0468LQON
 */
(function($) {

var $event = $.event,
	$special,
	dummy = {_:0},
	frame = 0,
	wasResized, animRunning;

$special = $event.special.throttledresize = {
	setup: function() {
		$( this ).on( "resize", $special.handler );
	},
	teardown: function() {
		$( this ).off( "resize", $special.handler );
	},
	handler: function( event, execAsap ) {
		// Save the context
		var context = this,
			args = arguments;

		wasResized = true;

		if ( !animRunning ) {
			setInterval(function(){
				frame++;

				if ( frame > $special.threshold && wasResized || execAsap ) {
					// set correct event type
					event.type = "throttledresize";
					$event.dispatch.apply( context, args );
					wasResized = false;
					frame = 0;
				}
				if ( frame > 9 ) {
					$(dummy).stop();
					animRunning = false;
					frame = 0;
				}
			}, 30);
			animRunning = true;
		}
	},
	threshold: 0
};

})(jQuery);

// ======================= imagesLoaded Plugin ===============================
// https://github.com/desandro/imagesloaded

// $('#my-container').imagesLoaded(myFunction)
// execute a callback when all images have loaded.
// needed because .load() doesn't work on cached images

// callback function gets image collection as argument
//  this is the container

// original: MIT license. Paul Irish. 2010.
// contributors: Oren Solomianik, David DeSandro, Yiannis Chatzikonstantinou

// blank image data-uri bypasses webkit log warning (thx doug jones)
var BLANK = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==';

$.fn.imagesLoaded = function( callback ) {
  var $this = this,
    deferred = $.isFunction($.Deferred) ? $.Deferred() : 0,
    hasNotify = $.isFunction(deferred.notify),
    $images = $this.find('img').add( $this.filter('img') ),
    loaded = [],
    proper = [],
    broken = [];

  // Register deferred callbacks
  if ($.isPlainObject(callback)) {
    $.each(callback, function (key, value) {
      if (key === 'callback') {
        callback = value;
      } else if (deferred) {
        deferred[key](value);
      }
    });
  }

  function doneLoading() {
    var $proper = $(proper),
      $broken = $(broken);

    if ( deferred ) {
      if ( broken.length ) {
        deferred.reject( $images, $proper, $broken );
      } else {
        deferred.resolve( $images );
      }
    }

    if ( $.isFunction( callback ) ) {
      callback.call( $this, $images, $proper, $broken );
    }
  }

  function imgLoaded( img, isBroken ) {
    // don't proceed if BLANK image, or image is already loaded
    if ( img.src === BLANK || $.inArray( img, loaded ) !== -1 ) {
      return;
    }

    // store element in loaded images array
    loaded.push( img );

    // keep track of broken and properly loaded images
    if ( isBroken ) {
      broken.push( img );
    } else {
      proper.push( img );
    }

    // cache image and its state for future calls
    $.data( img, 'imagesLoaded', { isBroken: isBroken, src: img.src } );

    // trigger deferred progress method if present
    if ( hasNotify ) {
      deferred.notifyWith( $(img), [ isBroken, $images, $(proper), $(broken) ] );
    }

    // call doneLoading and clean listeners if all images are loaded
    if ( $images.length === loaded.length ){
      setTimeout( doneLoading );
      $images.unbind( '.imagesLoaded' );
    }
  }

  // if no images, trigger immediately
  if ( !$images.length ) {
    doneLoading();
  } else {
    $images.bind( 'load.imagesLoaded error.imagesLoaded', function( event ){
      // trigger imgLoaded
      imgLoaded( event.target, event.type === 'error' );
    }).each( function( i, el ) {
      var src = el.src;

      // find out if this image has been already checked for status
      // if it was, and src has not changed, call imgLoaded on it
      var cached = $.data( el, 'imagesLoaded' );
      if ( cached && cached.src === src ) {
        imgLoaded( el, cached.isBroken );
        return;
      }

      // if complete is true and browser supports natural sizes, try
      // to check for image status manually
      if ( el.complete && el.naturalWidth !== undefined ) {
        imgLoaded( el, el.naturalWidth === 0 || el.naturalHeight === 0 );
        return;
      }

      // cached images don't fire load sometimes, so we reset src, but only when
      // dealing with IE, or image is complete (loaded) and failed manual check
      // webkit hack from http://groups.google.com/group/jquery-dev/browse_thread/thread/eee6ab7b2da50e1f
      if ( el.readyState || el.complete ) {
        el.src = BLANK;
        el.src = src;
      }
    });
  }

  return deferred ? deferred.promise( $this ) : $this;
};

var Grid = (function() {

    // list of items
  var $grid = null,
    // the items
    $items = null,
    // current expanded item's index
    current = -1,
    // position (top) of the expanded item
    // used to know if the preview will expand in a different row
    previewPos = -1,
    // extra amount of pixels to scroll the window
    scrollExtra = 0,
    // extra margin when expanded (between preview overlay and the next items)
    marginExpanded = 10,
    $window = $( window ), winsize,
    $body = $( 'html, body' ),
    // transitionend events
    transEndEventNames = {
      'WebkitTransition' : 'webkitTransitionEnd',
      'MozTransition' : 'transitionend',
      'OTransition' : 'oTransitionEnd',
      'msTransition' : 'MSTransitionEnd',
      'transition' : 'transitionend'
    },
    transEndEventName = transEndEventNames[ Modernizr.prefixed( 'transition' ) ],
    // support for csstransitions
    support = Modernizr.csstransitions,
    // default settings
    settings = {
      minHeight : 500,
      speed : 350,
      easing : 'ease'
    };

  function init( grid, config ) {
                $grid = $(grid);
                $items = $grid.children('li');

    // the settings..
    settings = $.extend( true, {}, settings, config );

    // preload all images
    $grid.imagesLoaded( function() {

      // save item´s size and offset
      saveItemInfo( true );
      // get window´s size
      getWinSize();
      // initialize some events
      initEvents();

    } );

  }

  // add more items to the grid.
  // the new items need to appended to the grid.
  // after that call Grid.addItems(theItems);
  function addItems( $newitems ) {

    $items = $items.add( $newitems );

    $newitems.each( function() {
      var $item = $( this );
      $item.data( {
        offsetTop : $item.offset().top,
        height : $item.height()
      } );
    } );

    initItemsEvents( $newitems );

  }

  // saves the item´s offset top and height (if saveheight is true)
  function saveItemInfo( saveheight ) {
    $items.each( function() {
      var $item = $( this );
      $item.data( 'offsetTop', $item.offset().top );
      if( saveheight ) {
        $item.data( 'height', $item.height() );
      }
    } );
  }

  function initEvents() {
    
    // when clicking an item, show the preview with the item´s info and large image.
    // close the item if already expanded.
    // also close if clicking on the item´s cross
    initItemsEvents( $items );
    
    // on window resize get the window´s size again
    // reset some values..
    $window.on( 'debouncedresize', function() {
      
      scrollExtra = 0;
      previewPos = -1;
      // save item´s offset
      saveItemInfo();
      getWinSize();
      var preview = $.data( this, 'preview' );
      if( typeof preview != 'undefined' ) {
        hidePreview();
      }

    } );

  }

  function initItemsEvents( $items ) {
    $items.on( 'click', 'span.og-close', function() {
      hidePreview();
      return false;
    } ).children( 'a' ).on( 'click', function(e) {

      var $item = $( this ).parent();
      // check if item already opened
      current === $item.index() ? hidePreview() : showPreview( $item );
      return false;

    } );
  }

  function getWinSize() {
    winsize = { width : $window.width(), height : $window.height() };
  }

  function showPreview( $item ) {
    var preview = $.data( this, 'preview' ),
      // item´s offset top
      position = $item.data( 'offsetTop' );

    scrollExtra = 0;

    // if a preview exists and previewPos is different (different row) from item´s top then close it
    if( typeof preview != 'undefined' ) {

      // not in the same row
      if( previewPos !== position ) {
        // if position > previewPos then we need to take te current preview´s height in consideration when scrolling the window
        if( position > previewPos ) {
          scrollExtra = preview.height;
        }
        hidePreview();
      }
      // same row
      else {
        preview.update( $item );
        return false;
      }
      
    }

    // update previewPos
    previewPos = position;
    // initialize new preview for the clicked item
    preview = $.data( this, 'preview', new Preview( $item ) );
    // expand preview overlay
    preview.open();

  }

  function hidePreview() {
    current = -1;
    var preview = $.data( this, 'preview' );
    preview.close();
    $.removeData( this, 'preview' );
  }

  // the preview obj / overlay
  function Preview( $item ) {
    this.$item = $item;
    this.expandedIdx = this.$item.index();
    this.create();
    this.update();
  }

  Preview.prototype = {
    create : function() {
      // create Preview structure:
      this.$details = $( '#og-details-template' ).clone().removeAttr('id').show();
      this.$loading = $( '<div class="og-loading"></div>' );
      this.$fullimage = $( '<div class="og-fullimg"></div>' ).append( this.$loading );
      this.$closePreview = $( '<span class="og-close"></span>' );
      this.$previewInner = $( '<div class="og-expander-inner"></div>' ).append( this.$closePreview, this.$fullimage, this.$details );
      this.$previewLeft = $('<div class="og-previous">&lt;</div>');
      this.$previewRight = $('<div class="og-next">&gt;</div>');
      this.$previewEl = $( '<div class="og-expander"></div>' ).append( this.$previewInner, this.$previewLeft, this.$previewRight );
      // append preview element to the item
      this.$item.append( this.getEl() );
      // set the transitions for the preview and the item
      if( support ) {
        this.setTransition();
      }
    },

    update : function( $item ) {

      if( $item ) {
        this.$item = $item;
      }
      
      // if already expanded remove class "og-expanded" from current item and add it to new item
      // $('.og-grid li').removeClass('og-expanded');
      if( current !== -1 ) {
        var $currentItem = $items.eq( current );
        $currentItem.removeClass( 'og-expanded' );
        this.$item.addClass( 'og-expanded' );
        // position the preview correctly
        this.positionPreview();
      }

      // update current value
      current = this.$item.index();

      // update preview´s content
      var $itemEl = this.$item.children( 'a' ),
        eldata = {
          largesrc : $itemEl.data( 'largesrc' ),
        };

      $(this.$item).trigger('og-select', this.$details);

      var self = this;
      
      // remove the current image in the preview
      if( typeof self.$largeImg != 'undefined' ) {
        self.$largeImg.remove();
      }

      // preload large image and add it to the preview
      // for smaller screens we don´t display the large image (the media query will hide the fullimage wrapper)
      if( self.$fullimage.is( ':visible' ) ) {
        this.$loading.show();
        $( '<img/>' ).load( function() {
          var $img = $( this );
          if( $img.attr( 'src' ) === self.$item.children('a').data( 'largesrc' ) ) {
            self.$loading.hide();
            self.$fullimage.find( 'img' ).remove();
            self.$largeImg = $img.fadeIn( 350 );
            self.$fullimage.append( self.$largeImg );
          }
        } ).attr( 'src', eldata.largesrc );  
      }

    },

    // Open the preview pane
    open : function() {
      setTimeout( $.proxy( function() {  
        // set the height for the preview and the item
        this.setHeights();
        // scroll to position the preview in the right place
        this.positionPreview();
      }, this ), 25 );

      var self = this;
      $('.og-previous, .og-next').on('click', function() {
        // XXX not quite working... maybe just click the images?
        if ($(this).is('.og-previous')) {
          if (current > 0) {
            current--;
            var $li = $items.eq(current);
            self.update($li);
            // showPreview($li);
          }
        } else {
          if (current < $items.length) {
            current++;
            var $li = $items.eq(current);
            self.update($li);
            // showPreview($li);
          }
        }
      });
    },

    // Close the preview pane
    close : function() {
      $('.og-previous, .og-next').off('click');

      var self = this,
        onEndFn = function() {
          self.$item.removeClass( 'og-expanded' );
          self.$item.css('height', '');
          self.$previewEl.remove();
        };

      setTimeout( $.proxy( function() {

        if( typeof this.$largeImg !== 'undefined' ) {
          this.$largeImg.fadeOut( 'fast' );
        }
        this.$previewEl.css( 'height', 0 );
        // the current expanded item (might be different from this.$item)
        var $expandedItem = $items.eq( this.expandedIdx );
        $expandedItem.css( 'height', $expandedItem.data( 'height' ) ).one( transEndEventName, onEndFn );

        if( !support ) {
          onEndFn.call();
        }

      }, this ), 25 );
      
      return false;

    },
    calcHeight : function() {

      var heightPreview = winsize.height - this.$item.data( 'height' ) - marginExpanded,
        itemHeight = winsize.height;

      if( heightPreview < settings.minHeight ) {
        heightPreview = settings.minHeight;
        itemHeight = settings.minHeight + this.$item.data( 'height' ) + marginExpanded;
      }

      this.height = heightPreview;
      this.itemHeight = itemHeight;

    },
    setHeights : function() {

      var self = this,
        onEndFn = function() {
          self.$item.addClass( 'og-expanded' );
        };

      this.calcHeight();
      this.$previewEl.css( 'height', this.height );
      this.$item
        .css( 'height', this.itemHeight )
        .one( transEndEventName, onEndFn );

      if( !support ) {
        onEndFn.call();
      }

    },
    positionPreview : function() {

      // scroll page
      // case 1 : preview height + item height fits in window´s height
      // case 2 : preview height + item height does not fit in window´s height and preview height is smaller than window´s height
      // case 3 : preview height + item height does not fit in window´s height and preview height is bigger than window´s height
      var position = this.$item.data( 'offsetTop' ),
        previewOffsetT = this.$previewEl.offset().top - scrollExtra,
        scrollVal = this.height + this.$item.data( 'height' ) + marginExpanded <= winsize.height ? position : this.height < winsize.height ? previewOffsetT - ( winsize.height - this.height ) : previewOffsetT;
      
      $body.animate( { scrollTop : scrollVal }, settings.speed );

    },
    setTransition  : function() {
      this.$previewEl.css( 'transition', 'height ' + settings.speed + 'ms ' + settings.easing );
      this.$item.css( 'transition', 'height ' + settings.speed + 'ms ' + settings.easing );
    },
    getEl : function() {
      return this.$previewEl;
    }
  }

  return { 
    init : init,
    addItems : addItems
  };

})();

(function($) {

  var imageMargin = 12;  // TODO(danvk): measure this.

// Returns an array of { height: XXX, images: [] }
// Each entry in images should have a height/width data field.
// TODO(danvk): could just return {height, startIndex, limitIndex} objects.
function partitionIntoRows(images, containerWidth) {
  var rows = [];
  var currentRow = [];
  $.each(images, function(i, image) {
    currentRow.push(image);
    var denom = 0;
    $.each(currentRow, function(_, image) {
      denom += $(image).data('eg-width') / $(image).data('eg-height');
    });
    var height = (containerWidth - imageMargin * currentRow.length) / denom;
    if (height < rowHeight) {
      rows.push({ height: height, images: currentRow });
      currentRow = [];
    }
  });
  if (currentRow.length > 0) {
    rows.push({ height: rowHeight, images: currentRow });
  }
  return rows;
}


function flowImages(lis, width) {
  var rows = partitionIntoRows(lis, width);
  $.each(rows, function(_, row) {
    var height = Math.round(row.height);
    $.each(row.images, function(_, li) {
      var imgW = $(li).data('eg-width'),
          imgH = $(li).data('eg-height');
      $(li).find('img').attr({
        'width': Math.floor(imgW * (height / imgH)),
        'height': height
      });
    });
    // line wrap happens naturally here.
  });
}

/**
 * options = {
 *   maxRowHeight: NNN
 * }
 * images = [ { src: "", width: M, height: N, largesrc: "", id: "" }, ... ]
 */
$.fn.expandableGrid = function(options, images) {
  var lis = $.map(images, function(image) {
    var $li = $('<li><a><img /></a></li>');
    $li.find('img').attr({
      'src': image.src,
    });
    $li.find('a').attr({
      'data-largesrc': image.largesrc,
      'data-title': 'title',
      'data-description': 'description',
      'href': '#'
    });
    if (image.hasOwnProperty('id')) {
      $li.data('image-id', image.id);
    }
    $li.data({
      'eg-width': image.width,
      'eg-height': image.height
    });
    return $li.get(0);
  });

  var $ul = $('<ul class=og-grid>').append($(lis).hide());
  $ul.appendTo(this.empty());
  flowImages(lis, $(this).width());
  $(lis).show();

  Grid.init($ul.get(0));

  return this;
};

$(window).on('resize', function( event ) {
  $('ul.og-grid').each(function(_, ul) {
    flowImages($(ul).find('li'), $(ul).width());
  });
});

})(jQuery);
