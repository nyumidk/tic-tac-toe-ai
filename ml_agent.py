"""
ml_agent.py — Scikit-learn ML Agent for Tic-Tac-Toe
------------------------------------------------------
Implements the learning component (CIA-1 Part 4 — Reinforcement/Learning).

The agent records every (board_state, move_played, outcome) triplet from
past games. Once enough data is collected, a Random Forest Classifier is
trained to predict the best move from board state alone — pure experience,
no search needed.

Pipeline:
  After each game → save game history to dataset
  Every N games   → retrain the Random Forest on accumulated data
  During play     → if model is trained AND confident → use ML move
                    otherwise fall back to BFS

CIA-1 Part 5 | Course: ITPCC510 / AI
Fr. C. Rodrigues Institute of Technology, Vashi
Student: Neha Yadav | Roll No: 5024143
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Files for persistence across sessions
DATA_FILE  = "game_data.pkl"
MODEL_FILE = "rf_model.pkl"

# Minimum games before we train the ML model
MIN_GAMES_TO_TRAIN = 10
# Retrain every N games
RETRAIN_EVERY      = 5
# Minimum confidence for ML move to be used over BFS
MIN_CONFIDENCE     = 0.60

AI    = "O"
HUMAN = "X"


def encode_board(board):
    """
    Encode board as a numeric feature vector for scikit-learn.
    "" → 0, "X" → 1, "O" → 2
    Returns a list of 9 integers.
    """
    mapping = {"": 0, HUMAN: 1, AI: 2}
    return [mapping[cell] for cell in board]


class MLAgent:
    def __init__(self):
        self.data   = self._load_data()
        self.model  = self._load_model()
        self.games_since_retrain = 0

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "rb") as f:
                return pickle.load(f)
        return []   # list of (encoded_board, move, outcome) tuples

    def _save_data(self):
        with open(DATA_FILE, "wb") as f:
            pickle.dump(self.data, f)

    def _load_model(self):
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE, "rb") as f:
                return pickle.load(f)
        return None

    def _save_model(self):
        with open(MODEL_FILE, "wb") as f:
            pickle.dump(self.model, f)

    # ── Data Collection ───────────────────────────────────────────────────────

    def record_game(self, history, outcome):
        """
        Record a completed game into the dataset.

        history : list of (board_state, move_played) for AI moves only
        outcome : "win", "draw", or "loss"

        We weight wins positively, draws neutrally, losses negatively
        by duplicating winning records more often (simple oversampling).
        """
        weight = {"win": 3, "draw": 1, "loss": 1}
        copies = weight.get(outcome, 1)

        for board, move in history:
            encoded = encode_board(board)
            for _ in range(copies):
                self.data.append((encoded, move, outcome))

        self._save_data()
        self.games_since_retrain += 1

        log = [f"  [ML] Game recorded ({outcome}). Dataset size: {len(self.data)}"]

        # Retrain if we have enough data and it's time
        if (len(self.data) >= MIN_GAMES_TO_TRAIN * 3 and
                self.games_since_retrain >= RETRAIN_EVERY):
            train_log = self.train()
            log.extend(train_log)
            self.games_since_retrain = 0

        return log

    # ── Training ─────────────────────────────────────────────────────────────

    def train(self):
        """Train Random Forest on accumulated game data."""
        log = ["  [ML] Training Random Forest..."]

        X = np.array([d[0] for d in self.data])   # board encodings
        y = np.array([d[1] for d in self.data])   # moves played

        if len(set(y)) < 2:
            log.append("  [ML] Not enough move variety yet — skipping train")
            return log

        # Split for evaluation
        if len(X) > 20:
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2,
                                                        random_state=42)
        else:
            X_tr, y_tr = X, y
            X_te, y_te = X, y

        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=9,
            random_state=42
        )
        self.model.fit(X_tr, y_tr)
        acc = self.model.score(X_te, y_te)
        self._save_model()

        log.append(f"  [ML] Trained on {len(X_tr)} samples")
        log.append(f"  [ML] Validation accuracy: {acc:.1%}")
        log.append(f"  [ML] Model saved to {MODEL_FILE}")
        return log

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict_move(self, board):
        """
        Ask the ML model for its best move.

        Returns (move, confidence, log) if model is confident enough,
        or (None, 0.0, log) if model is untrained / not confident.
        """
        log = []

        if self.model is None:
            games_needed = max(0, MIN_GAMES_TO_TRAIN - len(self.data) // 3)
            log.append(f"  [ML] No model yet — need ~{games_needed} more games")
            return None, 0.0, log

        encoded = np.array([encode_board(board)])
        probs   = self.model.predict_proba(encoded)[0]
        classes = self.model.classes_

        # Only consider empty cells
        from bfs import get_empty_cells
        empty = get_empty_cells(board)

        # Filter to valid (empty) moves only
        valid = [(classes[i], probs[i]) for i in range(len(classes))
                 if classes[i] in empty]

        if not valid:
            log.append("  [ML] No valid ML move available")
            return None, 0.0, log

        best_move, confidence = max(valid, key=lambda x: x[1])

        log.append(f"  [ML] Predicting from {len(self.data)} training samples")
        log.append(f"  [ML] Best move: cell {best_move} (confidence {confidence:.1%})")

        if confidence >= MIN_CONFIDENCE:
            log.append(f"  [ML] Confidence sufficient → using ML move")
            return best_move, confidence, log
        else:
            log.append(f"  [ML] Confidence too low ({confidence:.1%} < {MIN_CONFIDENCE:.0%}) → BFS fallback")
            return None, confidence, log

    # ── Status ───────────────────────────────────────────────────────────────

    def status(self):
        games = len(self.data) // 3
        trained = self.model is not None
        return {
            "games_recorded": games,
            "model_trained":  trained,
            "dataset_size":   len(self.data),
            "min_to_train":   MIN_GAMES_TO_TRAIN,
        }
