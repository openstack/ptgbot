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

Handlebars.registerHelper('roomactive',
                          function(scheduled, additional, room, times) {
  for (var i=0; i<times.length; i++) {
    if (scheduled[room][times[i]] != "") {
      return true;
    }
    if (additional[room]) {
      if (additional[room][times[i]['name']] != undefined) {
        return true;
      }
    }
  }
  return false;
});

Handlebars.registerHelper('roomcode',
                          function(scheduled, additional, room, timecode, s) {
  var cell = '';
  content = scheduled[room][timecode];
  if ((content != undefined) && (content != '')) {
    cell = '<span class="label label-primary ' + scheduled[room][timecode] +
           '">' + scheduled[room][timecode];
    return new Handlebars.SafeString(cell);
  } else {
    if (additional[room]) {
      console.log(additional[room][timecode]);
      if (additional[room][timecode] != undefined) {
        if (additional[room][timecode] == "") {
          if (s == 1) {
            cell = '<small><i>Available for booking</i></small>';
          } else {
            cell = '<small><i>' + room + "-" + timecode + '</i></small>';
          }
        } else {
          cell = '<span class="label label-primary ' +
                 additional[room][timecode] +
                 '">' + additional[room][timecode];
        }
      }
    }
  }
  return new Handlebars.SafeString(cell);
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
