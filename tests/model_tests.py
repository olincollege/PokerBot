"""
Unit tests for the Model class in the poker game.
This module tests the functionality of the Model class.
It includes tests for the initialization of the model, deck creation,
dealing hands, community cards, betting handling, and hand evaluation.
"""

import sys
import types
import random
from unittest.mock import Mock

import pytest


cfg = types.ModuleType("config")
cfg.PLAYER_NAME = "Alice"
cfg.STARTING_STACK = 200
cfg.SMALL_BLIND = 2
cfg.BIG_BLIND = 4
cfg.BET_SIZES = {"flop": 4, "turn": 8, "river": 8}
cfg.MAX_RAISES_PER_ROUND = 3
cfg.player_blind_pos = (0, 0)
cfg.bot_blind_pos = (10, 0)
# any extra attrs model might read but our tests don’t care about
cfg.__dict__.setdefault("SCREEN_LENGTH", 800)
cfg.__dict__.setdefault("SCREEN_WIDTH", 600)

sys.modules["config"] = cfg


view_stub = types.ModuleType("view")


class DummyView:
    def __init__(self, _model):
        pass

    def __getattr__(self, _name):
        # any display_* method → harmless no‑op
        return lambda *args, **kwargs: None


view_stub.PokerView = DummyView
sys.modules["view"] = view_stub


ctrl_stub = types.ModuleType("controller")
ctrl_stub.Controller = lambda _view: None
sys.modules["controller"] = ctrl_stub


ml_stub = types.ModuleType("ML_bot")
ml_stub.bot_action = lambda _model: "continue"
ml_stub.QBot = lambda *args, **kwargs: types.SimpleNamespace(
    update=lambda _r: None)
sys.modules["ML_bot"] = ml_stub


h_eval_stub = types.ModuleType("hand_evaluator")
h_eval_stub.eval7 = lambda cards: 42  # always the same rank
sys.modules["hand_evaluator"] = h_eval_stub


import model  # noqa: E402


# Helper – build a fresh Model each time
@pytest.fixture
def fresh_model():
    return model.Model()


def test_init_defaults(fresh_model):
    m = fresh_model
    # players & stacks
    assert m.players == [cfg.PLAYER_NAME, "Bot"]
    assert m.chips[cfg.PLAYER_NAME] == cfg.STARTING_STACK
    assert m.chips["Bot"] == cfg.STARTING_STACK
    # blinds & bets
    assert m.small_blind == cfg.SMALL_BLIND
    assert m.big_blind == cfg.BIG_BLIND
    # deck size & uniqueness
    assert len(m.deck) == 52 and len(set(m.deck)) == 52
    # raise counter
    assert m.raise_count == 0 and m.max_raises_per_round == cfg.MAX_RAISES_PER_ROUND


def test_create_deck_unique_and_contains_expected():
    deck = model.Model().create_deck()
    assert len(deck) == 52 and len(set(deck)) == 52
    assert "ace_of_spades" in deck and "2_of_clubs" in deck


def test_deal_hands_and_deck_shrink(monkeypatch):
    # freeze shuffle so order is predictable
    monkeypatch.setattr(random, "shuffle", lambda d: None)
    m = model.Model()
    original_deck = m.create_deck().copy()
    m.deck = original_deck.copy()

    m.deal_hands()

    expected_player = [original_deck[-1], original_deck[-2]]
    expected_bot = [original_deck[-3], original_deck[-4]]
    assert m.player_hand == expected_player
    assert m.bot_hand == expected_bot
    assert len(m.deck) == 48


@pytest.mark.parametrize(
    "stage,count",
    [
        ("flop", 3),
        ("turn", 1),
        ("river", 1),
    ],
)
def test_deal_community_cards(stage, count):
    m = model.Model()
    m.deck = list(range(100, 100 + count + 5))  # dummy deck
    m.community_cards = []
    m.deal_community_cards(stage)
    assert len(m.community_cards) == count
    assert len(m.deck) == 5  # popped exactly `count` cards


def test_bet_handling_updates_chips_and_previous():
    m = model.Model()
    # player bet handling
    m.previous_player_bet = 0
    m.player_bet = 10
    start_player_chips = m.chips[m.players[0]]
    m.player_bet_handling()
    assert m.chips[m.players[0]] == start_player_chips - 10
    assert m.previous_player_bet == 10

    # bot bet handling
    m.previous_bot_bet = 0
    m.bot_bet = 15
    start_bot_chips = m.chips["Bot"]
    m.bot_bet_handling()
    assert m.chips["Bot"] == start_bot_chips - 15
    assert m.previous_bot_bet == 15


def test_get_current_bet_size_known_and_default():
    m = model.Model()
    m.stage = "flop"
    assert m.get_current_bet_size() == cfg.BET_SIZES["flop"]
    m.stage = "unknown"
    assert m.get_current_bet_size() == cfg.BIG_BLIND


def test_reset_after_betting_round_and_round_bets():
    m = model.Model()
    # simulate some betting state
    m.previous_player_bet = 5
    m.previous_bot_bet = 5
    m.player_bet = 20
    m.bot_bet = 15
    m.previous_stack = m.chips[m.players[0]] + m.chips["Bot"]
    m.previous_player_chips = m.chips[m.players[0]]
    m.previous_bot_chips = m.chips["Bot"]

    m.reset_after_betting_round()
    assert m.player_bet == 0 and m.bot_bet == 0 and m.raise_count == 0

    # make sure helper doesn’t crash
    m.get_round_bets()


def test_reset_after_hand_flips_blinds_and_sets_pot():
    m = model.Model()
    chips_before = m.chips[m.players[0]]

    m.reset_after_hand()
    assert set([m.small_blind_holder, m.big_blind_holder]) == set(m.players)
    assert m.pot == cfg.SMALL_BLIND + cfg.BIG_BLIND

    expected_deduction = (
        cfg.SMALL_BLIND if m.small_blind_holder == cfg.PLAYER_NAME else cfg.BIG_BLIND)
    assert m.chips[m.players[0]] == chips_before - expected_deduction


def test_hand_evaluator_calls_eval7():
    m = model.Model()
    assert m.hand_evaluator(["doesn't", "matter"]) == 42
