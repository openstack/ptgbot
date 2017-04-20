=================
OpenStack PTG Bot
=================

ptgbot is the bot that PTG room moderators use to surface what's
currently happening at the event. It builds a static webpage that
attendees can query for up-to-date information.

Commands follow the following format:

@ROOMNAME [until|at] TIME TOPIC


Testing
=======

Copy config.ini.sample to config.ini:

  cp config.ini.sample config.ini

Edit config.ini contents, for example:

[ircbot]
nick=ptgbot
pass=
server=irc.freenode.net
port=6667
channels=testptg
db=html/ptg.json

In one terminal, run the bot:

  tox -evenv -- ptgbot -d config.ini

Join that channel and give a command to the bot:

  @swift until 10:00 Discussing ring internals

(note, the bot currently only takes commands from Freenode identified users)

In another terminal, start the webserver:

  cd html && python -m SimpleHTTPServer

Open the web page in a web browser:

  http://127.0.0.1:8000/ptg.html
