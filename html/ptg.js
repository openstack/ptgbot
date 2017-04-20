// sets variable source to the animalTemplate id in index.html
var source = document.getElementById("PTGtemplate").innerHTML;

// Handlebars compiles the above source into a template
var template = Handlebars.compile(source);

$.getJSON("ptg.json", function(json) {
  console.log(json);
  document.getElementById("PTGsessions").innerHTML = template(json);
});
