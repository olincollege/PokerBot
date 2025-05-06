"""
Unit tests for the hand evaluator module.
This module tests the functionality of the hand evaluation functions,
including the evaluation of 5-card, 6-card, and 7-card hands.
"""

import pytest
import random
from unittest.mock import patch
from io import StringIO

# Import the module to test
from hand_evaluator import (
    _SUITS, _RANKS, _PRIMES, RANK_NAMES, SUIT_NAMES, DECK, _DECK,
    LOOKUP, hash_function, eval5, eval6, eval7, one_round5, one_round7,
    HASH_ADJUST, HASH_VALUES, FLUSHES, UNIQUE_5
)

# Test fixture for common hand types
@pytest.fixture
def sample_hands():
    return {
        # Royal flush
        'royal_flush': ['ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades'],
        # Straight flush
        'straight_flush': ['9_of_diamonds', '8_of_diamonds', '7_of_diamonds', '6_of_diamonds', '5_of_diamonds'],
        # Four of a kind
        'four_of_a_kind': ['ace_of_spades', 'ace_of_hearts', 'ace_of_diamonds', 'ace_of_clubs', 'king_of_spades'],
        # Full house
        'full_house': ['king_of_spades', 'king_of_hearts', 'king_of_diamonds', 'queen_of_clubs', 'queen_of_spades'],
        # Flush
        'flush': ['ace_of_hearts', '10_of_hearts', '8_of_hearts', '6_of_hearts', '4_of_hearts'],
        # Straight
        'straight': ['9_of_spades', '8_of_hearts', '7_of_diamonds', '6_of_clubs', '5_of_spades'],
        # Three of a kind
        'three_of_a_kind': ['queen_of_spades', 'queen_of_hearts', 'queen_of_diamonds', '10_of_clubs', '8_of_spades'],
        # Two pair
        'two_pair': ['jack_of_spades', 'jack_of_hearts', '8_of_diamonds', '8_of_clubs', 'ace_of_spades'],
        # One pair
        'one_pair': ['10_of_spades', '10_of_hearts', 'ace_of_diamonds', 'king_of_clubs', 'queen_of_spades'],
        # High card
        'high_card': ['ace_of_spades', 'king_of_hearts', 'queen_of_diamonds', 'jack_of_clubs', '9_of_spades'],
    }

# Test basic constants and card representation
def test_deck_constants():
    # Check if the deck has the correct number of cards
    assert len(DECK) == 52
    assert len(_DECK) == 52
    assert len(LOOKUP) == 52
    
    # Verify that RANK_NAMES and SUIT_NAMES contain the expected values
    assert RANK_NAMES == ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
    assert SUIT_NAMES == ["spades", "clubs", "diamonds", "hearts"]
    
    # Test that each card in the deck is unique
    assert len(set(DECK)) == 52
    assert len(set(_DECK)) == 52

def test_lookup_mapping():
    # Test that lookup mapping works correctly for a few cards
    assert 'ace_of_spades' in LOOKUP
    assert 'king_of_hearts' in LOOKUP
    assert '2_of_clubs' in LOOKUP
    
    # Test that the encoding format is consistent
    for card_name in DECK:
        rank_name, suit_name = card_name.split('_of_')
        rank_index = RANK_NAMES.index(rank_name)
        suit_index = SUIT_NAMES.index(suit_name)
        
        # Verify the card encoding contains the right components
        encoded_card = LOOKUP[card_name]
        assert encoded_card & 0xF000  # Has suit bits
        assert encoded_card & 0xFF00  # Has rank bits
        assert encoded_card & 0xFF    # Has prime bits

# Test hand evaluation functions
def test_eval5_ranking(sample_hands):
    # Get scores for each hand type
    scores = {hand_type: eval5(cards) for hand_type, cards in sample_hands.items()}
    
    # Expected ranking (from best to worst)
    expected_ranking = [
        'royal_flush',
        'straight_flush',
        'four_of_a_kind',
        'full_house',
        'flush',
        'straight',
        'three_of_a_kind',
        'two_pair',
        'one_pair',
        'high_card'
    ]
    
    # Check that the scores reflect the correct ranking
    for i in range(len(expected_ranking) - 1):
        better_hand = expected_ranking[i]
        worse_hand = expected_ranking[i + 1]
        assert scores[better_hand] < scores[worse_hand], f"{better_hand} should rank better than {worse_hand}"

def test_eval5_specific_hands():
    # Test specific hand evaluation for correctness
    royal_flush = ['ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades']
    high_card = ['ace_of_spades', 'king_of_hearts', 'queen_of_diamonds', 'jack_of_clubs', '9_of_spades']
    
    royal_flush_score = eval5(royal_flush)
    high_card_score = eval5(high_card)
    
    assert royal_flush_score < high_card_score

