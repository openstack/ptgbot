#! /usr/bin/env python

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

import json
import os
import datetime


class PTGDataBase():

    BASE = {'rooms': [], 'ethercalc': [], 'now': {}, 'next': {}, 'colors': {},
            'location': {}}

    def __init__(self, filename, ethercalc):
        self.filename = filename
        self.ethercalc = ethercalc
        if os.path.isfile(filename):
            with open(filename, 'r') as fp:
                self.data = json.load(fp)
        else:
            self.data = self.BASE
        self.save()

    def add_now(self, room, session):
        self.data['now'][room] = session
        if room in self.data['next']:
            del self.data['next'][room]
        self.save()

    def add_color(self, room, color):
        self.data['colors'][room] = color
        self.save()

    def add_location(self, room, location):
        if 'location' not in self.data:
            self.data['location'] = {}
        self.data['location'][room] = location
        self.save()

    def add_next(self, room, session):
        if room not in self.data['next']:
            self.data['next'][room] = []
        self.data['next'][room].append(session)
        self.save()

    def is_room_valid(self, room):
        return room in self.data['rooms']

    def list_rooms(self):
        return sorted(self.data['rooms'])

    def add_rooms(self, rooms):
        for room in rooms:
            if room not in self.data['rooms']:
                self.data['rooms'].append(room)
        self.save()

    def del_rooms(self, rooms):
        for room in rooms:
            if room in self.data['rooms']:
                self.data['rooms'].remove(room)
        self.save()

    def clean_rooms(self, rooms):
        for room in rooms:
            if room in self.data['now']:
                del self.data['now'][room]
            if room in self.data['next']:
                del self.data['next'][room]
        self.save()

    def wipe(self):
        self.data = self.BASE
        self.save()

    def save(self):
        if self.ethercalc:
            self.data['ethercalc'] = self.ethercalc.load()
        timestamp = datetime.datetime.now()
        self.data['timestamp'] = '{:%Y-%m-%d %H:%M:%S}'.format(timestamp)
        with open(self.filename, 'w') as fp:
            json.dump(self.data, fp)
