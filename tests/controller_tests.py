"""
Unit tests for the controller module in a headless Pygame environment.
This module tests the functionality of the Controller class, specifically
"""

import pygame
import os
import sys
import types
import importlib
from contextlib import contextmanager

import pytest

# ────────────────────────────────────────────────────────────────────────────
# 1.  Headless Pygame setup – must be done *before* importing pygame
# ────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

pygame.init()  # pylint: disable=no-member
pygame.display.set_mode((1, 1))

# ────────────────────────────────────────────────────────────────────────────
# 2.  Minimal **config** with just what controller needs
# ────────────────────────────────────────────────────────────────────────────
config_stub = types.ModuleType("config")
config_stub.start_game_button_pos = (10, 20)
config_stub.START_BUTTON_WIDTH = 120
config_stub.START_BUTTON_LENGTH = 40
sys.modules["config"] = config_stub


# ────────────────────────────────────────────────────────────────────────────
# 3.  Dummy view object – tracks whether its display method was called
# ────────────────────────────────────────────────────────────────────────────
class DummyView:
    """
    A dummy view class to simulate a UI for testing purposes.
    """

    def __init__(self):
        """
        Initializes the DummyView with a flag to track if the game has started.
        """
        self.started = False
        self.action_buttons = {}

    def display_start_game_button(self):
        """
        Simulates displaying the start game button.
        """
        self.started = True


# ────────────────────────────────────────────────────────────────────────────
# 4.  Import the real Controller (after stubs are ready)
# ────────────────────────────────────────────────────────────────────────────
controller = importlib.import_module("controller")
Controller = controller.Controller


# ────────────────────────────────────────────────────────────────────────────
# 5.  Fixture: silence pygame.display.flip so loops don’t actually flip
# ────────────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def stub_flip(monkeypatch):
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    yield
    pygame.event.clear()


# ────────────────────────────────────────────────────────────────────────────
# 6.  Helper to feed pygame.event.get with scripted sequences
# ────────────────────────────────────────────────────────────────────────────
@contextmanager
def event_stream(events):
    """Temporarily monkey‑patch pygame.event.get to yield *events*, then []."""
    original_get = pygame.event.get
    called = {"n": 0}

    def fake_get():
        called["n"] += 1
        if called["n"] == 1:
            return events
        return []

    pygame.event.get = fake_get
    try:
        yield
    finally:
        pygame.event.get = original_get


# ────────────────────────────────────────────────────────────────────────────
# 7.  Tests
# -----------------------------------------------------------------------------


def test_is_button_clicked_true_inside_left_click():
    rect = pygame.Rect(0, 0, 50, 50)
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (25, 25), "button": 1})
    assert Controller.is_button_clicked(None, rect, click) is True


def test_is_button_clicked_false_right_button():
    rect = pygame.Rect(0, 0, 50, 50)
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (25, 25), "button": 3})
    assert Controller.is_button_clicked(None, rect, click) is False


def test_start_game_returns_after_click(monkeypatch):
    view = DummyView()
    ctrl = Controller(view)

    button_x, button_y = config_stub.start_game_button_pos
    mouse_x = button_x + config_stub.START_BUTTON_WIDTH // 2
    mouse_y = button_y + config_stub.START_BUTTON_LENGTH // 2

    click = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"pos": (mouse_x, mouse_y), "button": 1}
    )

    with event_stream([click]):
        result = ctrl.start_game()

    assert view.started is True
    assert result is None


def test_player_action_controller_returns_correct_action(monkeypatch):
    # prepare a dummy view with two action buttons
    view = DummyView()
    fold_rect = pygame.Rect(0, 0, 40, 20)
    call_rect = pygame.Rect(50, 0, 40, 20)
    view.action_buttons = {"fold": fold_rect, "call": call_rect}

    ctrl = Controller(view)

    # craft a mouse click inside the "call" button
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (55, 10), "button": 1})

    with event_stream([click]):
        action = ctrl.player_action_controller()

    assert action == "call"
