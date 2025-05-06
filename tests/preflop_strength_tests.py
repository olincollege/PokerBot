import pytest
import random
import json
from pathlib import Path
import os

# Import from the hand evaluator module
from hand_evaluator import eval7, DECK, LOOKUP, RANK_NAMES, SUIT_NAMES

# Import functions to test from your module
from generate_preflop_strength import (
    to_card_name,
    gen_all_starting_hands,
    create_hand_from_string,
    simulate_equity
)

class TestPreflopStrength:
    
    def test_to_card_name(self):
        """Test the card name conversion function."""
        assert to_card_name('A', 's') == "ace_of_spades"
        assert to_card_name('K', 'h') == "king_of_hearts"
        assert to_card_name('Q', 'd') == "queen_of_diamonds"
        assert to_card_name('J', 'c') == "jack_of_clubs"
        assert to_card_name('T', 's') == "10_of_spades"
        assert to_card_name('9', 'h') == "9_of_hearts"
        assert to_card_name('2', 'c') == "2_of_clubs"
    
    def test_gen_all_starting_hands(self):
        """Test that we generate all 169 canonical preflop hands."""
        hands = gen_all_starting_hands()
        
        # Check the total count
        assert len(hands) == 169
        
        # Check for specific hand types
        assert 'AA' in hands  # Pocket pair
        assert 'AKs' in hands  # Suited connectors
        assert 'AKo' in hands  # Offsuit connectors
        assert '72o' in hands  # Worst starting hand
        
        # Test that all pocket pairs are there (13 total)
        pairs = [h for h in hands if h[0] == h[1]]
        assert len(pairs) == 13
        
        # Test that suited and offsuit hands are balanced
        suited = [h for h in hands if h.endswith('s')]
        offsuit = [h for h in hands if h.endswith('o')]
        assert len(suited) == len(offsuit) == 78  # 13*12/2 = 78
    
    def test_create_hand_from_string(self):
        """Test that hand strings are converted to actual card combinations."""
        # Test pocket pair
        aa_hands = create_hand_from_string('AA')
        assert len(aa_hands) == 12  # 12 combinations of AA
        
        # Verify specific combinations exist in AA
        assert ['ace_of_spades', 'ace_of_hearts'] in aa_hands
        assert ['ace_of_clubs', 'ace_of_diamonds'] in aa_hands
        
        # Test suited hand
        aks_hands = create_hand_from_string('AKs')
        assert len(aks_hands) == 4  # 4 suits
        
        # Verify all suited hands are actually suited
        for hand in aks_hands:
            assert hand[0].split('_of_')[1] == hand[1].split('_of_')[1]
        
        # Test offsuit hand
        ako_hands = create_hand_from_string('AKo')
        assert len(ako_hands) == 12  # 4*3 = 12 ways to choose 2 different suits
        
        # Verify all offsuit hands have different suits
        for hand in ako_hands:
            assert hand[0].split('_of_')[1] != hand[1].split('_of_')[1]
    
    @pytest.mark.parametrize("hand", ["AA", "KK", "QQ", "AKs", "AKo", "72o"])
    def test_simulate_equity_sanity(self, hand):
        """Test that equity simulation returns reasonable results."""
        # Using low trial count for speed in tests
        equity = simulate_equity(hand, num_trials=1000)
        
        # Check that equity is a reasonable number
        assert 0 <= equity <= 1
        
        # Check that strong hands have higher equity
        if hand in ["AA", "KK", "QQ"]:
            assert equity > 0.7  # Premium pairs should have high equity
        elif hand in ["AKs", "AKo"]:
            assert equity > 0.5  # Strong unpaired hands
        elif hand == "72o":
            assert equity < 0.4  # Worst starting hand
    
    def test_equity_ordering(self):
        """Test that hand equities follow expected ordering."""
        # Test with small trial count for speed
        aa_equity = simulate_equity("AA", num_trials=1000)
        kk_equity = simulate_equity("KK", num_trials=1000)
        aks_equity = simulate_equity("AKs", num_trials=1000)
        ako_equity = simulate_equity("AKo", num_trials=1000)
        
        # Check expected ordering
        assert aa_equity > kk_equity  # AA beats KK
        assert aks_equity > ako_equity  # Suited beats offsuit
    
    @pytest.mark.slow
    def test_full_simulation(self, tmpdir):
        """Test the full simulation (marked as slow)."""
        # Create a temporary file for output
        output_file = os.path.join(tmpdir, "test_preflop_strength.json")
        
        # Run simulation with reduced trials
        hands = gen_all_starting_hands()
        table = {}
        for hand in hands[:5]:  # Only test first 5 hands to save time
            table[hand] = round(simulate_equity(hand, num_trials=1000), 4)
        
        with open(output_file, "w") as f:
            json.dump(table, f)
        
        # Check that file was created and has content
        assert os.path.exists(output_file)
        with open(output_file, "r") as f:
            loaded_data = json.load(f)
        
        assert len(loaded_data) == 5
        for hand in hands[:5]:
            assert hand in loaded_data
            assert 0 <= loaded_data[hand] <= 1

    @pytest.fixture
    def mock_eval7(self, monkeypatch):
        """Mock the eval7 function for deterministic testing."""
        def mock_function(cards):
            # Simple mock that returns higher values for better hands
            # based on the first card rank only (just for testing)
            ranks = {'ace': 14, 'king': 13, 'queen': 12, 'jack': 11, 
                    '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, 
                    '4': 4, '3': 3, '2': 2}
            
            # Extract the rank from first card
            first_card_rank = cards[0].split('_of_')[0]
            return 15 - ranks.get(first_card_rank, 0)  # Invert so lower is better
            
        monkeypatch.setattr('hand_evaluator.eval7', mock_function)
        return mock_function
    
    def test_simulate_with_mock(self, mock_eval7):
        """Test simulation using a mocked eval7 function."""
        # With our mock, AA win most of the time
        aa_equity = simulate_equity("AA", num_trials=100)
        assert 0.75 < aa_equity < 0.95  # Roughly 85% win rate with our mock
        
        # And 22 should win roughly half of the time
        low_equity = simulate_equity("22", num_trials=100)
        assert 0.4 < low_equity < 0.6