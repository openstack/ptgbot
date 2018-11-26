# Copyright 2011, 2013 OpenStack Foundation
# Copyright 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import collections
import daemon
from ib3.auth import SASL
from ib3.connection import SSL
import irc.bot
import json
import logging.config
import os
import requests
import time
import textwrap

import ptgbot.db

try:
    import daemon.pidlockfile as pid_file_module
except ImportError:
    # as of python-daemon 1.6 it doesn't bundle pidlockfile anymore
    # instead it depends on lockfile-0.9.1
    import daemon.pidfile as pid_file_module

# https://bitbucket.org/jaraco/irc/issue/34/
# irc-client-should-not-crash-on-failed
# ^ This is why pep8 is a bad idea.
irc.client.ServerConnection.buffer_class.errors = 'replace'
# If a long message is split, how long to sleep between sending parts
# of a message.  This is lower than the general recommended interval,
# but in practice freenode allows short bursts at a higher rate.
MESSAGE_CONTINUATION_SLEEP = 0.5
# The amount of time to sleep between messages.
ANTI_FLOOD_SLEEP = 2
DOC_URL = 'https://git.openstack.org/cgit/openstack/ptgbot/tree/README.rst'


class PTGBot(SASL, SSL, irc.bot.SingleServerIRCBot):
    log = logging.getLogger("ptgbot.bot")

    def __init__(self, nickname, password, server, port, channel, db):
        super(PTGBot, self).__init__(
            server_list=[(server, port)],
            nickname=nickname,
            realname=nickname,
            ident_password=password,
            channels=[channel])
        self.nickname = nickname
        self.password = password
        self.channel = channel
        self.identify_msg_cap = False
        self.data = db

    def on_welcome(self, c, e):
        self.identify_msg_cap = False
        self.log.debug("Requesting identify-msg capability")
        c.cap('REQ', 'identify-msg')
        c.cap('END')

    def on_cap(self, c, e):
        self.log.debug("Received cap response %s" % repr(e.arguments))
        if e.arguments[0] == 'ACK' and 'identify-msg' in e.arguments[1]:
            self.log.debug("identify-msg cap acked")
            self.identify_msg_cap = True

    def usage(self, channel):
        self.send(channel, "Format is '#TRACK COMMAND [PARAMETERS]'")
        self.send(channel, "See doc at: " + DOC_URL)

    def send_track_list(self, channel):
        tracks = self.data.list_tracks()
        if tracks:
            self.send(channel, "Active tracks: %s" % str.join(' ', tracks))
        else:
            self.send(channel, "There are no active tracks defined yet")

    def on_pubmsg(self, c, e):
        if not self.identify_msg_cap:
            self.log.debug("Ignoring message because identify-msg "
                           "cap not enabled")
            return
        nick = e.source.split('!')[0]
        msg = e.arguments[0][1:]
        chan = e.target

        if msg.startswith('#'):
            if (self.data.is_voice_required() and not
                    (self.channels[chan].is_voiced(nick) or
                     self.channels[chan].is_oper(nick))):
                self.send(chan, "%s: Need voice to issue commands" % (nick,))
                return

            words = msg.split()
            if ((len(words) < 2) or
               (len(words) == 2 and words[1].lower() != 'clean')):
                self.send(chan, "%s: Incorrect number of arguments" % (nick,))
                self.usage(chan)
                return

            track = words[0][1:].lower()
            if not self.data.is_track_valid(track):
                self.send(chan, "%s: unknown track '%s'" % (nick, track))
                self.send_track_list(chan)
                return

            adverb = words[1].lower()
            params = str.join(' ', words[2:])
            if adverb in ['now', 'next', 'location']:
                if not self.data.get_track_room(track):
                    self.send(chan, "%s: track '%s' is not scheduled today" %
                              (nick, track))
                    return
            if adverb == 'now':
                self.data.add_now(track, params)
            elif adverb == 'next':
                self.data.add_next(track, params)
            elif adverb == 'clean':
                self.data.clean_tracks([track])
            elif adverb == 'color':
                self.data.add_color(track, params)
            elif adverb == 'location':
                self.data.add_location(track, params)
            elif adverb == 'book':
                room, sep, timeslot = params.partition('-')
                if self.data.is_slot_valid_and_empty(room, timeslot):
                    self.data.book(track, room, timeslot)
                    self.send(chan, "%s: Room %s is now booked on %s for %s" %
                              (nick, room, timeslot, track))
                else:
                    self.send(chan, "%s: invalid slot reference '%s'" %
                              (nick, params))
            else:
                self.send(chan, "%s: unknown directive '%s'" % (nick, adverb))
                self.usage(chan)
                return

        if msg.startswith('~'):
            if not self.channels[chan].is_oper(nick):
                self.send(chan, "%s: Need op for admin commands" % (nick,))
                return
            words = msg.split()
            command = words[0][1:].lower()
            if command == 'reload':
                self.data.reload()
            elif command == 'fetchdb':
                url = words[1]
                self.send(chan, "Loading DB from %s ..." % url)
                try:
                    self.data.import_json(requests.get(url).json())
                    self.send(chan, "Done.")
                except Exception as e:
                    self.send(chan, "Error loading DB: %s" % e)
            elif command == 'unbook':
                params = str.join(' ', words[1:])
                room, sep, timeslot = params.partition('-')
                self.data.unbook(room, timeslot)
            elif command == 'newday':
                self.data.new_day_cleanup()
            elif command == 'requirevoice':
                self.data.require_voice()
            elif command == 'alloweveryone':
                self.data.allow_everyone()
            elif command == 'list':
                self.send_track_list(chan)
            elif command in ('clean', 'add', 'del'):
                if len(words) < 2:
                    self.send(chan, "this command takes one or more arguments")
                    return
                getattr(self.data, command + '_tracks')(words[1:])
            else:
                self.send(chan, "%s: unknown command '%s'" % (nick, command))
                return

    def send(self, channel, msg):
        # 400 chars is an estimate of a safe line length (which can vary)
        chunks = textwrap.wrap(msg, 400)
        if len(chunks) > 10:
            raise Exception("Unusually large message: %s" % (msg,))
        for count, chunk in enumerate(chunks):
            self.connection.privmsg(channel, chunk)
            if count:
                time.sleep(MESSAGE_CONTINUATION_SLEEP)
        time.sleep(ANTI_FLOOD_SLEEP)


def start(configpath):
    with open(configpath, 'r') as fp:
        config = json.load(fp, object_pairs_hook=collections.OrderedDict)

    if 'log_config' in config:
        log_config = config['log_config']
        fp = os.path.expanduser(log_config)
        if not os.path.exists(fp):
            raise Exception("Unable to read logging config file at %s" % fp)
        logging.config.fileConfig(fp)
    else:
        logging.basicConfig(level=logging.DEBUG)

    db = ptgbot.db.PTGDataBase(config)

    bot = PTGBot(config['irc_nick'],
                 config.get('irc_pass', ''),
                 config['irc_server'],
                 config['irc_port'],
                 config['irc_channel'],
                 db)
    bot.start()


def main():
    parser = argparse.ArgumentParser(description='PTG bot.')
    parser.add_argument('configfile', help='specify the config file')
    parser.add_argument('-d', dest='nodaemon', action='store_true',
                        help='do not run as a daemon')
    args = parser.parse_args()

    if not args.nodaemon:
        pid = pid_file_module.TimeoutPIDLockFile(
            "/var/run/ptgbot/ptgbot.pid", 10)
        with daemon.DaemonContext(pidfile=pid):
            start(args.configfile)
    start(args.configfile)


if __name__ == "__main__":
    main()
