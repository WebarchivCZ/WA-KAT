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

var destroy_typyahead_tag = function(tag_id){
  $(tag_id + ' .typeahead').typeahead("destroy");
}