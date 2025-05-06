# Limit Hold’em Poker Clone

*A student‑friendly, fixed‑limit Texas Hold’em sandbox built with **Pygame***

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Running the Game](#running-the-game)
5. [Gameplay & Controls](#gameplay--controls)
6. [Contributors](#contributors)

---

## Project Overview

Welcome to **Limit Hold’em Poker Clone** – a lightweight classroom project that lets you explore the core logic of *fixed‑limit* Texas Hold’em without the complexity of a full casino client.  It is intentionally streamlined for learning:

* **Model‑View‑Controller** (MVC) architecture keeps graphics, game state, and input handling cleanly separated.
* A simple **Q‑learning bot** demonstrates how reinforcement learning can adapt betting strategy over many hands.
* Code comments are concise, and there’s **no mandatory automated‑test suite** – students can run, tweak, and immediately see results.

  
### Live Demo  
Try the web build here: <https://v0-softdes-poker-website.vercel.app/>


---

## Architecture

| Layer          | Responsibilities                                                                                                                                                                               | Key Classes     |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| **Model**      | • Create & shuffle deck<br>• Enforce **fixed‑limit betting** (small bet / big bet, max three raises)<br>• Track chip stacks, pot, blinds & showdown<br>• Hook for reinforcement‑learning agent | `Model`, `QBot` |
| **View**       | • Load/scale sprites<br>• Render cards, chips, text overlays                                                                                                                                   | `PokerView`     |
| **Controller** | • Capture mouse / keyboard events<br>• Map them to model actions (Fold / Call / Raise / Check, Start Game)                                                                                     | `Controller`    |

---

## Installation

```bash
git clone https://github.com/your‑org/limit‑holdem‑clone.git
cd limit‑holdem‑clone
pip install -r requirements.txt   # pygame ≥ 2.6, numpy, eval7
```

Python 3.9+ is recommended.

---

## Running the Game

```bash
python main.py
```

A **Start New Game** button appears; click it (or press **Enter**) to shuffle, post blinds, and begin the hand.

---

## Gameplay & Controls

| Action                          | Input                                                                                           |
| ------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Fold / Call / Raise / Check** | *Left‑click* the red buttons on the right                                                       |
| **Raises**                      | Each click of **Raise** adds exactly one fixed‑limit bet (three total raises allowed per round) |
| **Quit**                        | Close the window or press `Ctrl+C` in the terminal                                              |

Blinds rotate automatically after each hand and the bot updates its strategy based on the outcome.

---


## Contributors

| Name                 | Role                            |
| -------------------- | ------------------------------- |
| **Suraj Sajjala**    | Gameplay logic & RL integration |
| **Sreesanth Adelli** | Assets & UI polish              |
| **Troy Anderson**    | Architecture guidance           |

> *Built for Olin College students – experiment, modify, and deal the next hand!*  include lin [https://v0-softdes-poker-website.vercel.app/](https://v0-softdes-poker-website.vercel.app/)
