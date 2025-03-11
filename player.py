def player_bet_handling(self):
        self.chips[self.players[0]] -= (
            self.player_bet - self.previous_player_bet
        )
        self.previous_player_bet = self.player_bet



def player_action(self):
        """Player's action during the betting round (e.g., fold, check, bet, etc.)"""
        print(f"\n{self.players[0]}'s turn.")
        if self.player_bet < self.bot_bet:
            print(f"How much to call: {self.bot_bet-self.player_bet}")
            action = input("Choose action (fold, call, raise): ").lower()
        else:
            action = input("Choose action (fold, check, call, raise): ").lower()

        if action == "fold":
            return "Bot"  # Player folds, end hand with Bot Win
        elif action == "check":
            if self.player_bet < self.bot_bet:
                print("Invalid action. Try again.")
                return player_action(self)
            return 0  # Player checks, stays in the pot
        elif action == "call":
            self.player_bet = self.current_bet
            player_bet_handling(self)
            print("Player Called")
            return "continue"
            # Player calls
        elif action == "raise":
            raise_amount = int(input("Raise your current bet by: "))
            if (
                self.player_bet + raise_amount > self.bot_bet
            ):  # Make sure raise amount is more than bot bet
                self.player_bet += raise_amount
                self.current_bet = self.player_bet
                player_bet_handling(self)
                return "continue"
            else:
                print("Invalid Raise Amount Try Again")
                return self.player_action()

        else:
            print("Invalid action. Try again.")
            return player_action(self)