// sets variable source to the animalTemplate id in index.html
var source = document.getElementById("LinksTemplate").innerHTML;

// Handlebars compiles the above source into a template
var template = Handlebars.compile(source);

$.getJSON("ptg.json", function(json) {
  document.getElementById("ExtraLinks").innerHTML = template(json);
});
