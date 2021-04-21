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


def process_admin_command(db, command, params):

    if command == 'emptydb':
        db.empty()

    elif command == 'fetchdb':
        if len(params) < 1:
            return "Missing URL to fetch (~fetch URL)"
        url = params[0]
        try:
            db.import_json(url)
            return "Loaded DB from %s" % url
        except Exception as e:
            return "Error loading DB: %s" % e

    elif command == 'newday':
        db.new_day_cleanup()

    elif command == 'motd':
        if len(params) < 1:
            return "Missing subcommand (~motd add|del|clean|reorder ...)"

        if params[0] == "add":
            if len(params) < 3:
                return "Missing parameters (~motd add LEVEL MSG)"
            if params[1] not in ['info', 'success', 'warning', 'danger']:
                return ("Incorrect message level '%s' (should be info, "
                        "success, warning or danger)" % params[1])
            db.motd_add(params[1], str.join(' ', params[2:]))

        elif params[0] == "del":
            if len(params) < 2:
                return "Missing message number (~motd del NUM)"
            if not db.motd_has(params[1]):
                return "Incorrect message number %s" % params[1]
            db.motd_del(params[1])

        elif params[0] in ("clean", "clear"):
            if len(params) > 1:
                return "'~motd clean' does not take parameters"
            db.motd_clean()

        elif params[0] == "reorder":
            if len(params) < 2:
                return "Missing params (~motd reorder X Y...)"
            order = []
            for num in params[1:]:
                if not db.motd_has(num):
                    return "Incorrect message number %s" % num
                order.append(num)
            db.motd_reorder(order)

        else:
            return "Unknown motd subcommand %s" % params[0]

    elif command == 'requirevoice':
        db.require_voice()

    elif command == 'alloweveryone':
        db.allow_everyone()

    elif command == 'list':
        return 'Available tracks: ' + str.join(' ', db.list_tracks())

    elif command in ('clean', 'add', 'del'):
        if len(params) < 1:
            return "This command takes one or more arguments"
        getattr(db, command + '_tracks')(params)

    else:
        return "Unknown command '%s'" % command
