# Copyright 2011, 2013, 2020 OpenStack Foundation
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


# Checks location against known tracks.  If prefixed with # then
# insists it must match a known track.  If not #-prefixed but
# matches a known track then the # prefix is added.  Returns the
# normalized location to check into, or None if a valid one was
# not established.  When matching/matched against a known track,
# it will be lower-cased.  This assumes that all registered tracks
# are lower-case.

import re


def normalize_location(tracks, location):
    if location.startswith('#'):
        track = location[1:].lower()
        if track in tracks:
            return location.lower()
        else:
            raise ValueError(track)
    else:
        if location.lower() in tracks:
            return '#' + location.lower()
        else:
            # Free-form location
            return location


def process_user_command(db, nick, cmd, params):
    if cmd == 'in':
        if len(params) == 0:
            return "The 'in' command should be followed by a location."

        location = " ".join(params)
        try:
            location = normalize_location(db.list_tracks(), location)
        except ValueError as e:
            return "Unrecognised track #%s" % e

        db.check_in(nick, location)
        return "OK, checked into %s - thanks for the update!" % location

    elif cmd == 'out':
        if len(params) > 0:
            return "The 'out' command does not accept any extra parameters."

        last_check_in = db.get_last_check_in(nick)
        if last_check_in['location'] is None:
            return "You weren't checked in anywhere yet!"

        if last_check_in['out'] is not None:
            return ("You already checked out of %s at %s!" %
                    (last_check_in['location'], last_check_in['out']))

        location = db.check_out(nick)
        return "OK, checked out of %s - thanks for the update!" % location

    elif cmd == 'seen':
        if len(params) != 1:
            return "The 'seen' command needs a single nick argument."

        seen_nick = params[0]
        last_check_in = db.get_last_check_in(seen_nick)

        if last_check_in['location'] is None:
            return "%s never checked in anywhere" % seen_nick
        elif last_check_in['out'] is None:
            return ("%s was last seen in %s at %s" % (
                    last_check_in['nick'],
                    last_check_in['location'],
                    last_check_in['in']))
        else:
            return ("%s checked out of %s at %s" % (
                    last_check_in['nick'],
                    last_check_in['location'],
                    last_check_in['out']))

    elif cmd == 'subscribe':
        new_re = str.join(' ', params)
        existing_re = db.get_subscription(nick)
        if new_re == "":
            if existing_re is None:
                return "You don't have a subscription regex set yet"
            else:
                return "Your current subscription regex is: " + existing_re
        else:
            try:
                re.compile(new_re)
            except Exception as e:
                return "Invalid regex: %s" % e
            else:
                db.set_subscription(nick, new_re)
                return ("Subscription set to " + new_re +
                        (" (was %s)" % existing_re if existing_re else ""))

    elif cmd == 'unsubscribe':
        existing_re = db.get_subscription(nick)
        if existing_re is None:
            return "You don't have a subscription regex set yet"
        else:
            db.set_subscription(nick, None)
            return "Cancelled subscription %s" % existing_re

    else:
        return "Unknown user command. Should be: in, out, seen, or subscribe"
