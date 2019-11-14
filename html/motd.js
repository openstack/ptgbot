// sets variable source to the animalTemplate id in index.html
var dsource = document.getElementById("MOTDTemplate").innerHTML;

// Handlebars compiles the above source into a template
var dtemplate = Handlebars.compile(dsource);

$.getJSON("ptg.json", function(json) {
  document.getElementById("MOTD").innerHTML = dtemplate(json);
});
