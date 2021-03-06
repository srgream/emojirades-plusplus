from plusplusbot.bot import PlusPlusBot
from unittest.mock import patch

import unittest
import tempfile
import logging
import os

logging.basicConfig(level=logging.DEBUG)


class EmojiradeBotTester(unittest.TestCase):
    """
    Base testing class that creates a bot that will accept events to test against
    """

    @patch("time.sleep", side_effect=InterruptedError)
    def send_event(self, event, sleep):
        self.bot.slack.sc.rtm_read.return_value = [event]

        try:
            self.bot.listen_for_commands()
        except InterruptedError:
            pass

    def reset_and_transition_to(self, state):
        """ From the beginning state, transition to another state the user wants """
        self.setUp()
        assert self.state["step"] == "new_game"

        if state == "waiting":
            events = [self.events.new_game]
        elif state == "provided":
            events = [self.events.new_game, self.events.posted_emojirade]
        elif state == "guessing":
            events = [self.events.new_game, self.events.posted_emojirade, self.events.posted_emoji]
        else:
            raise RuntimeError("Invalid state ({0}) provided to TestPlusPlusBot.transition_to()".format(state))

        for event in events:
            self.send_event(event)

    def save_responses(self, channel, message):
        self.responses.append((channel, message))

    def find_im(self, user_id):
        return user_id.replace("U", "D")

    def pretty_name(self, user_id):
        return user_id

    @patch("plusplusbot.bot.SlackClient")
    def setUp(self, slack_client):
        self.responses = []
        self.config, self.events = self.prepare_event_data()

        self.scorefile = tempfile.NamedTemporaryFile()
        self.statefile = tempfile.NamedTemporaryFile()

        os.environ["SLACK_BOT_TOKEN"] = "xoxb-000000000000-aaaaaaaaaaaaaaaaaaaaaaaa"

        self.bot = PlusPlusBot(self.scorefile.name, self.statefile.name)
        self.bot.slack.bot_id = self.config.bot_id

        # Override bot functions
        self.bot.slack.sc.rtm_send_message = self.save_responses
        self.bot.slack.find_im = self.find_im
        self.bot.slack.pretty_name = self.pretty_name

        self.state = self.bot.gamestate.state[self.config.channel]
        self.scoreboard = self.bot.scorekeeper.scoreboard[self.config.channel]

    def tearDown(self):
        self.scorefile.close()
        self.statefile.close()

    @staticmethod
    def prepare_event_data():
        team = "T00000001"
        channel = "C00000001"
        bot_id = "U00000000"
        bot_channel = "D00000000"
        player_1 = "U00000001"
        player_1_channel = "D00000001"
        player_2 = "U00000002"
        player_2_channel = "D00000002"
        player_3 = "U00000003"
        player_3_channel = "D00000003"
        player_4 = "U00000004"
        player_4_channel = "D00000004"
        emojirade = "testing"

        event_config = {
            "team": team,
            "channel": channel,
            "bot_id": bot_id,
            "bot_channel": bot_channel,
            "player_1": player_1,
            "player_1_channel": player_1_channel,
            "player_2": player_2,
            "player_2_channel": player_2_channel,
            "player_3": player_3,
            "player_3_channel": player_3_channel,
            "player_4": player_4,
            "player_4_channel": player_4_channel,
            "emojirade": emojirade,
        }

        base_event = {
            "team": team,
            "source_team": team,
            "channel": channel,
            "type": "message",
            "ts": "1000000000.000001",
        }

        event_registry = {
            "base": base_event,
            "new_game": {
                **base_event,
                **{
                    "user": player_1,
                    "text": "<@{0}> new game <@{1}> <@{2}>".format(bot_id, player_1, player_2),
                },
            },
            "posted_emojirade": {
                **base_event,
                **{
                    "channel": bot_channel,
                    "user": player_1,
                    "text": "emojirade {0}".format(emojirade),
                },
            },
            "posted_emoji": {
                **base_event,
                **{
                    "user": player_2,
                    "text": ":waddle:",
                },
            },
            "incorrect_guess": {
                **base_event,
                **{
                    "user": player_3,
                    "text": "foobar",
                },
            },
            "correct_guess": {
                **base_event,
                **{
                    "user": player_3,
                    "text": emojirade,
                },
            },
            "manual_award": {
                **base_event,
                **{
                    "user": player_2,
                    "text": "<@{0}>++".format(player_3),
                },
            },
            "plusplus": {
                **base_event,
                **{
                    "user": player_1,
                    "text": "<@{0}>++".format(player_2),
                },
            },
            "leaderboard": {
                **base_event,
                **{
                    "user": player_1,
                    "text": "<@{0}> leaderboard".format(bot_id),
                },
            },
            "fixwinner": {
                **base_event,
                **{
                    "user": player_2,
                    "text": "<@{0}> fixwinner <@{1}>".format(bot_id, player_4),
                },
            },
        }

        class Foo(object):
            pass

        events = Foo()
        config = Foo()

        for k, v in event_registry.items():
            setattr(events, k, v)

        for k, v in event_config.items():
            setattr(config, k, v)

        return config, events
