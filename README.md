# Tic-Tac-Toe — BFS AI Agent

**CIA-1 Part 5 | Course: ITPCC510 / Artificial Intelligence**
Fr. C. Rodrigues Institute of Technology, Vashi
**Student:** Neha Yadav | **Roll No:** 5024143 | **Semester:** V (2026-27)
**Faculty:** Dr. S. L. Vaikole

---

## Reference Paper

> *"Intelligent Agent Systems: Evolving Decision-Making Models and Applications"*
> Boujia Mohammed Amine & Sabbane Mohamed
> 2024 Mediterranean Smart Cities Conference (MSCC), IEEE
> DOI: [10.1109/MSCC62288.2024.10697074](https://doi.org/10.1109/MSCC62288.2024.10697074)

---

## Problem Statement

An intelligent AI agent plays Tic-Tac-Toe against a human opponent on a 3×3 grid. The agent must select the optimal move at each turn — aiming to win in the fewest possible moves, or force a draw if winning is not guaranteed.

This implements the concepts developed across all 5 parts of CIA-1:
- **Part 1:** Problem formulated as a goal-based multi-agent adversarial task (fully observable, deterministic, sequential, static, discrete)
- **Part 2:** BFS selected and applied as the AI search method
- **Part 3:** Knowledge-based inference (win/block detection using FOL rules) applied before BFS runs
- **Part 4:** Reinforcement Learning (Q-Learning) identified as the learning technique
- **Part 5 (this):** Full implementation using Python + pygame

---

## How it Works — AI Decision Pipeline

```
Human makes a move
        ↓
KB Inference (Part 3)
  → Can AI win immediately?  YES → play that cell
  → Can opponent win next?   YES → block that cell
        ↓ (if neither)
BFS Search (Part 2)
  → Explore all future game states level by level
  → Find the shallowest path to a win
  → Fall back to strategic cell preference (centre → corners → edges)
        ↓
AI plays chosen cell
```

### BFS Explained

- Each **node** = a board state (which cells have X, O, or are empty)
- Each **edge** = placing AI's symbol (O) in one empty cell
- BFS explores depth 1 first (all immediate moves), then depth 3 (AI move + opponent reply + AI move), and so on
- The **first winning state found = shallowest win = optimal move**
- Total state space: at most 362,880 paths (9! permutations), but KB pruning reduces this significantly

### Why BFS over other methods

| Method | Why not chosen |
|---|---|
| DFS | Goes deep before wide — may miss faster wins |
| UCS | Identical to BFS when all move costs are equal (they are here) |
| Greedy / A* | Require a heuristic — no reliable admissible heuristic for Tic-Tac-Toe |
| **BFS** | ✅ Complete, finds shallowest win, no heuristic needed, feasible state space |

---

## Project Structure

```
tic-tac-toe-ai/
├── main.py          # pygame GUI + game loop
├── bfs.py           # BFS AI logic + KB inference
├── requirements.txt # dependencies
└── README.md        # this file
```

---

## Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/nyumidk/tic-tac-toe-ai.git
cd tic-tac-toe-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the game
```bash
python main.py
```

---

## How to Play

| Action | How |
|---|---|
| Make a move | Click any empty cell on the board |
| See AI reasoning | Watch the **BFS Search Log** panel on the right |
| Start a new game | Click the **New Game** button |
| Quit | Close the window |

- **You are X** (blue), **AI is O** (red)
- The BFS log panel shows exactly how the AI chose its move — states explored, depth reached, and final decision
- The terminal also prints the full BFS log for each AI move

---

## Sample BFS Output (Terminal)

```
[Human] Played cell 4

=======================================================
  BFS AI THINKING...
=======================================================
  Level 0 (current): 8 empty cells
  Exploring 8 immediate moves via BFS...
  [BFS] WIN path found at depth 1 via cell 0
  [BFS] States explored so far: 1
  Total states explored: 1
    Depth 1: 1 states
  CHOSEN MOVE: cell 0
=======================================================
```

---

## Screenshots

*(Add screenshots of the game here after running it)*

---

## Connection to Reference Paper

The paper (*Boujia & Sabbane, 2024*) discusses intelligent agent systems and their decision-making models. This implementation directly applies:

| Paper Section | Concept | Implementation |
|---|---|---|
| Section II-B-1 | Intelligent Agent (perceives environment via sensors, acts via actuators) | Agent reads board state (sensor), places symbol (actuator) |
| Section II-B-3 | Decision-making models — rule-based + search | KB win/block rules (Part 3) + BFS (Part 2) |
| Section III-B | Game Theory — adversarial agents with opposing goals | Human (X) vs AI (O) — competitive multi-agent environment |
| Section IV-B | MAS in real-time systems | Real-time move selection with BFS log shown live |

---

## Learning Outcomes Addressed

- **LO 2.4:** Select and apply best searching method to solve a given problem ✅ (BFS)
- **LO 6.1, 6.2:** Design and develop AI applications in real world scenarios using AI tools ✅ (Python + pygame)
