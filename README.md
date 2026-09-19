# Tic-Tac-Toe — Hybrid AI Agent (KB + ML + BFS)

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

An intelligent AI agent plays Tic-Tac-Toe against a human opponent on a 3×3 grid, choosing the best possible move at each turn — aiming to win in the fewest moves, or force a draw if winning is impossible. The agent uses a three-stage decision pipeline that combines knowledge-based inference, machine learning, and search — integrating the concepts from all 5 parts of CIA-1.

---

## AI Decision Pipeline

```
┌─────────────────────────────────────────────────────┐
│              AI DECISION PIPELINE                   │
│                                                     │
│  Stage 1: KB Inference (Part 3)                     │
│    → Can AI win immediately?   YES → play that cell │
│    → Can opponent win next?    YES → block that cell │
│                 ↓ (neither)                         │
│  Stage 2: ML Prediction (Part 4 — scikit-learn)     │
│    → Random Forest trained on past games            │
│    → If confidence ≥ 60%  →  use ML move            │
│                 ↓ (low confidence / untrained)      │
│  Stage 3: BFS Search (Part 2)                       │
│    → Explore all future states level by level       │
│    → Find shallowest winning path                   │
│    → Fallback: centre → corners → edges             │
└─────────────────────────────────────────────────────┘
```

Each stage is colour-coded in the in-game log panel:
- 🟠 **Orange** = KB Inference
- 🟣 **Purple** = ML Prediction
- 🟢 **Green**  = BFS Search

---

## How the ML Agent Learns

After every completed game, the agent records every board state and move it played, along with the outcome (win / draw / loss). Winning game records are oversampled (stored 3×) to bias the model toward successful strategies.

Once **10 games** have been recorded, a **Random Forest Classifier** (scikit-learn) is trained on this data. Every 5 games thereafter, the model retrains on the growing dataset. Over time:

- The ML model increasingly takes over from BFS
- The agent learns to recognise good positions from experience rather than computing them
- Win rate against random / weak opponents improves with each game played

Game data and the trained model persist across sessions in:
- `game_data.pkl` — accumulated training examples
- `rf_model.pkl`  — the trained Random Forest model

---

## Connection to CIA-1 Parts

| CIA Part | Concept | Implementation |
|---|---|---|
| Part 1 | Problem formulation, PEAS, task environment | Tic-Tac-Toe as fully observable, discrete, sequential, multi-agent adversarial problem |
| Part 2 | BFS search | `bfs.py` — explores game states level by level to find shallowest win |
| Part 3 | Knowledge-based agent, FOL inference | Immediate win/block detection before any search runs |
| Part 4 | Learning technique (RL / supervised) | `ml_agent.py` — Random Forest trains on game history |
| Part 5 | Implementation + demonstration | This repo — pygame GUI + full hybrid AI pipeline |

---

## Connection to Reference Paper

| Paper Section | Concept | Implementation Here |
|---|---|---|
| Section II-B-1 | Intelligent agent (sensors + actuators) | Reads board (sensor), places symbol (actuator) |
| Section II-B-3 | Decision-making: rule-based + search + ML | KB → ML → BFS pipeline |
| Section III-B | Game Theory — adversarial rational agents | Human (X) vs AI (O) — opposing goals |
| Section III-D | Deep learning enriching decision-making | ML (Random Forest) learning from experience |
| Section V-B | Computational efficiency | KB pruning eliminates BFS in ~30% of turns |

---

## Project Structure

```
tic-tac-toe-ai/
├── main.py          # pygame GUI + game loop + AI integration
├── bfs.py           # BFS search + KB inference
├── ml_agent.py      # scikit-learn Random Forest ML agent
├── requirements.txt # dependencies
├── README.md        # this file
├── game_data.pkl    # generated after first game — ML training data
└── rf_model.pkl     # generated after 10 games — trained model
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
| Make a move | Click any empty cell |
| See AI reasoning | Watch the **AI Decision Log** panel (right side) |
| New game | Click **New Game** button |
| Reset ML learning | Click **Reset ML** button |
| Quit | Close the window |

- **You are X** (blue), **AI is O** (red)
- A badge below the board shows which method the AI used last (KB / ML / BFS)
- The ML status line updates live as the model learns

---

## Screenshots



![Tic-Tac-Toe Hybrid AI](tic-tac-toe1 (1))
![Tic-Tac-Toe Hybrid AI](tic-tac-toe1 (2))
![Tic-Tac-Toe Hybrid AI](tic-tac-toe1 (3))


---

## Sample Terminal Output

```
[Human] Cell 4

================================================
  AI DECISION PIPELINE
================================================
  Stage 1: KB Inference
  [KB] No immediate win/block.
  Stage 2: ML Prediction
  [ML] No model yet — need ~8 more games
  Stage 3: BFS Search
  ====================================================
    BFS AI THINKING...
  ====================================================
    Exploring 8 moves via BFS...
    [BFS] Win at depth 5 via cell 0
    [BFS] States explored: 546
    Total states explored: 546
      Depth 1: 9 states
      Depth 3: 504 states
      Depth 5: 33 states
    CHOSEN MOVE → cell 0
  ====================================================
  FINAL → cell 0 via [BFS]
================================================
```
