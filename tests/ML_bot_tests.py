"""
Unit tests for the ML_bot module using pytest framework.
This module tests the functionality of the ML_bot, including loading preflop data.
"""

import pytest
import numpy as np
import json
import os
import random
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# Import from the modules to test
from ML_bot import (
    load_preflop_data, PREFLOP_LOOKUP, canonicalize, get_hand_rank,
    bot_bet_handling, QBot, bot_action
)

# Test fixture for hand combinations
@pytest.fixture
def sample_hands():
    return {
        # High pairs
        'pocket_aces': ['ace_of_spades', 'ace_of_hearts'],
        'pocket_kings': ['king_of_spades', 'king_of_hearts'],
        # Suited hands
        'ace_king_suited': ['ace_of_spades', 'king_of_spades'],
        'queen_jack_suited': ['queen_of_hearts', 'jack_of_hearts'],
        # Offsuit hands
        'ace_king_offsuit': ['ace_of_spades', 'king_of_hearts'],
        'eight_six_offsuit': ['8_of_spades', '6_of_diamonds'],
        # Low pairs
        'pocket_deuces': ['2_of_spades', '2_of_hearts'],
    }

@pytest.fixture
def community_cards():
    return {
        'empty': [],
        'flop': ['ace_of_clubs', 'king_of_diamonds', '2_of_hearts'],
        'turn': ['ace_of_clubs', 'king_of_diamonds', '2_of_hearts', '10_of_spades'],
        'river': ['ace_of_clubs', 'king_of_diamonds', '2_of_hearts', '10_of_spades', '7_of_clubs']
    }

@pytest.fixture
def mock_game_state():
    """Mock game state for testing bot_action and related functions"""
    game = MagicMock()
    game.stage = "preflop"
    game.bot_hand = ['ace_of_spades', 'king_of_spades']
    game.community_cards = []
    game.bot_bet = 0
    game.player_bet = 0
    game.raise_count = 0
    game.max_raises_per_round = 3
    game.players = ["player", "bot"]
    game.chips = {"player": 1000, "bot": 1000}
    game.previous_bot_bet = 0
    game.current_bet = 0
    
    # Mock the get_current_bet_size method
    game.get_current_bet_size = MagicMock(return_value=20)
    
    # Create a real QBot instance for the game
    game.bot = QBot(num_buckets=10, save_path="test_q_strategy.json")
    
    return game

# Test preflop data loading
def test_load_preflop_data():
    # Test with existing file
    with patch('builtins.open', mock_open(read_data='{"AA": 1.0, "KK": 0.95}')):
        data = load_preflop_data()
        assert data == {"AA": 1.0, "KK": 0.95}
    
    # Test with missing file
    with patch('builtins.open', side_effect=FileNotFoundError):
        with patch('sys.stdout', new=StringIO()):  # Capture print output
            data = load_preflop_data()
            assert "AA" in data
            assert isinstance(data, dict)
            assert len(data) > 0

def test_preflop_lookup_exists():
    assert PREFLOP_LOOKUP is not None
    assert isinstance(PREFLOP_LOOKUP, dict)
    assert len(PREFLOP_LOOKUP) > 0

# Test hand canonicalization
def test_canonicalize(sample_hands):
    # Test pocket pairs
    assert canonicalize(sample_hands['pocket_aces']) == "AA"
    assert canonicalize(sample_hands['pocket_kings']) == "KK"
    assert canonicalize(sample_hands['pocket_deuces']) == "22"
    
    # Test suited hands
    assert canonicalize(sample_hands['ace_king_suited']) == "AKs"
    assert canonicalize(sample_hands['queen_jack_suited']) == "QJs"
    
    # Test offsuit hands
    assert canonicalize(sample_hands['ace_king_offsuit']) == "AK"
    assert canonicalize(sample_hands['eight_six_offsuit']) == "86"
    
    # Test order invariance
    assert canonicalize(['ace_of_spades', 'king_of_spades']) == canonicalize(['king_of_spades', 'ace_of_spades'])
    assert canonicalize(['8_of_hearts', '6_of_hearts']) == canonicalize(['6_of_hearts', '8_of_hearts'])

