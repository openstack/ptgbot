# Copyright (c) 2017, Thierry Carrez
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

import calendar
import copy
import datetime
import json
import os
import random


class PTGDataBase():

    BASE = {'tracks': [], 'slots': {}, 'now': {}, 'next': {}, 'colors': {},
            'location': {}, 'schedule': {}, 'voice': 0}

    def __init__(self, config):
        self.filename = config['db_filename']

        if os.path.isfile(self.filename):
            with open(self.filename, 'r') as fp:
                self.data = json.load(fp)
        else:
            self.data = copy.deepcopy(self.BASE)

        self.save()

    def import_json(self, jsondata):
        # Update the DB with the data found in the provided JSON
        self.data.update(jsondata)

        # Add tracks mentioned in configuration that are not in track list
        for room, bookings in self.data['schedule'].items():
            for time, track in bookings.items():
                if track not in self.data['tracks']:
                    self.add_tracks([track])

        self.colorize()
        self.save()

    def add_now(self, track, session):
        self.data['now'][track] = session
        # Update location if none manually provided yet
        room = self.get_track_room(track)
        if room and track not in self.data['location']:
            self.add_location(track, room)
        if track in self.data['next']:
            del self.data['next'][track]
        self.save()

    def add_color(self, track, color):
        self.data['colors'][track] = color
        self.save()

    def colorize(self):
        for track in self.data['tracks']:
            if track not in self.data['colors']:
                self.add_color(track, random.choice([
                    '#596468',
                    '#9ea8ad',
                    '#b57506',
                    '#f8ac29',
                    '#5b731a',
                    '#9dc62d',
                    '#156489',
                    '#27a3dd',
                    '#2a6d3c',
                    '#3fa45b',
                    '#930a0a',
                    '#dc0d0e',
                ]))

    def get_track_room(self, track):
        # This simplified version returns the first room the track is
        # scheduled in for the day. If the event does not run on this
        # day, pick the first day.
        today = calendar.day_name[datetime.date.today().weekday()]
        if today not in self.data['slots']:
            today = next(iter(self.data['slots']))
        for room, bookings in self.data['schedule'].items():
            for btime, btrack in bookings.items():
                for slot in self.data['slots'].get(today, []):
                    if btrack == track and btime == slot['name']:
                        return room
        return None

    def add_location(self, track, location):
        self.data['location'][track] = location
        self.save()

    def add_next(self, track, session):
        if track not in self.data['next']:
            self.data['next'][track] = []
        self.data['next'][track].append(session)
        self.save()

    def is_track_valid(self, track):
        return track in self.data['tracks']

    def list_tracks(self):
        return sorted(self.data['tracks'])

    def add_tracks(self, tracks):
        for track in tracks:
            if track not in self.data['tracks']:
                self.data['tracks'].append(track)
        self.colorize()
        self.save()

    def del_tracks(self, tracks):
        for track in tracks:
            if track in self.data['tracks']:
                self.data['tracks'].remove(track)
        self.save()

    def clean_tracks(self, tracks):
        for track in tracks:
            if track in self.data['now']:
                del self.data['now'][track]
            if track in self.data['next']:
                del self.data['next'][track]
        self.save()

    def is_slot_valid_and_empty(self, room, timeslot):
        try:
            return not self.data['schedule'][room][timeslot]
        except KeyError:
            return False

    def book(self, track, room, timeslot):
        self.data['schedule'][room][timeslot] = track
        self.save()

    def unbook(self, room, timeslot):
        if room in self.data['schedule'].keys():
            if timeslot in self.data['schedule'][room].keys():
                self.data['schedule'][room][timeslot] = ""
        self.save()

    def is_voice_required(self):
        return self.data['voice'] == 1

    def require_voice(self):
        self.data['voice'] = 1
        self.save()

    def allow_everyone(self):
        self.data['voice'] = 0
        self.save()

    def new_day_cleanup(self):
        self.data['now'] = {}
        self.data['next'] = {}
        self.data['location'] = {}
        self.save()

    def reload(self):
        self.data = copy.deepcopy(self.BASE)
        self.save()

    def save(self):
        timestamp = datetime.datetime.now()
        self.data['timestamp'] = '{:%Y-%m-%d %H:%M:%S}'.format(timestamp)
        self.data['tracks'] = sorted(self.data['tracks'])
        with open(self.filename, 'w') as fp:
            json.dump(self.data, fp)
