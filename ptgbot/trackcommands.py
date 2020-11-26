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

import re


def notify(db, botsend, track, adverb, sentence):
    location = db.get_location(track)
    track = '#' + track
    trackloc = track
    if location is not None:
        trackloc = "%s (%s)" % (track, location)

    for nick, regexp in db.get_subscriptions().items():
        if regexp is None:
            # Person did #unsubscribe, so skip
            continue
        event_text = " ".join([track, adverb, sentence])
        if re.search(regexp, event_text, re.IGNORECASE):
            message = "%s in %s: %s" % (adverb, trackloc, sentence)
            # Note: there is no guarantee that nick will be online
            # at this point.  However if not, the bot will receive
            # a 401 :No such nick/channel message which it will
            # ignore due to the lack of a nosuchnick handler.
            # Fortunately this is the behaviour we want.
            botsend(nick, message)


def not_scheduled_today(db, track):
    if not db.get_track_room(track):
        return ("Message added, but please note that track '%s' does not "
                "appear to have a room scheduled today." % track)


def process_track_command(db, botsend, track, params):
    if not db.is_track_valid(track):
        return "Unknown track '%s'" % track

    if len(params) < 1:
        return "Missing track command (#TRACK [now|next|clean...] ...)"

    adverb = params[0].lower()
    sentence = str.join(' ', params[1:])

    if adverb == 'now':
        if len(params) < 2:
            return "Missing sentence (#TRACK now ...)"
        db.add_now(track, sentence)
        notify(db, botsend, track, adverb, sentence)
        return not_scheduled_today(db, track)

    elif adverb == 'next':
        if len(params) < 2:
            return "Missing sentence (#TRACK next ...)"
        db.add_next(track, sentence)
        notify(db, botsend, track, adverb, sentence)
        return not_scheduled_today(db, track)

    elif adverb == 'clean':
        if len(params) > 1:
            return "'#TRACK clean' does not take any parameter"
        db.clean_tracks([track])

    elif adverb == 'etherpad':
        if len(params) != 2:
            return "'#TRACK etherpad' takes a single URL parameter"
        db.add_etherpad(track, params[1])

    elif adverb == 'url':
        if len(params) != 2:
            return "'#TRACK url' takes a single URL parameter"
        db.add_url(track, params[1])

    elif adverb == 'color':
        if len(params) != 2:
            return "'#TRACK color' takes a single colorcode parameter"
        db.add_color(track, params[1])

    elif adverb == 'location':
        db.add_location(track, sentence)

    elif adverb == 'book':
        if len(params) != 2:
            return "'#TRACK book' takes a single slotname parameter"
        room, sep, tslot = params[1].partition('-')
        if db.is_slot_valid_and_empty(room, tslot):
            db.book(track, room, tslot)
            return "Room %s is now booked on %s for %s" % (room, tslot, track)
        else:
            return "Slot '%s' is invalid (or booked)" % params[1]

    elif adverb == 'unbook':
        if len(params) != 2:
            return "'#TRACK unbook' takes a single slotname parameter"
        room, sep, tslot = params[1].partition('-')
        if db.is_slot_booked_for_track(track, room, tslot):
            db.unbook(room, tslot)
            return ("Room %s (previously booked for %s) is now free on %s" %
                    (room, track, tslot))
        else:
            return ("Slot '%s' is invalid (or not booked for %s)" %
                    (params[1], track))

    else:
        return ("Unknown command '%s'. Did you mean: %s now %s... ?" %
                (adverb, track, adverb))