# Test hand ranking function
def test_get_hand_rank(sample_hands, community_cards):
    # Test preflop rankings
    preflop_aa = get_hand_rank(sample_hands['pocket_aces'], community_cards['empty'])
    preflop_kk = get_hand_rank(sample_hands['pocket_kings'], community_cards['empty'])
    preflop_22 = get_hand_rank(sample_hands['pocket_deuces'], community_cards['empty'])
    
    # Higher pairs should have better (lower) ranks
    assert preflop_aa < preflop_kk < preflop_22
    
    # Test with community cards
    flop_rank = get_hand_rank(sample_hands['pocket_aces'], community_cards['flop'])
    turn_rank = get_hand_rank(sample_hands['pocket_aces'], community_cards['turn'])
    river_rank = get_hand_rank(sample_hands['pocket_aces'], community_cards['river'])
    
    # Ensure the function works with different community card counts
    assert isinstance(flop_rank, (int, float))
    assert isinstance(turn_rank, (int, float))
    assert isinstance(river_rank, (int, float))
    
    # Test error handling with invalid inputs
    with patch('new_bot.eval5', side_effect=Exception("Test error")):
        with patch('sys.stdout', new=StringIO()):  # Capture print output
            result = get_hand_rank(['invalid_card'], [])
            assert isinstance(result, (int, float))

# Test bot bet handling
def test_bot_bet_handling():
    # Create a mock game state
    mock_game = MagicMock()
    mock_game.chips = {"player": 1000, "bot": 1000}
    mock_game.players = ["player", "bot"]
    mock_game.bot_bet = 50
    mock_game.previous_bot_bet = 20
    
    # Call the function
    bot_bet_handling(mock_game)
    
    # Verify the chips were properly deducted
    assert mock_game.chips["bot"] == 970  # 1000 - (50 - 20)
    assert mock_game.previous_bot_bet == 50

# Tests for QBot class
def test_qbot_initialization():
    # Test default initialization
    qbot = QBot(num_buckets=20, save_path="test_q_strategy.json")
    assert qbot.num_buckets == 20
    assert qbot.num_states == 4 * 20 * 4
    assert qbot.Q.shape == (4 * 20 * 4, 3)
    assert len(qbot.trajectory) == 0
    
    # Test with different parameters
    qbot2 = QBot(num_buckets=10, save_path="different_path.json")
    assert qbot2.num_buckets == 10
    assert qbot2.num_states == 4 * 10 * 4
    assert qbot2.Q.shape == (4 * 10 * 4, 3)

def test_qbot_load_strategy():
    # Test loading with existing file
    q_data = {
        'q_table': [[[0.1, 0.2, 0.3]] * (4 * 10 * 4)],
        'games_played': 42
    }
    
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=json.dumps(q_data))):
            qbot = QBot(num_buckets=10, save_path="test_q_strategy.json")
            assert qbot.games_played == 42
    
    # Test loading with error
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', side_effect=Exception("Test error")):
            with patch('sys.stdout', new=StringIO()):  # Capture print output
                qbot = QBot(num_buckets=10, save_path="test_q_strategy.json")
                # Should initialize with random values
                assert qbot.Q.shape == (4 * 10 * 4, 3)
                assert np.any(qbot.Q != 0)  # At least some values should be non-zero

def test_qbot_save_strategy():
    qbot = QBot(num_buckets=5, save_path="test_q_strategy.json")
    
    # Test successful save
    with patch('builtins.open', mock_open()) as mock_file:
        with patch('json.dump') as mock_json_dump:
            qbot.save_strategy()
            mock_file.assert_called_once_with("test_q_strategy.json", 'w')
            mock_json_dump.assert_called_once()
    
    # Test save with error
    with patch('builtins.open', side_effect=Exception("Test error")):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            qbot.save_strategy()
            output = fake_out.getvalue()
            assert "Error saving strategy" in output

def test_qbot_encode_state():
    qbot = QBot(num_buckets=10)
    
    # Test various state encodings
    state1 = qbot.encode_state(0, 0, 0)  # Preflop, lowest rank, no bets
    assert state1 == 0
    
    state2 = qbot.encode_state(1, 3726, 2)  # Flop, middle rank, both bet
    expected_bucket = int((3726 / 7462) * 10)
    assert state2 == 1 * 10 * 4 + expected_bucket * 4 + 2  # street * buckets * betting_states + bucket * betting_states + betting_state
    
    state3 = qbot.encode_state(3, 7461, 3)  # River, highest rank, player bet
    assert state3 == 3 * 10 * 4 + 9 * 4 + 3

def test_qbot_get_bucket():
    qbot = QBot(num_buckets=10)
    
    # Test bucket calculation
    assert qbot.get_bucket(0) == 0  # Best possible hand
    assert qbot.get_bucket(3731) == 5  # Middle hand (around 50%)
    assert qbot.get_bucket(7461) == 9  # Worst possible hand
    
    # Test boundary conditions
    assert qbot.get_bucket(7462) == 9  # Should cap at num_buckets - 1

def test_qbot_get_valid_actions():
    qbot = QBot()
    
    # Test different betting states
    assert qbot.get_valid_actions(0) == [1, 2]  # No bets yet: Check or Raise
    assert qbot.get_valid_actions(1) == [1, 2]  # Bot bet, player hasn't: Check or Raise
    assert qbot.get_valid_actions(2) == [1]     # Both bet same: Check/Call only
    assert qbot.get_valid_actions(3) == [0, 1, 2]  # Player bet, bot didn't: Fold, Call, or Raise
    
    # Test with raise cap reached
    assert qbot.get_valid_actions(3, raise_cap_reached=True) == [0, 1]  # Can't raise anymore

