from openai import OpenAI
import random
import os
from apikeys import api_key
from view import PokerView


def bot_bet_handling(self):
    self.chips[self.players[1]] -= self.bot_bet - self.previous_bot_bet
    self.previous_bot_bet = self.bot_bet


client = OpenAI(api_key=api_key)


# Function to send the prompt to OpenAI API and get a decision
def get_decision_from_openai(self):

    # Prepare the context for the game state
    prompt = f"""
    Poker round: {self.stage}
    Bot (You) hand: {self.bot_hand}
    Community cards: {self.community_cards}
    Player's stack: {self.chips[self.players[0]]}
    Bot's stack: {self.chips[self.players[1]]}
    Pot size: {self.pot}
    Current bet: {self.current_bet}
    Player's bet: {self.player_bet}
    Previous bot bet: {self.previous_bot_bet}
    Previous actions: Player bet {self.player_bet}, Bot bet {self.bot_bet}
    
    What should the bot do next, optimally speaking? Respond with one of the following options: 'fold', 'check', 'call', 'raise'. 
    Please only respond with the action, no extra information. No apostrophes, only the letters for the word.
    """

    # Query OpenAI to get the bot's decision
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # Or another model you prefer
        messages=[
            {"role": "system", "content": "You are an assistant helping a poker game."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "text"},
        max_tokens=50,
        temperature=0.7,
    )

    # Parsing the OpenAI response into a structured dictionary
    try:
        # Access the 'content' from the first choice's message
        choice = response.choices[0].message.content.strip().lower()
    except (IndexError, KeyError):
        choice = "fold"  # Default action in case of an error in parsing

    return choice


# Updated bot_action method using OpenAI decision
def bot_action(self):
    """Bot's action based on OpenAI API's decision"""
    actions = []

    # Determine possible actions based on current bets
    if self.player_bet == self.bot_bet:
        actions = ["check", "raise"]
    elif self.player_bet > self.bot_bet:
        actions = ["fold", "call", "raise"]

    # Use OpenAI to make the decision
    action = get_decision_from_openai(self)  # Get decision from OpenAI
    PokerView.display_bot_decision(
        self, action, self.stage
    )  # Display decision on the screen
    # Perform action based on the decision

    if action == "fold":
        print(self.players[0])
        return self.players[0]  # Bot folds, Player Wins
    elif action == "check":
        print("Bot Checked")
        return 0
    elif action == "call":
        print("Bot Called")
        self.bot_bet = self.player_bet
        bot_bet_handling(self)  # Make sure to handle the bet
        return self.current_bet
    elif action == "raise":
        raise_amount = random.randint(1, 100) + (
            self.player_bet - self.bot_bet
        )  # Random raise on top of the bet
        print(f"Bot raised to {raise_amount + self.bot_bet}")
        self.bot_bet += raise_amount
        self.current_bet = self.bot_bet
        bot_bet_handling(self)  # Update bet
        PokerView.display_bot_decision(
            self, action, self.stage, raise_amount
        )  # Display decision on the screen
        return self.current_bet
    else:
        print("Bot did something?????")
