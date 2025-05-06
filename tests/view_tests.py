"""Unit tests for the PokerView class.
This module tests the functionality of the PokerView class, specifically
the display methods for various game elements.
"""

import sys
import types
from unittest.mock import Mock

import pytest


config_mock = types.ModuleType("config")

# Screen & card geometry
config_mock.SCREEN_LENGTH = 800
config_mock.SCREEN_WIDTH = 600
config_mock.CARD_LENGTH = 100
config_mock.CARD_WIDTH = 70

# Positions – just put everything somewhere on the screen


def _point():
    """Return a default point for positioning elements."""
    return (50, 50)


for name in [
    "player_hand_pos_1",
    "player_hand_pos_2",
    "bot_hand_pos_1",
    "bot_hand_pos_2",
    "flop_pos_1",
    "flop_pos_2",
    "flop_pos_3",
    "turn_pos",
    "river_pos",
    "raise_button_pos",
    "call_button_pos",
    "check_button_pos",
    "fold_button_pos",
    "bot_stack_pos",
    "player_stack_pos",
    "bot_decision_pos",
    "invalid_text_pos",
    "pot_pos",
    "display_round_pos",
    "display_winner_pos",
    "display_showdown_pos",
    "player_blind_pos",
    "bot_blind_pos",
    "start_game_button_pos",
]:
    setattr(config_mock, name, _point())

# Sizes / colours
config_mock.BUTTON_LENGTH = 40
config_mock.BUTTON_WIDTH = 120
config_mock.BUTTON_COLOR = (20, 120, 20)
config_mock.TEXT_COLOR = (255, 255, 255)
config_mock.PIGGY_LENGTH = 60
config_mock.PIGGY_WIDTH = 60
config_mock.BLACK_COLOR = (0, 0, 0)
config_mock.GREEN_COLOR = (0, 255, 0)
config_mock.DARK_RED_COLOR = (120, 0, 0)
config_mock.BLIND_LENGTH = 30
config_mock.BLIND_WIDTH = 30
config_mock.START_BUTTON_LENGTH = 60
config_mock.START_BUTTON_WIDTH = 180

sys.modules["config"] = config_mock


pygame_mock = types.ModuleType("pygame")
pygame_mock.SRCALPHA = 32


# -- Surface ------------------------------------------------------------------
class SurfaceMock(Mock):
    """Minimal subset of pygame.Surface needed by the view."""

    def __init__(self, *_, **__):
        super().__init__(
            spec=[
                "blit",
                "subsurface",
                "get_rect",
                "get_width",
                "get_height",
                "fill",
                "convert_alpha",
            ]
        )
        self._w = 400
        self._h = 300

    def get_rect(self, **kwargs):
        """Return a mock rect object with appropriate dimensions."""
        rect = Mock()
        rect.w = self._w
        rect.h = self._h
        rect.center = kwargs.get("center", (0, 0))
        return rect

    def subsurface(self, *_):
        """Return a new surface mock for a subsurface."""
        return SurfaceMock()

    def get_width(self):
        """Return the width of the surface."""
        return self._w

    def get_height(self):
        """Return the height of the surface."""
        return self._h

    def convert_alpha(self):
        """Return self with alpha conversion applied."""
        return self


pygame_mock.Surface = SurfaceMock

# -- Display ------------------------------------------------------------------
pygame_mock.display = types.SimpleNamespace(
    set_mode=lambda *_: SurfaceMock(),
    flip=Mock(),
    update=Mock(),
)

# -- Font ---------------------------------------------------------------------
pygame_font = types.ModuleType("pygame.font")
pygame_font.init = lambda: None
pygame_font.SysFont = lambda *_1, **_2: Mock(
    render=Mock(return_value=SurfaceMock()))
pygame_mock.font = pygame_font

# -- Transform & image --------------------------------------------------------
pygame_mock.transform = types.SimpleNamespace(scale=lambda *_: SurfaceMock())
pygame_mock.image = types.SimpleNamespace(load=lambda *_: SurfaceMock())

# -- Draw & Rect --------------------------------------------------------------
pygame_mock.draw = types.SimpleNamespace(rect=Mock())


def rect_mock(*args):
    """Flexible substitute for pygame.Rect accepting the common signatures.

    Real `pygame.Rect` can be built in many ways – two of which the code under
    test uses:
      • pygame.Rect(x, y, w, h)
      • pygame.Rect((x, y), (w, h))
    This mock just captures *x, y, w, h*, stores them, and provides a `.center`
    attribute (all the view actually touches).
    """
    if len(args) == 4:  # x, y, w, h
        pos_x, pos_y, width, height = args
    elif len(args) == 2 and all(isinstance(a, tuple) for a in args):
        (pos_x, pos_y), (width, height) = args
    else:
        raise TypeError("Unsupported Rect signature in test stub")

    rect = Mock()
    rect.x, rect.y, rect.w, rect.h = pos_x, pos_y, width, height
    rect.center = (pos_x + width // 2, pos_y + height // 2)
    return rect


pygame_mock.Rect = rect_mock

sys.modules["pygame"] = pygame_mock

# Import view after mocks are injected
import view  # noqa: E402


class DummyModel:
    """Dummy model class for testing the view."""
    player_hand = ("AS", "KD")
    bot_hand = ("7C", "8H")
    community_cards = ("2D", "3S", "4H", "5C", "6D")
    pot = 150
    chips = 0


@pytest.fixture
def poker_view():
    """Create and return a PokerView instance for testing."""
    return view.PokerView(DummyModel())


def _runs_without_exception(func, *args):
    """Execute a function with args and verify it doesn't raise an exception."""
    func(*args)


methods_and_args = [
    ("display_background", ()),
    ("display_loading_screen", ()),
    ("display_player_hand", (("AS", "KD"),)),
    ("display_flop", (("2D", "3S", "4H"),)),
    ("display_turn", (("5C",),)),
    ("display_river", (("6D",),)),
    ("display_fold_button", ()),
    ("display_check_button", ()),
    ("display_call_button", ()),
    ("display_raise_button", ()),
    ("display_bot_stack", (1000,)),
    ("display_player_stack", (950,)),
    ("display_bot_decision", ("call", "Pre‑Flop")),
    ("display_bot_decision", ("raise", "Turn", 120)),
    ("display_invalid_text", ()),
    ("display_invalid_text", ()),
    ("hide_invalid_text", ()),
    ("display_pot", (400,)),
    ("display_round", ("Flop",)),
    ("display_winner", ("Player",)),
    ("display_showdown", ()),
    ("display_player_round_bet", (55,)),
    ("display_bot_round_bet", (60,)),
    ("display_bot_hand", (("7C", "8H"),)),
    ("display_hidden_bot_hand", ()),
    ("display_small_blind", ((10, 10),)),
    ("display_big_blind", ((20, 20),)),
    ("display_start_game_button", ()),
]


@pytest.mark.parametrize("method_name,args", methods_and_args)
def test_view_methods_do_not_crash(poker_view, method_name, args): # pylint: disable=redefined-outer-name
    """Test that view methods run without raising exceptions."""
    _runs_without_exception(getattr(poker_view, method_name), *args)
