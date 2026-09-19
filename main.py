"""
main.py — Tic-Tac-Toe: Human vs Hybrid AI (pygame GUI)
--------------------------------------------------------
AI Decision Pipeline:
  1. KB Inference  — win/block immediately (Part 3)
  2. ML Agent      — Random Forest from past games (Part 4, scikit-learn)
  3. BFS Search    — exhaustive state-space search fallback (Part 2)

CIA-1 Part 5 | Course: ITPCC510 / AI
Fr. C. Rodrigues Institute of Technology, Vashi
Student: Neha Yadav | Roll No: 5024143

Run:
    pip install pygame scikit-learn
    python main.py
"""

import pygame
import sys
from bfs import bfs_best_move, check_winner, is_draw, get_empty_cells, WIN_CONDITIONS, AI, HUMAN
from ml_agent import MLAgent

# ── Layout ───────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 960, 600
BOARD_SIZE   = 460
CELL         = BOARD_SIZE // 3
BOARD_X      = 40
BOARD_Y      = 70
LOG_X        = BOARD_X + BOARD_SIZE + 40
LOG_W        = WIN_W - LOG_X - 20
LOG_Y        = 70
LOG_H        = WIN_H - LOG_Y - 20

# ── Colours ──────────────────────────────────────────────────────────────────
BG         = (12,  18,  38)
GRID       = (70, 110, 170)
X_COL      = (80, 200, 240)
O_COL      = (240,  90,  90)
WIN_LINE   = (255, 210,  50)
WHITE      = (230, 230, 230)
DIM        = (120, 140, 175)
LOG_BG     = (20,  28,  52)
LOG_BORDER = (55,  85, 135)
STATUS_BG  = (28,  38,  68)
BTN        = (45,  85, 155)
BTN_H      = (65, 115, 195)
GREEN      = (60, 200, 110)
ORANGE     = (240, 160,  50)
PURPLE     = (170,  80, 220)

pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Tic-Tac-Toe — Hybrid AI (BFS + ML)  |  CIA-1 Part 5")

F_BIG   = pygame.font.SysFont("consolas", 34, bold=True)
F_MED   = pygame.font.SysFont("consolas", 20, bold=True)
F_SM    = pygame.font.SysFont("consolas", 14)
F_TINY  = pygame.font.SysFont("consolas", 12)

ml = MLAgent()


# ── Game State ───────────────────────────────────────────────────────────────
def new_game(scores):
    return {
        "board":       [""] * 9,
        "turn":        HUMAN,
        "over":        False,
        "winner":      None,
        "win_combo":   None,
        "log":         ["  Hybrid AI ready (KB + ML + BFS)",
                        f"  ML status: {ml_status_line()}",
                        "  Your turn — click a cell."],
        "scores":      scores,
        "last_move":   None,
        "ai_history":  [],        # (board_snapshot, move) for ML recording
        "ai_method":   None,      # which method was used last: KB / ML / BFS
    }


def ml_status_line():
    s = ml.status()
    if s["model_trained"]:
        return f"Model trained ({s['games_recorded']} games)"
    else:
        needed = max(0, s["min_to_train"] - s["games_recorded"])
        return f"Learning... ({s['games_recorded']}/{s['min_to_train']} games, need {needed} more)"


scores = {"X": 0, "O": 0, "Draw": 0}
state  = new_game(scores)


# ── Helpers ──────────────────────────────────────────────────────────────────
def cell_rect(idx):
    r, c = divmod(idx, 3)
    return pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL, CELL)


def find_win_combo(board, player):
    for combo in WIN_CONDITIONS:
        if all(board[i] == player for i in combo):
            return combo
    return None


# ── Drawing ──────────────────────────────────────────────────────────────────
def draw_header():
    t = F_MED.render("Tic-Tac-Toe  —  Hybrid AI  (KB + ML + BFS)", True, WHITE)
    screen.blit(t, (BOARD_X, 14))
    s = F_TINY.render(
        "CIA-1 Part 5  |  Neha Yadav  5024143  |  ITPCC510/AI  |  Fr. C. Rodrigues Institute of Technology",
        True, DIM)
    screen.blit(s, (BOARD_X, 38))


