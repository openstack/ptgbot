// sets variable source to the animalTemplate id in index.html
var source = document.getElementById("PTGtemplate").innerHTML;

// Handlebars compiles the above source into a template
var template = Handlebars.compile(source);

Handlebars.registerHelper('trackContentLine', function(options) {
  var words = options.fn(this).split(" ");
  var sentence = "";
  for (var i = 0; i < words.length; i++) {
    if (words[i].startsWith("#")) {
        sentence += '<span class="label label-info">'
          + words[i].substring(1) + '</span>';
    } else if (words[i].match(/^https?:\/\//)) {
        sentence += '<a href="' + words[i] + '">'
          + words[i] + '</a>';
    } else {
        sentence += words[i];
    }
    sentence += ' ';
  }
  return new Handlebars.SafeString(sentence);
});

Handlebars.registerHelper('roomactive',
                          function(schedule, room, times) {
  for (var i=0; i<times.length; i++) {
    if (schedule[room][times[i]['name']] != undefined) {
      return true;
    }
  }
  return false;
});

Handlebars.registerHelper('checkins', function(track) {
  return checkins_count(track);
});
Handlebars.registerHelper('checkedin', function(track) {
  return checkins_tooltip(track);
});

function checkins_count(track) {
  var room_checkins = checkins['#' + track];
  return room_checkins ? Object.keys(room_checkins).length : 0;
}

function checkins_tooltip(track) {
  var room_checkins = checkins['#' + track];
  if (room_checkins) {
    var attendees = room_checkins.map(function(checkin) {
      return checkin.nick;
    }).sort();
    return 'Checked in here: ' + attendees.join(", ");
  } else {
    return "No one is checked in here. " +
      "DM the bot 'in #" + track + "' to check in.";
  }
}

function track_badge(track, roomurl) {
  var title = checkins_tooltip(track);
  if (roomurl != undefined) {
    title = "Click here to join the meeting";
    return '<a target="_blank" href="' + roomurl +
    '" class="btn btn-xs btn-primary ' +
    track +
    '" title="' + title + '">' + track;
  }
  return '<span class="label label-primary ' +
    track +
    '" title="' + title + '">' + track;
}

Handlebars.registerHelper('trackbadge',
                          function(urls, locations, schedule, track) {
  if (urls[track] != undefined) {
    roomurl = urls[track];
  } else {
    if (locations[track] != undefined) {
        roomurl = schedule[locations[track]]['url'];
    } else {
        roomurl = undefined;
    }
  }
  return new Handlebars.SafeString(track_badge(track, roomurl));
});

Handlebars.registerHelper('roomcode',
                          function(urls, schedule, room, timecode, s) {
  var cell = '';
  if (schedule[room][timecode] != undefined) {
    if (schedule[room][timecode] == "") {
      if (s == 1) {
        cell = '<small><i>Available for booking</i></small>';
      } else {
        cell = '<small><i>' + room + "-" + timecode + '</i></small>';
      }
    } else {
      if (urls[schedule[room][timecode]] != undefined) {
          url = urls[schedule[room][timecode]];
      } else {
          url = schedule[room]['url']
      }
      cell = track_badge(schedule[room][timecode], url);
    }
  }
  return new Handlebars.SafeString(cell);
});

Handlebars.registerHelper('displaytime',
                          function(time) {
  if (time['realtime'] != undefined) {
    var t = new Date(time['realtime']);
    content = '<a target="_blank" href="' +
        'https://www.timeanddate.com/worldclock/fixedtime.html?iso=' +
        time['realtime'] + '" title="' + t + '">' +
        time['desc'] +'</a>';
  } else {
    content = time['desc'];
  }
  return new Handlebars.SafeString(content);
});

// Grey out cell if current time matches the slot hour
Handlebars.registerHelper('activetime',
                          function(time) {
  if (time['realtime'] != undefined) {
    var t = new Date(time['realtime']);
    var now = new Date();
    var diff = now.getTime() - t.getTime();
    if (diff > 0 && diff < (1000*60*60)) {
        return new Handlebars.SafeString('style="background-color: #eeeeee"');
    }
  }
  return new Handlebars.SafeString('');
});

// What is the day today ?
// Return Monday until Tuesday 1 UTC
var now = new Date();
now.setHours(now.getHours()-1);
var days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
var day = days[ now.getUTCDay() ];
var checkins = {};

$.getJSON("ptg.json", function(json) {
  if ('last_check_in' in json) {
    // Compile lists of who's checked into each location
    for (var attendee in json['last_check_in']) {
      var checkin = json['last_check_in'][attendee];
      if (checkin.location) {
        if (checkin['in'] && ! checkin['out']) {
          if (! (checkin.location in checkins)) {
            checkins[checkin.location] = [];
          }
          checkins[checkin.location].push(checkin);
        }
      }
    }
  }
  json['checkins'] = checkins;
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
