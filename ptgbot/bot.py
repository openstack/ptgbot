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
import functools
import irc.bot
import json
import logging.config
import os
import ssl
import time
import textwrap

import ptgbot.db
from ptgbot.admincommands import process_admin_command
from ptgbot.trackcommands import process_track_command
from ptgbot.usercommands import process_user_command


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
# but in practice IRC networks allows short bursts at a higher rate.
MESSAGE_CONTINUATION_SLEEP = 0.5
# The amount of time to sleep between messages.
ANTI_FLOOD_SLEEP = 2
DOC_URL = 'https://opendev.org/openstack/ptgbot/src/branch/master/README.rst'


def make_safe(func):
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            msg = "Bot airbag activated: " + str(e)
            args[0].log.error(msg, exc_info=True)
            args[0].send(args[0].channel, msg)
    return inner


class PTGBot(irc.bot.SingleServerIRCBot):
    log = logging.getLogger("ptgbot.bot")

    def __init__(self, nickname, password, server, port, channel, db):
        connect_params = {}
        if port == 6697:
            # Taken from the example in the Factory class docstring at
            # https://github.com/jaraco/irc/blob/main/irc/connection.py
            context = ssl.create_default_context()
            wrapper = functools.partial(
                context.wrap_socket, server_hostname=server)
            factory = irc.connection.Factory(wrapper=wrapper)
            connect_params['connect_factory'] = factory

        super(PTGBot, self).__init__(
            server_list=[(server, port)],
            nickname=nickname,
            realname=nickname,
            **connect_params)
        self.nickname = nickname
        self.password = password
        self.channel = channel
        self.data = db

    def on_welcome(self, c, e):
        time.sleep(5)
        if self.password:
            self.send("NickServ", "IDENTIFY " + self.password)
            time.sleep(2)
        self.connection.join(self.channel)

    def usage(self, channel):
        self.send(channel, "I accept commands in the following format: "
                  "'#TRACK COMMAND [PARAMETERS]'")
        self.send(channel, "See doc at: " + DOC_URL)

    def send_track_list(self, channel):
        tracks = self.data.list_tracks()
        if tracks:
            self.send(channel, "Active tracks: %s" % str.join(' ', tracks))
        else:
            self.send(channel, "There are no active tracks defined yet")

    @make_safe
    def on_privmsg(self, c, e):
        nick = e.source.split('!')[0]
        args = e.arguments[0]
        words = args.split()
        if len(words) < 1:
            self.log.debug("Ignoring privmsg with no content")
            return
        cmd = words[0].lower()

        if cmd.startswith('#') or cmd.startswith('+'):
            cmd = cmd[1:]

        msg = process_user_command(self.data, nick, cmd, words[1:])
        if msg:
            self.send(nick, msg)
        return

    def is_chanop(self, nick, chan):
        return self.channels[chan].is_oper(nick)

    def is_voiced(self, nick, chan):
        return (self.channels[chan].is_voiced(nick) or
                self.channels[chan].is_oper(nick))

    def handle_public_command(self, chan, nick, args):
        words = args.split()

        # Some messages are empty or only contain spaces.
        # Do nothing in that case.
        if not words:
            return

        cmd = words[0].lower()

        if len(cmd) > 1 and cmd[1:] == 'help':
            return "See PTGbot documentation at: " + DOC_URL

        if cmd.startswith('+'):
            return process_user_command(self.data, nick, cmd[1:], words[1:])

        if cmd.startswith('#'):
            if cmd in ['#in', '#out', '#seen', '#subscribe', '#unsubscribe']:
                return process_user_command(self.data, nick,
                                            cmd[1:], words[1:])
            else:
                if (self.data.is_voice_required() and
                        not self.is_voiced(nick, chan)):
                    return "Need voice to issue commands"
                track = words[0][1:].lower()
                return process_track_command(self.data, self.send, track,
                                             words[1:])

        if cmd.startswith('~'):
            if not self.is_chanop(nick, chan):
                return "Need op for admin commands"
            directive = words[0][1:].lower()
            return process_admin_command(self.data, directive, words[1:])

    @make_safe
    def on_pubmsg(self, c, e):
        nick = e.source.split('!')[0]
        args = e.arguments[0]
        chan = e.target

        msg = self.handle_public_command(chan, nick, args)
        if msg:
            self.send(chan, ("%s: " % nick) + msg)
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