def draw_board():
    pygame.draw.rect(screen, STATUS_BG,
                     pygame.Rect(BOARD_X-10, BOARD_Y-10, BOARD_SIZE+20, BOARD_SIZE+20),
                     border_radius=12)

    # Highlight last AI move
    if state["last_move"] is not None:
        r = cell_rect(state["last_move"])
        pygame.draw.rect(screen, (38, 58, 100), r.inflate(-6, -6), border_radius=8)

    # Grid
    for i in range(1, 3):
        pygame.draw.line(screen, GRID,
                         (BOARD_X, BOARD_Y + i*CELL),
                         (BOARD_X + BOARD_SIZE, BOARD_Y + i*CELL), 3)
        pygame.draw.line(screen, GRID,
                         (BOARD_X + i*CELL, BOARD_Y),
                         (BOARD_X + i*CELL, BOARD_Y + BOARD_SIZE), 3)

    # Symbols
    for idx, val in enumerate(state["board"]):
        r  = cell_rect(idx)
        cx, cy = r.centerx, r.centery
        if val == HUMAN:
            o = 28
            pygame.draw.line(screen, X_COL, (cx-o, cy-o), (cx+o, cy+o), 6)
            pygame.draw.line(screen, X_COL, (cx+o, cy-o), (cx-o, cy+o), 6)
        elif val == AI:
            pygame.draw.circle(screen, O_COL, (cx, cy), 32, 6)
        else:
            hint = F_TINY.render(str(idx), True, (45, 65, 95))
            screen.blit(hint, (r.x+6, r.y+6))

    # Win line
    if state["win_combo"]:
        a = cell_rect(state["win_combo"][0]).center
        b = cell_rect(state["win_combo"][2]).center
        pygame.draw.line(screen, WIN_LINE, a, b, 8)

    # Method badge
    method_col = {"KB": ORANGE, "ML": PURPLE, "BFS": GREEN, None: DIM}
    if state["ai_method"]:
        badge_txt = F_SM.render(f" Last move: {state['ai_method']} ", True, BG)
        badge_bg  = method_col[state["ai_method"]]
        bw = badge_txt.get_width() + 4
        pygame.draw.rect(screen, badge_bg,
                         pygame.Rect(BOARD_X, BOARD_Y + BOARD_SIZE + 56, bw, 22),
                         border_radius=5)
        screen.blit(badge_txt, (BOARD_X + 2, BOARD_Y + BOARD_SIZE + 58))


def draw_status():
    if state["over"]:
        if state["winner"] == HUMAN:
            msg, col = "  You won!", X_COL
        elif state["winner"] == AI:
            msg, col = "  AI wins!", O_COL
        else:
            msg, col = "  Draw!", WHITE
    else:
        if state["turn"] == HUMAN:
            msg, col = "  Your turn  (X)", X_COL
        else:
            msg, col = "  AI thinking...", O_COL

    pygame.draw.rect(screen, STATUS_BG,
                     pygame.Rect(BOARD_X-10, BOARD_Y+BOARD_SIZE+10, BOARD_SIZE+20, 38),
                     border_radius=8)
    screen.blit(F_MED.render(msg, True, col), (BOARD_X, BOARD_Y+BOARD_SIZE+18))


def draw_scores():
    y = BOARD_Y + BOARD_SIZE + 90
    for label, key, col in [("You (X)", "X", X_COL),
                              ("AI  (O)", "O", O_COL),
                              ("Draws  ", "Draw", DIM)]:
        screen.blit(F_SM.render(f"  {label}: {state['scores'][key]}", True, col), (BOARD_X, y))
        y += 22

    # ML status line
    y += 6
    ml_line = ml_status_line()
    col = GREEN if ml.status()["model_trained"] else ORANGE
    screen.blit(F_TINY.render(f"  ML: {ml_line}", True, col), (BOARD_X, y))


def draw_log():
    pygame.draw.rect(screen, LOG_BG,
                     pygame.Rect(LOG_X-8, LOG_Y-8, LOG_W+16, LOG_H+16),
                     border_radius=10)
    pygame.draw.rect(screen, LOG_BORDER,
                     pygame.Rect(LOG_X-8, LOG_Y-8, LOG_W+16, LOG_H+16),
                     2, border_radius=10)

    screen.blit(F_SM.render("  AI DECISION LOG", True, GREEN), (LOG_X, LOG_Y-4))
    pygame.draw.line(screen, LOG_BORDER, (LOG_X, LOG_Y+16), (LOG_X+LOG_W, LOG_Y+16), 1)

    line_h   = 16
    max_lines = (LOG_H - 26) // line_h
    lines    = state["log"][-max_lines:]

    for i, line in enumerate(lines):
        if "[KB]"  in line: col = ORANGE
        elif "[ML]" in line: col = PURPLE
        elif "[BFS]" in line: col = GREEN
        elif "CHOSEN" in line or "WIN" in line: col = WIN_LINE
        elif line.startswith("  ="):  col = LOG_BORDER
        else: col = DIM

        screen.blit(F_TINY.render(line, True, col), (LOG_X, LOG_Y+22+i*line_h))


def draw_buttons():
    mx, my = pygame.mouse.get_pos()
    buttons = {}

    # New Game
    r1 = pygame.Rect(BOARD_X, WIN_H-44, 130, 32)
    c1 = BTN_H if r1.collidepoint(mx, my) else BTN
    pygame.draw.rect(screen, c1, r1, border_radius=7)
    screen.blit(F_SM.render(" New Game", True, WHITE), (r1.x+8, r1.y+8))
    buttons["new"] = r1

    # Reset ML
    r2 = pygame.Rect(BOARD_X+145, WIN_H-44, 130, 32)
    c2 = BTN_H if r2.collidepoint(mx, my) else (80, 40, 40)
    pygame.draw.rect(screen, c2, r2, border_radius=7)
    screen.blit(F_SM.render(" Reset ML", True, WHITE), (r2.x+8, r2.y+8))
    buttons["reset_ml"] = r2

    return buttons


