// sets variable source to the animalTemplate id in index.html
var dsource = document.getElementById("MOTDTemplate").innerHTML;

// Handlebars compiles the above source into a template
var dtemplate = Handlebars.compile(dsource);

Handlebars.registerHelper('linkify', function(str) {
    var pattern1 = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    var str1 = str.replace(pattern1, '<a target="_blank" href="$1">$1</a>');
    var pattern2 =/(^|[^\/])(www\.[\S]+(\b|$))/gim;
    var str2 = str1.replace(pattern2, '$1<a target="_blank" href="http://$2">$2</a>');
    return new Handlebars.SafeString(str2);
});

$.getJSON("ptg.json", function(json) {
  document.getElementById("MOTD").innerHTML = dtemplate(json);
});
