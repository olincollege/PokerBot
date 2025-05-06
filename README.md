# Limit Hold'em Poker Clone
*A student-friendly, fixed-limit Texas Hold'em sandbox built with **Pygame***
---
## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [File Overview](#file-overview)
4. [Installation](#installation)
5. [Running the Game](#running-the-game)
6. [Executing Tests](#executing-tests)
7. [Gameplay & Controls](#gameplay--controls)
8. [Contributors](#contributors)
---
## Project Overview
Welcome to **Limit Hold'em Poker Clone** – a lightweight classroom project that lets you explore the core logic of *fixed-limit* Texas Hold'em without the complexity of a full casino client. It is intentionally streamlined for learning:
* **Model-View-Controller** (MVC) architecture keeps graphics, game state, and input handling cleanly separated.  
* A simple **Q-learning bot** demonstrates how reinforcement learning can adapt betting strategy over many hands.  

## Architecture
| Layer          | Responsibilities                                                                                                                                                                               | Key Classes     |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| **Model**      | • Create & shuffle deck<br>• Enforce **fixed-limit betting** (small bet / big bet, max three raises)<br>• Track chip stacks, pot, blinds & showdown<br>• Hook for reinforcement-learning agent | `Model`, `QBot` |
| **View**       | • Load/scale sprites<br>• Render cards, chips, text overlays                                                                                                                                   | `PokerView`     |
| **Controller** | • Capture mouse / keyboard events<br>• Map them to model actions (Fold / Call / Raise / Check, Start Game)                                                                                     | `Controller`    |
---
## File Overview
| File                       | Description                                                   |
|----------------------------|---------------------------------------------------------------|
| `main.py`                  | Entry point that launches the game                            |
| `model.py`                 | Core game logic and state management                          |
| `view.py`                  | Game rendering and visual components                          |
| `controller.py`            | Input handling and user interactions                          |
| `ML_bot.py`                | Q-learning bot implementation                                 |
| `hand_evaluator.py`        | Hand strength evaluation logic                                |
| `hand_evaluator_data.py`   | Data structures for hand evaluation                           |
| `generate_preflop_strength.py` | Creates probability data for starting hands               |
| `train_ML_bot.py`          | Training script for the Q-learning bot                        |
| `config.py`                | Game configuration settings                                   |
| `tests/*.py`               | Unit tests for various components                             |

## Installation
```bash
git clone https://github.com/olincollege/PokerBot.git
cd PokerBot
pip install -r requirements.txt
```

## Running the Game
1. Generate preflop strength data (take a look at json results - you can see the probability of each hand winning heads up against the range of all hands):
```bash
python generate_preflop_strength.py
```

2. Train the ML bot (replace 1000 with desired number of training hands. Not strictly required, but the more iterations you do this the better the bot will be. Can be run multiple times. Bot will make ~random decisions without.):
```bash
python train_ML_bot.py 1000
```

3. Start the game:
```bash
python main.py
```

## Executing Tests
Run specific tests with verbose output:
```bash
python -m pytest tests/controller_tests.py -v
python -m pytest tests/model_tests.py -v
python -m pytest tests/view_tests.py -v
```