def test_qbot_choose_action():
    qbot = QBot(num_buckets=5)
    
    # Set specific Q-values for testing
    state = 42
    qbot.Q[state] = np.array([0.1, 0.5, 0.3])
    
    # Test with deterministic selection (epsilon = 0)
    with patch('random.random', return_value=0.9):  # Above epsilon
        # With all actions valid, should choose action 1 (highest Q-value)
        assert qbot.choose_action(state, [0, 1, 2]) == 1
        
        # With restricted valid actions
        assert qbot.choose_action(state, [0, 2]) == 2  # Now action 2 has highest among valid
        assert qbot.choose_action(state, [0]) == 0    # Only one valid action
    
    # Test with exploration (epsilon > random value)
    with patch('random.random', return_value=0.01):  # Below epsilon
        with patch('random.choice', return_value=2) as mock_choice:
            action = qbot.choose_action(state, [0, 1, 2])
            mock_choice.assert_called_once_with([0, 1, 2])
            assert action == 2

def test_qbot_record_and_update():
    with patch('new_bot.QBot.load_strategy'):  # Mock to skip actual loading
        qbot = QBot(num_buckets=5)

    original_q = qbot.Q.copy()
    
    # Record some actions
    qbot.record(10, 1)
    qbot.record(20, 0)
    assert len(qbot.trajectory) == 2
    assert qbot.trajectory[0] == (10, 1)
    assert qbot.trajectory[1] == (20, 0)
    
    # Test update with some reward
    with patch('new_bot.QBot.save_strategy'):  # Mock save to avoid file operations
        qbot.update(10.0)  # Apply positive reward
        
        # Verify Q-values were updated
        assert qbot.Q[20, 0] != original_q[20, 0]
        assert qbot.Q[10, 1] != original_q[10, 1]
        
        # Verify trajectory was cleared
        assert len(qbot.trajectory) == 0
        
        # Verify games_played was incremented
        assert qbot.games_played == 1

# Test bot_action function
def test_bot_action(mock_game_state):
    # Test fold action
    with patch('new_bot.QBot.choose_action', return_value=0):
        result = bot_action(mock_game_state)
        assert result == mock_game_state.players[0]  # Player wins when bot folds
    
    # Test check/call action
    mock_game_state.player_bet = 20
    with patch('new_bot.QBot.choose_action', return_value=1):
        with patch('sys.stdout', new=StringIO()):  # Capture print output
            result = bot_action(mock_game_state)
            assert result == 20
            assert mock_game_state.bot_bet == 20
            assert mock_game_state.current_bet == 20
    
    # Test raise action
    mock_game_state.player_bet = 10
    mock_game_state.bot_bet = 0
    mock_game_state.raise_count = 0
    with patch('new_bot.QBot.choose_action', return_value=2):
        with patch('sys.stdout', new=StringIO()):  # Capture print output
            result = bot_action(mock_game_state)
            assert result == 30  # player_bet (10) + raise (20)
            assert mock_game_state.bot_bet == 30
            assert mock_game_state.current_bet == 30
            assert mock_game_state.raise_count == 1

    # Test different streets
    for street, stage_name in enumerate(["preflop", "flop", "turn", "river"]):
        mock_game_state.stage = stage_name
        mock_game_state.bot_bet = 0
        mock_game_state.player_bet = 0
        
        with patch('new_bot.QBot.encode_state') as mock_encode:
            with patch('new_bot.QBot.choose_action', return_value=1):
                with patch('sys.stdout', new=StringIO()):
                    bot_action(mock_game_state)
                    # Verify the correct street was passed to encode_state
                    mock_encode.assert_called_once()
                    args, _ = mock_encode.call_args
                    assert args[0] == street

def test_bot_action_error_handling(mock_game_state):
    # Test with error in get_hand_rank
    with patch('new_bot.get_hand_rank', side_effect=Exception("Test error")):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with patch('new_bot.QBot.choose_action', return_value=1):
                result = bot_action(mock_game_state)
                output = fake_out.getvalue()
                assert "Error getting hand rank" in output
                assert result == mock_game_state.player_bet  # Should still work despite error

    # Test with no valid actions (shouldn't normally happen)
    with patch('new_bot.QBot.get_valid_actions', return_value=[]):
        with patch('sys.stdout', new=StringIO()):
            result = bot_action(mock_game_state)
            assert result == 0  # Default action for no valid actions

if __name__ == "__main__":
    pytest.main()