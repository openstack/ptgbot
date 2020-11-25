# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_message_process
--------------------
Check that IRC messages are processed correctly
"""

from irc.client import Event
import copy
import testtools
from unittest import mock

from ptgbot.bot import DOC_URL, PTGBot
from ptgbot.db import PTGDataBase


class TestProcessMessage(testtools.TestCase):

    def setUp(self):
        super(TestProcessMessage, self).setUp()
        self.db = PTGDataBase(
            {'db_filename': 'base.json'},
            write_to_disk=False
        )
        self.bot = PTGBot('', '', '', '', '#channel', self.db)
        self.bot.identify_msg_cap = True

    def test_ignored_messages(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+hey ptgbot wazzzup'])

        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.on_pubmsg('', msg)
            self.assertFalse(mock_send.called)

    def test_help(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#help'])

        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.on_pubmsg('', msg)
            mock_send.assert_called_with('#channel', "See doc at: " + DOC_URL)

    def test_invalidtrack(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#svift now Looking at me'])

        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.on_pubmsg('', msg)
            mock_send.assert_any_call(
                '#channel',
                "johndoe: unknown track 'svift'"
            )

    def test_now(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift now Looking at me'])

        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['now']['swift'],
            "Looking at me"
        )

    def test_next(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift next Looking at you'])

        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['next']['swift'],
            ["Looking at you"]
        )
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift next Looking at us'])

        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['next']['swift'],
            ["Looking at you", "Looking at us"]
        )

    def test_now_clears_next(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift next Looking at you'])

        self.bot.on_pubmsg('', msg)
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift now Looking at me'])

        self.bot.on_pubmsg('', msg)
        self.assertFalse('swift' in self.db.data['next'])

    def test_etherpad(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift etherpad https://etherpad.opendev.org/swift'])

        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['etherpads']['swift'],
            "https://etherpad.opendev.org/swift"
        )
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift etherpad auto'])

        self.bot.on_pubmsg('', msg)
        self.assertFalse('swift' in self.db.data['etherpads'])

    def test_url(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift url https://meetpad.opendev.org/swift'])

        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['urls']['swift'],
            "https://meetpad.opendev.org/swift"
        )
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift url none'])

        self.bot.on_pubmsg('', msg)
        self.assertFalse('swift' in self.db.data['urls'])

    def test_color(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift color #ffffff'])

        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['colors']['swift'],
            "#ffffff"
        )

    def test_location(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift location On the beach'])

        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['location']['swift'],
            "On the beach"
        )

    def test_book(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift book Aspen-FriP1'])

        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.on_pubmsg('', msg)
            mock_send.assert_called_with(
                '#channel',
                "johndoe: Room Aspen is now booked on FriP1 for swift"
            )
        self.assertEquals(
            self.db.data['schedule']['Aspen']['FriP1'],
            "swift"
        )

    def test_unbook(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+#swift unbook Vail-TueP2'])

        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.on_pubmsg('', msg)
            mock_send.assert_called_with(
                '#channel',
                "johndoe: Room Vail (previously booked for swift) is "
                "now free on TueP2"
            )
        self.assertEquals(
            self.db.data['schedule']['Vail']['TueP2'],
            ""
        )

    def test_invalid_book(self):
        slots = ['Beach-TueP2', 'Vail-TueP2']

        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            for slot in slots:
                msg = Event('',
                            'johndoe!~johndoe@openstack/member/johndoe',
                            '#channel',
                            ['+#swift book ' + slot])
                self.bot.on_pubmsg('', msg)
                mock_send.assert_called_with(
                    '#channel',
                    "johndoe: slot '%s' is invalid (or booked)" % slot
                )
                mock_send.reset_mock()

    def test_invalid_unbook(self):
        slots = ['Beach-TueP2', 'Aspen-FriP1']

        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            for slot in slots:
                msg = Event('',
                            'johndoe!~johndoe@openstack/member/johndoe',
                            '#channel',
                            ['+#swift unbook ' + slot])
                self.bot.on_pubmsg('', msg)
                mock_send.assert_called_with(
                    '#channel',
                    "johndoe: slot '%s' is invalid "
                    "(or not booked for swift)" % slot
                )
                mock_send.reset_mock()

    def test_admin_cmds_only_admins(self):
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+~list'])
        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.is_chanop = mock.MagicMock(return_value=False)
            self.bot.on_pubmsg('', msg)
            mock_send.assert_called_with(
                '#channel',
                "johndoe: Need op for admin commands",
            )

    def test_admin_cmds_parameters(self):
        responses = {
            '~m': "Unknown command 'm'",
            '~motd': "Missing subcommand (~motd add|del|clean|reorder ...)",
            '~motd foo': "Unknown motd subcommand foo",
            '~motd add info': "Missing parameters (~motd add LEVEL MSG)",
            '~motd add foo bar': "Incorrect message level 'foo' (should "
                                 "be info, success, warning or danger)",
            '~motd del': "Missing message number (~motd del NUM)",
            '~motd del 999': "Incorrect message number 999",
            '~motd clean 2': "'~motd clean' does not take parameters",
            '~motd reorder': "Missing params (~motd reorder X Y...)",
            '~motd reorder 999': "Incorrect message number 999",
            '~add': "this command takes one or more arguments",
        }
        self.bot.is_chanop = mock.MagicMock(return_value=True)
        original_db_data = copy.deepcopy(self.db.data)
        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            for cmd, response in responses.items():
                msg = Event('',
                            'johndoe!~johndoe@openstack/member/johndoe',
                            '#channel',
                            ['+' + cmd])
                self.bot.on_pubmsg('', msg)
                mock_send.assert_called_with(
                    '#channel',
                    response
                )
                self.assertEqual(self.db.data, original_db_data)
                mock_send.reset_mock()

    def test_motd(self):
        motdstates = [
            ('~motd add info foo bar', [
                {'level': 'info', 'message': 'foo bar'}
            ]),
            ('~motd add info open bar', [
                {'level': 'info', 'message': 'foo bar'},
                {'level': 'info', 'message': 'open bar'},
            ]),
            ('~motd reorder 2 1', [
                {'level': 'info', 'message': 'open bar'},
                {'level': 'info', 'message': 'foo bar'},
            ]),
            ('~motd del 1', [
                {'level': 'info', 'message': 'foo bar'},
            ]),
            ('~motd add danger cocktails available', [
                {'level': 'info', 'message': 'foo bar'},
                {'level': 'danger', 'message': 'cocktails available'},
            ]),
            ('~motd reorder 1', [
                {'level': 'info', 'message': 'foo bar'},
            ]),
        ]
        self.bot.is_chanop = mock.MagicMock(return_value=True)
        for cmd, motd in motdstates:
            msg = Event('',
                        'johndoe!~johndoe@openstack/member/johndoe',
                        '#channel',
                        ['+' + cmd])
            self.bot.on_pubmsg('', msg)
            self.assertEqual(self.db.data['motd'], motd)

    def test_require_voice(self):
        self.bot.is_chanop = mock.MagicMock(return_value=True)
        self.bot.is_voiced = mock.MagicMock(return_value=False)
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+~requirevoice'])
        self.bot.on_pubmsg('', msg)
        msg = Event('',
                    'janedoe!~janedoe@openstack/member/janedoe',
                    '#channel',
                    ['+#swift now Looking at me'])
        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.on_pubmsg('', msg)
            mock_send.assert_called_with(
                '#channel',
                "janedoe: Need voice to issue commands",
            )
        msg = Event('',
                    'johndoe!~johndoe@openstack/member/johndoe',
                    '#channel',
                    ['+~alloweveryone'])
        self.bot.on_pubmsg('', msg)
        msg = Event('',
                    'janedoe!~janedoe@openstack/member/janedoe',
                    '#channel',
                    ['+#swift now Looking at me'])
        self.bot.on_pubmsg('', msg)
        self.assertEquals(
            self.db.data['now']['swift'],
            "Looking at me"
        )

    def test_airbag(self):
        with mock.patch.object(
            self.bot, 'send',
        ) as mock_send:
            self.bot.on_pubmsg()
            mock_send.assert_called_with(
                '#channel',
                "Bot airbag activated: on_pubmsg() "
                "missing 2 required positional arguments: 'c' and 'e'"
            )
            mock_send.reset_mock()
            self.bot.on_privmsg()
            mock_send.assert_called_with(
                '#channel',
                "Bot airbag activated: on_privmsg() "
                "missing 2 required positional arguments: 'c' and 'e'"
            )
