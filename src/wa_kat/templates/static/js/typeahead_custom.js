var tag_passer = function(strs) {
  return function findMatches(q, cb) {
    cb(strs);
  };
};

var make_typeahead_tag = function(tag_id, hints){
  $(tag_id + ' .typeahead').typeahead({
      hint: true,
      highlight: true,
      minLength: 0
    }, {
      source: tag_passer(hints),
      limit: 20,
      templates: {
          suggestion: function(item) {
            return "<p style='margin: 0px'><b>DC: </b>" + item + "</p>";
          },
          footer: function(query) {
            return "<b>Analyzátory nalezené hodnoty.'</b>"
          }
      }
  });
}