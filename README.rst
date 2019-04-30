===========================
Open Infrastructure PTG Bot
===========================

ptgbot is the bot that PTG track moderators use to surface what's
currently happening at the event. Track moderators send messages to
the bot, and from that information the bot builds a static webpage
with several sections of information:

* The discussion topics currently discussed ("now")
* An indicative set of discussion topics coming up next ("next")
* The tracks pre-scheduled for the day
* The tracks which booked available slots in the additional rooms

The bot also allows people to voluntarily check into (and out of)
tracks or other arbitrary locations, if they want to be found more
easily by other people.


User commands
=============

Anyone can privately message the bot with the following commands:

* ``in #TRACKNAME`` - tells the bot you are currently in the track
  named ``TRACKNAME``.  This must be one of the tracks it knows about,
  for example: ``in #nova``

* ``in LOCATION`` - tells the bot you are currently in a location
  which doesn't correspond to any track.  This can be any freeform
  text, for example: ``in the pub``

* ``out`` - tells the bot you've checked out of your current location.
  However others will still be able to see when and where you checked
  out.

* ``seen NICK`` - asks the bot where the user with the given IRC nick
  was last seen (if anywhere).  The nick is case-insensitive.

* ``subscribe REGEXP`` - subscribes for a direct message notification
  from the bot whenever a topic with a substring matching ``REGEXP``
  is set via the ``now`` or ``next`` commands (see below).  The exact
  string the (case-insensitive) regular expression will be matched
  against is of the form ``#track now topic`` (i.e. the same as the
  full commands issued by track moderators).  So for example
  ``subscribe #nova.*test|python *3`` would match any testing topics
  in the nova track, and any Python 3 topics in any track.

* ``subscribe`` - shows your current subscription regular expression
  (if any)

* ``unsubscribe`` - cancels your current subscription (if any)

The above commands also work in the channel when prefixed with ``#``,
for example ``#in the pub``.  You can use the ``#`` prefix with
private messages to the bot too, in case you don't want to memorise
different syntax for these commands depending on whether you are
messaging the bot privately or in a channel.


Track moderators commands
=========================

By default the bot allows anyone in the channel to issue track moderation
commands. However note that it is possible for admins to restrict access
to people who have voice in the channel (+v).

Commands follow the following format::

  #TRACKNAME COMMAND [PARAMETERS]

Here is the list of available commands.

now
---

The ``now`` command indicates the current topic of discussion in a given
track. Example usage::

  #swift now discussing ring placement

* Your track needs to exist in the system, and be scheduled in the day.
  Information about the room will be added automatically from the schedule.

* You can mention other tracks by using the corresponding hashtags, like:
  ``#nova now discussing multi-attach with #cinder``.

* There can only be one ``now`` discussion topic at a time. If multiple
  topics are discussed at the same time in various corners of the room,
  they should all be specified in a single ``now`` command.

* In order to ensure that information is current, entering a ``now`` command
  wipes out any ``next`` entry for the same track.

next
----

The ``next`` command lets you communicate the upcoming topics of discussion in
your track. You can use it as a teaser for things to come. Example usage::

  #swift next at 2pm we plan to discuss #glance support
  #swift next around 3pm we plan to cover cold storage features

* Your track needs to exist in the system, and be scheduled in the day.

* You can specify multiple ``next`` discussion topics. To clear the list, you
  can enter a new ``now`` discussion topic, or use the ``clean`` command.

* Since passing a new ``now`` command wipes out the ``next`` entries, you
  might want to refresh those after entering a ``now`` topic.

book
----

The ``book`` command is used to book available slots in the additional rooms.
Available time slots (at the bottom of the PTGbot page) display a slot code
you can use book the room. Example usage::

  #vitrage book Missouri-MonAM

* Your track needs to exist in the system.

* Once you booked the slot, you are part of the schedule for the day, and
  you can use the ``now`` and ``next`` commands to communicate what topic
  is being discussed.

unbook
------

The ``unbook`` command is used to free up booked slots in the additional rooms.
You should generally not unbook a track without the consent of its track lead.
Example usage::

  #vitrage unbook Missouri-MonAM

clean
-----

You can remove all ``now`` and ``next`` entries related to your track by
issuing the ``clean`` command (with no argument). Example usage::

  #ironic clean

color
-----

By default all tracks appear as blue badges on the page. You can set your
own color using the ``color`` command. Colors can be specified in any
form supported by the CSS attribute background-color::

  #infra color red
  #oslo color #42f4c5

* The color command only sets the background color for the track
  name. The foreground is always white.

location
--------

The room your track discussions happen in should be filled automatically
by the PTGbot by looking up the schedule information. In case it's not right,
you can overwrite it using the ``location`` command. Example usage::

  #oslo location Level B, Ballroom A


Admin commands
==============

You have to be a channel operator (+o) to use admin commands.

~list
  List available track names

~add TRACK [TRACK..]
  Add new track(s)

~del TRACK [TRACK..]
  Deletes track(s)

~clean TRACK [TRACK..]
  Removes active entries for specified track(s)

~newday
  Removes now/next/location entries, to be run at the start of a new day

~motd LEVEL MESSAGE
  Adds a message of the day on top of the rendered page. Level must be one of
  info, success, warning or danger.

~cleanmotd
  Removes message of the day on top of the rendered page.

~emptydb
  Resets the database entirely to minimal contents

~fetchdb URL
  Fetches JSON DB from specified URL. Any JSON key specified will replace
  existing data in database.

~requirevoice
  Requires that users are voiced (+v) to issue track moderation commands

~alloweveryone
  Allows everyone in the channel to issue track moderation commands


Local testing
=============

Copy config.json.sample to config.json::

  cp config.json.sample config.json

Edit config.json contents, for example::

  {
  "irc_nick": "ptgbot",
  "irc_server": "irc.freenode.net",
  "irc_port": 6697,
  "irc_channel": "#testptg",
  "db_filename": "html/ptg.json",
  }

In one terminal, run the bot::

  tox -evenv -- ptgbot -d config.json

Join that channel and give commands to the bot::

  ~fetchdb http://paste.openstack.org/raw/737820/
  #swift now discussing ring placement

(note, the bot currently only takes commands from Freenode identified users)

In another terminal, start the webserver::

  cd html && python -m SimpleHTTPServer

Open the web page in a web browser: http://127.0.0.1:8000/ptg.html
