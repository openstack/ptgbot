=================
OpenStack PTG Bot
=================

ptgbot is the bot that PTG room moderators use to surface what's
currently happening at the event. Commands follow the following format::

  #ROOMNAME [now|next] TOPIC

From that information the bot builds a static webpage with discussion
topics currently discussed ("now") and an indicative set of discussion
topics coming up next ("next").

Please note that:

* There can only be one "now" topic at a time. If multiple topics are
  discussed at the same time in various corners of the room, they should
  all be specified in a single "now" command.

* In order to ensure that information is current, entering a "now" command
  wipes out any "next" entry for the same room. You might want to refresh
  those after entering a "now" topic.

Example::

  #swift now discussing ring placement
  #swift next at 2pm we plan to discuss #glance support
  #swift next around 3pm we plan to cover cold storage features
  ...
  #swift now discussing #glance support, come over!
  #swift next at 3pm we plan to cover cold storage features


Testing
=======

Copy config.ini.sample to config.ini::

  cp config.ini.sample config.ini

Edit config.ini contents, for example::

  [ircbot]
  nick=ptgbot
  pass=
  server=irc.freenode.net
  port=6667
  channels=testptg
  db=html/ptg.json

In one terminal, run the bot::

  tox -evenv -- ptgbot -d config.ini

Join that channel and give a command to the bot::

  #swift now discussing ring placement

(note, the bot currently only takes commands from Freenode identified users)

In another terminal, start the webserver::

  cd html && python -m SimpleHTTPServer

Open the web page in a web browser: http://127.0.0.1:8000/ptg.html
