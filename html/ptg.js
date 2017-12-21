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

// What is the day today ?
var now = new Date();
var days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
var day = days[ now.getDay() ];

$.getJSON("ptg.json", function(json) {
  document.getElementById("PTGsessions").innerHTML = template(json);
  // if the current day doesn't exist, default to first existing one
  if ($('#st'+day).length == 0) {
      for (var i = 0; i < days.length; i++) {
          if ($('#st'+days[i]).length) {
              day = days[i];
              break;
          }
      }
  }
  $('#st'+day).tab('show');
  $('#at'+day).tab('show');
});