def test_eval6_vs_eval5():
    # Generate a 6-card hand
    six_card_hand = ['ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades', '2_of_hearts']
    
    # The best 5-card hand should be the royal flush
    best_5_card_hand = ['ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades']
    
    # Scores should match
    assert eval6(six_card_hand) == eval5(best_5_card_hand)

def test_eval7_vs_eval5():
    # Generate a 7-card hand (typical in Texas Hold'em)
    seven_card_hand = [
        'ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades',
        '2_of_hearts', '3_of_hearts'
    ]
    
    # The best 5-card hand should be the royal flush
    best_5_card_hand = ['ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades']
    
    # Scores should match
    assert eval7(seven_card_hand) == eval5(best_5_card_hand)

# Test helper functions
def test_hash_function():
    # Make sure hash_function returns consistent results
    # Use a specific product value to test hash_function
    product = 2 * 3 * 5 * 7 * 11  # Product of the first 5 primes
    hash_result = hash_function(product)
    
    # Call it again with the same input and verify consistency
    assert hash_function(product) == hash_result

# Test output functions using mocking
def test_one_round5_output():
    # Mock the random.shuffle function to ensure deterministic results
    with patch('random.shuffle') as mock_shuffle:
        # Make shuffle do nothing (keeping the sorted deck)
        mock_shuffle.side_effect = lambda x: None
        
        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_out:
            one_round5()
            output = fake_out.getvalue()
            
            # Basic check for expected output format
            assert "beats" in output or "ties" in output

def test_one_round7_output():
    # Mock the random.shuffle function to ensure deterministic results
    with patch('random.shuffle') as mock_shuffle:
        # Make shuffle do nothing (keeping the sorted deck)
        mock_shuffle.side_effect = lambda x: None
        
        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_out:
            one_round7()
            output = fake_out.getvalue()
            
            # Basic check for expected output format
            assert "[" in output  # Should display hands
            assert "beats" in output or "ties" in output

# Property-based tests
def test_deck_integrity():
    # Check that every card in the deck has a unique encoding
    encoded_values = [LOOKUP[card] for card in DECK]
    assert len(encoded_values) == len(set(encoded_values)), "Card encodings should be unique"

def test_eval5_deterministic():
    # Test that eval5 gives consistent results for the same hand
    test_hand = ['ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades']
    first_result = eval5(test_hand)
    
    # Call it multiple times and check consistency
    for _ in range(5):
        assert eval5(test_hand) == first_result, "eval5 should be deterministic"

def test_eval5_invariant_to_order():
    # Test that eval5 is invariant to the order of cards
    test_hand = ['ace_of_spades', 'king_of_spades', 'queen_of_spades', 'jack_of_spades', '10_of_spades']
    original_score = eval5(test_hand)
    
    # Shuffle the hand and verify the score remains the same
    for _ in range(5):
        shuffled_hand = test_hand.copy()
        random.shuffle(shuffled_hand)
        assert eval5(shuffled_hand) == original_score, "Hand evaluation should be invariant to card order"

# Add more comprehensive tests for specific card combinations and edge cases
def test_flush_detection():
    # Test flush detection logic
    flush_hand = ['2_of_hearts', '5_of_hearts', '7_of_hearts', '9_of_hearts', 'king_of_hearts']
    non_flush_hand = ['2_of_hearts', '5_of_hearts', '7_of_hearts', '9_of_hearts', 'king_of_spades']
    
    flush_score = eval5(flush_hand)
    non_flush_score = eval5(non_flush_hand)
    
    # Flush should rank better than non-flush
    assert flush_score < non_flush_score

def test_straight_detection():
    # Test straight detection logic
    straight_hand = ['5_of_hearts', '6_of_spades', '7_of_diamonds', '8_of_clubs', '9_of_hearts']
    non_straight_hand = ['5_of_hearts', '6_of_spades', '7_of_diamonds', '8_of_clubs', 'king_of_hearts']
    
    straight_score = eval5(straight_hand)
    non_straight_score = eval5(non_straight_hand)
    
    # Straight should rank better than non-straight high card
    assert straight_score < non_straight_score

def test_ace_low_straight():
    # Test the 'wheel' straight (A-2-3-4-5)
    wheel_straight = ['ace_of_hearts', '2_of_spades', '3_of_diamonds', '4_of_clubs', '5_of_hearts']
    regular_straight = ['5_of_hearts', '6_of_spades', '7_of_diamonds', '8_of_clubs', '9_of_hearts']
    
    wheel_score = eval5(wheel_straight)
    regular_score = eval5(regular_straight)
    
    # Both should be straights
    # Regular straight should rank better than wheel straight
    assert regular_score < wheel_score
    
    # But wheel should still rank better than a high card hand
    high_card_hand = ['ace_of_hearts', 'king_of_spades', 'queen_of_diamonds', 'jack_of_clubs', '9_of_hearts']
    high_card_score = eval5(high_card_hand)
    
    assert wheel_score < high_card_score

if __name__ == "__main__":
    pytest.main()