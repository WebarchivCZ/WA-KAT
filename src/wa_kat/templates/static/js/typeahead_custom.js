var tag_passer = function(strs) {
  return function findMatches(q, cb) {
    cb(strs);
  };
};

var make_typeahead_tag = function(tag_id, hints){
  $(tag_id + ' .typeahead').typeahead({
      hint: false,
      minLength: 0,
      highlight: false,
    }, {
      limit: 20,
      source: tag_passer(hints),
      display: function (item) { return item.val; },
      templates: {
          empty: "<p class='tt-footer'>No results found.</p>",
          suggestion: function(item) {
            return "<p class='tt-item'><b>" + item.source + ": </b>" + item.val + "</p>";
          },
          footer: function(query) {
            return "<p class='tt-footer'>Analyzátory nalezené hodnoty.</p>"
          },
      },
  });
}

var make_multi_searchable_typeahead_tag  = function(){
  // start with basic typeahead settings
  all_tags = new Array({
    hint: true,
    minLength: 0,
    highlight: true,
  });

  // first argument is the ID of the tag which will be converted to typeahead
  tag_id = arguments[0];

  // map arguments to `all_tags` array
  for (var i = 1; i < arguments.length; i++) {
    dataset = {
      limit: 20,
      source: tag_passer(arguments[i].data),
      templates: {
        header: '<h3 class="conspect_name">' + arguments[i].name + '</h3>',
      }
    }

    all_tags.push(dataset);
  }

  // convert the tag to typeahead with multiple searchable data sources
  typeahead_tag = $(tag_id + ' .typeahead');
  typeahead_tag.typeahead.apply(typeahead_tag, all_tags);
}

var destroy_typyahead_tag = function(tag_id){
  $(tag_id + ' .typeahead').typeahead("destroy");
}