=================
OpenStack PTG Bot
=================

ptgbot is the bot that PTG room moderators use to surface what's
currently happening at the event. Room operators send messages to
the bot, like::

  #swift now discussing ring balancing

and from that information the bot builds a static webpage with discussion
topics currently discussed ("now") and an indicative set of discussion
topics coming up next ("next"). It also merges information from the
reservable rooms ethercalc in order to produce a single, static,
mobile-friendly page.

Room operators commands
=======================

You have to have voice in the channel (+v) to send commands to the ptgbot.
Commands follow the following format::

  #ROOMNAME [now|next] TOPIC
  #ROOMNAME [color] CSS_COLOR_SPECIFIER

Please note that:

* There can only be one "now" topic at a time. If multiple topics are
  discussed at the same time in various corners of the room, they should
  all be specified in a single "now" command.

* In order to ensure that information is current, entering a "now" command
  wipes out any "next" entry for the same room. You might want to refresh
  those after entering a "now" topic.

* The color command only sets the background color for the room
  name. The foreground is always white. Colors can be specified in any
  form supported by the CSS attribute background-color.

Example::

  #swift now discussing ring placement
  #swift color blue
  #swift next at 2pm we plan to discuss #glance support
  #swift next around 3pm we plan to cover cold storage features
  ...
  #swift now discussing #glance support, come over!
  #swift next at 3pm we plan to cover cold storage features
  ...
  #oslo now discussing oslo.config drivers
  #oslo location Level B, Ballroom A
  #oslo color #42f4c5
  #oslo next after lunch we plan to discuss auto-generating config reference docs

You can also remove all entries related to your room by issuing the following
command::

  #ROOMNAME clean


Admin commands
==============

You have to be a channel operator (+o) to use admin commands.

~list
  List available room names

~add ROOM [ROOM..]
  Add new room name(s)

~del ROOM [ROOM..]
  Deletes room name(s)

~clean ROOM [ROOM..]
  Removes active entries for specified room(s)

~wipe
  Resets the database entirely (removes all defined rooms and entries)


Local testing
=============

Copy config.json.sample to config.json::

  cp config.json.sample config.json

Edit config.json contents, for example::

  {
  "irc_nick": "ptgbot",
  "irc_server": "irc.freenode.net",
  "irc_port": 6667,
  "irc_channel": "#testptg",
  "db_filename": "html/ptg.json",
  }

In one terminal, run the bot::

  tox -evenv -- ptgbot -d config.json

Join that channel and give a command to the bot::

  #swift now discussing ring placement

(note, the bot currently only takes commands from Freenode identified users)

In another terminal, start the webserver::

  cd html && python -m SimpleHTTPServer

Open the web page in a web browser: http://127.0.0.1:8000/ptg.html
