var make_typeahead_tag = function(tag_id, hints){
  /*
    Create typeahead, where user can choose value from `hints` or ignore it
    and type its own.

    Arguments:
      - tag_id (str): ID of the tag.
      - hints (list): List of dicts which will be used for hints. Format is
                      {"source": "source of the hint", "val": value}
  */
  tag_passer = function(strs) {
    return function findMatches(q, cb) {
      cb(strs);
    }
  }

  $(tag_id + ' .typeahead').typeahead({
      hint: false,
      minLength: 0,
      highlight: false,
    }, {
      limit: 20,
      source: tag_passer(hints),
      display: function (item) { return item.val; },
      templates: {
          empty: "<p class='tt-footer'>Nic nenalezeno.</p>",
          suggestion: function(item) {
            if (item.source.length == 0)
              return "<p class='tt-item'>" + item.val + "</p>"; 

            return "<p class='tt-item'><b>" + item.source + ": </b>" + item.val + "</p>";
          },
          footer: function(query) {
            return "<p class='tt-footer'>Analyzátory nalezené hodnoty.</p>"
          },
      },
  });
}


var make_periode_typeahead_tag = function(tag_id, hints){
  /*
    Create typeahead for periodicity. User can choose value from `hints` or
    ignore it and type its own.

    Values are fuzzy matched using bloodhound.

    When there is no value, after focus first 20 is shown.

    Arguments:
      - tag_id (str): ID of the tag.
      - hints (list): List of dicts which will be used for hints. Format is
                      {"source": "source of the hint", "val": value}
  */
  // see http://bit.ly/1Q2pyb4 for details
  function search_with_defaults(q, sync) {
    searchEngine = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        local: hints
    });
    if (q === '') {
      sync(searchEngine.index.all());
    } else {
      searchEngine.search(q, sync);
    }
  }

  $(tag_id + ' .typeahead').typeahead({
      hint: true,
      minLength: 0,
      highlight: true,
    }, {
      limit: 20,
      source: search_with_defaults,
      templates: {
          // empty: "<p class='tt-foote;r'>Nic nenalezeno.</p>",
          suggestion: function(item) {
            return "<p class='tt-item'>" + item + "</p>"; 
          },
          footer: function(query) {
            return "<p class='tt-footer'>Často používané hodnoty periodicity.</p>"
          },
      },
  });

  $(tag_id + ' .typeahead').on( 'focus', function() {
    if($(this).val() === '') // you can also check for minLength
        $(this).data().ttTypeahead.input.trigger('queryChanged', '');
  });
}


var make_multi_searchable_typeahead_tag = function(){
  /*
    Create typeahead for conspect.

    Function expects following arguments:
      
      - tag_id (str): ID of the tag.
      - dataset1 (dict): {"name": "Name of dataset 1", "data": [..]}
      - datasetN (dict): {"name": "Name of dataset N", "data": [..]}
      - ...
  */

  // start with basic typeahead settings
  all_tags = new Array({
    hint: true,
    limit: 20,
    minLength: 0,
    highlight: true,
  });

  // first argument is the ID of the tag which will be converted to typeahead
  tag_id = arguments[0];

  // map arguments to `all_tags` array
  for (var i = 1; i < arguments.length; i++) {
    dataset = {
      source: new Bloodhound({
          datumTokenizer: Bloodhound.tokenizers.whitespace,
          queryTokenizer: Bloodhound.tokenizers.whitespace,
          local: arguments[i].data
      }),
      templates: {
        header: '<h4 class="conspect_name">' + arguments[i].name + '</h4>',
      }
    }

    all_tags.push(dataset);
  }

  // convert the tag to typeahead with multiple searchable data sources
  typeahead_tag = $(tag_id + ' .typeahead');
  typeahead_tag.typeahead.apply(typeahead_tag, all_tags);
}


var make_keyword_typeahead_tag = function(tag_id, source, callback) {
  /*
    This functions converts the <div><input> pair identified by `tag_id`
    to typehead dropdown searchable input using `source` as source for the
    searchable elements.

    Everytime the element is selected from the typeahead suggestions,
    `callback` is called.

    `callback` is expected to be function, which takes one argument (selected
    element as string) and return string, on which the typehead input will
    be set.

    `source` is expected to be JSON array of unicode strings.
  */

  // initialize search engine
  var keywords = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: source
  });

  // register the typeahead
  $(tag_id + ' .typeahead').typeahead({
      hint: false,
      minLength: 0,
      highlight: false,
    }, {
      limit: 20,
      source: keywords,
      templates: {
          empty: "<p class='tt-footer'>Psaním vyberete.</p>",
          suggestion: function(item) {
            return "<p class='tt-item'>" + item + "</p>";
          },
          footer: function(query) {
            return "<p class='tt-footer'>Možná klíčová slova.</p>"
          },
      },
  });

  // register the callback, which is called every time the item is selected
  $(tag_id + ' .typeahead').on(
    'typeahead:selected',
    function(ev, obj, dataset) {
      $(tag_id + ' .typeahead').typeahead('val', callback(obj));
    }
  );
}


var destroy_typyahead_tag = function(tag_id){
  /*
    Remove typeahead from the tag identified by `tag_id`.
  */
  $(tag_id + ' .typeahead').typeahead("destroy");
}
