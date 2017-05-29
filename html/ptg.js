// sets variable source to the animalTemplate id in index.html
var source = document.getElementById("PTGtemplate").innerHTML;

// Handlebars compiles the above source into a template
var template = Handlebars.compile(source);

Handlebars.registerHelper('hashtag', function(options) {
  var words = options.fn(this).split(" ");
  var sentence = "";
  for (var i = 0; i < words.length; i++) {
    if (words[i].startsWith("#")) {
        sentence += '<span class="label label-info">'
          + words[i].substring(1) + '</span> ';
    } else {
        sentence += words[i] + " ";
    }
  }
  return new Handlebars.SafeString(sentence);
});

$.getJSON("ptg.json", function(json) {
  console.log(json);
  document.getElementById("PTGsessions").innerHTML = template(json);
});