# ── AI Move ──────────────────────────────────────────────────────────────────
def ai_move():
    board = state["board"]
    log   = []
    log.append("=" * 48)
    log.append("  AI DECISION PIPELINE")
    log.append("=" * 48)

    move   = None
    method = None

    # ── Stage 1: KB Inference ────────────────────────────────────────────────
    log.append("  Stage 1: KB Inference")
    from bfs import get_winning_move
    win   = get_winning_move(board, AI)
    block = get_winning_move(board, HUMAN)

    if win is not None:
        move, method = win, "KB"
        log.append(f"  [KB] WIN detected → cell {win}")
    elif block is not None:
        move, method = block, "KB"
        log.append(f"  [KB] BLOCK detected → cell {block}")
    else:
        log.append("  [KB] No immediate win/block.")

    # ── Stage 2: ML Prediction ───────────────────────────────────────────────
    if move is None:
        log.append("  Stage 2: ML Prediction")
        ml_move, conf, ml_log = ml.predict_move(board)
        log.extend(ml_log)
        if ml_move is not None:
            move, method = ml_move, "ML"

    # ── Stage 3: BFS Fallback ────────────────────────────────────────────────
    if move is None:
        log.append("  Stage 3: BFS Search")
        bfs_move, bfs_log = bfs_best_move(board)
        log.extend(bfs_log)
        move, method = bfs_move, "BFS"

    log.append(f"  FINAL → cell {move} via [{method}]")
    log.append("=" * 48)

    # Record for ML (before placing)
    state["ai_history"].append((board[:], move))
    state["ai_method"] = method

    # Place move
    state["board"][move] = AI
    state["last_move"]   = move
    state["log"]         = log

    print("\n".join(log))

    # Check outcome
    if check_winner(state["board"], AI):
        state["over"]      = True
        state["winner"]    = AI
        state["win_combo"] = find_win_combo(state["board"], AI)
        state["scores"]["O"] += 1
        record_game_to_ml("win")
    elif is_draw(state["board"]):
        state["over"]   = True
        state["winner"] = None
        state["scores"]["Draw"] += 1
        record_game_to_ml("draw")
    else:
        state["turn"] = HUMAN
        state["log"].append("  Your turn — click a cell.")


def record_game_to_ml(outcome):
    if state["ai_history"]:
        ml_log = ml.record_game(state["ai_history"], outcome)
        state["log"].extend(ml_log)
        print("\n".join(ml_log))


# ── Main Loop ─────────────────────────────────────────────────────────────────
clock = pygame.time.Clock()
ai_pending = False
ai_timer   = 0

while True:
    screen.fill(BG)
    draw_header()
    draw_board()
    draw_status()
    draw_scores()
    draw_log()
    btns = draw_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if btns["new"].collidepoint(mx, my):
                state = new_game(state["scores"])
                ai_pending = False
                print("\n--- New Game ---")
                continue

            if btns["reset_ml"].collidepoint(mx, my):
                import os
                for f in ["game_data.pkl", "rf_model.pkl"]:
                    if os.path.exists(f): os.remove(f)
                ml.__init__()
                state["log"] = ["  ML data reset.", "  Starting fresh."]
                print("\n--- ML Reset ---")
                continue

            if not state["over"] and state["turn"] == HUMAN:
                for idx in range(9):
                    r = cell_rect(idx)
                    if r.collidepoint(mx, my) and state["board"][idx] == "":
                        state["board"][idx] = HUMAN
                        state["last_move"]  = None
                        print(f"\n[Human] Cell {idx}")

                        if check_winner(state["board"], HUMAN):
                            state["over"]      = True
                            state["winner"]    = HUMAN
                            state["win_combo"] = find_win_combo(state["board"], HUMAN)
                            state["scores"]["X"] += 1
                            state["log"] = ["  You won this round!",
                                            "  Recording for ML..."]
                            record_game_to_ml("loss")
                        elif is_draw(state["board"]):
                            state["over"]   = True
                            state["winner"] = None
                            state["scores"]["Draw"] += 1
                            state["log"] = ["  Draw! Recording for ML..."]
                            record_game_to_ml("draw")
                        else:
                            state["turn"] = AI
                            state["log"]  = ["  AI thinking..."]
                            ai_pending    = True
                            ai_timer      = pygame.time.get_ticks()
                        break

    if ai_pending and not state["over"]:
        if pygame.time.get_ticks() - ai_timer > 450:
            ai_pending = False
            ai_move()

    pygame.display.flip()
    clock.tick(60)
