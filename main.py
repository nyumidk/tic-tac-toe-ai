"""
main.py — Tic-Tac-Toe: Human vs BFS AI (pygame GUI)
------------------------------------------------------
CIA-1 Part 5 | Course: ITPCC510 / AI
Fr. C. Rodrigues Institute of Technology, Vashi
Student: Neha Yadav | Roll No: 5024143

Reference Paper:
"Intelligent Agent Systems: Evolving Decision-Making Models and Applications"
Boujia & Sabbane, MSCC 2024 | DOI: 10.1109/MSCC62288.2024.10697074

How to run:
    pip install pygame
    python main.py
"""

import pygame
import sys
import time
from bfs import bfs_best_move, check_winner, is_draw, AI, HUMAN

# ── Window & Layout ──────────────────────────────────────────────────────────
WIN_W, WIN_H   = 900, 560
BOARD_SIZE     = 480
CELL           = BOARD_SIZE // 3
BOARD_X        = 40          # board left offset
BOARD_Y        = 60          # board top offset
LOG_X          = BOARD_X + BOARD_SIZE + 40
LOG_Y          = 60
LOG_W          = WIN_W - LOG_X - 20
LOG_H          = WIN_H - LOG_Y - 20

# ── Colours ──────────────────────────────────────────────────────────────────
BG          = (15,  20,  40)
GRID        = (80, 120, 180)
X_COL       = (70, 190, 230)
O_COL       = (240, 100, 100)
WIN_LINE    = (255, 210,  60)
TEXT_WHITE  = (230, 230, 230)
TEXT_DIM    = (130, 150, 180)
LOG_BG      = (22,  30,  55)
LOG_BORDER  = (60,  90, 140)
STATUS_BG   = (30,  40,  70)
BTN_COL     = (50,  90, 160)
BTN_HOV     = (70, 120, 200)
BTN_TEXT    = (255, 255, 255)
HIGHLIGHT   = (50, 200, 120)

pygame.init()
screen  = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Tic-Tac-Toe — BFS AI  |  CIA-1 Part 5")

font_big    = pygame.font.SysFont("consolas", 36, bold=True)
font_med    = pygame.font.SysFont("consolas", 22, bold=True)
font_small  = pygame.font.SysFont("consolas", 14)
font_tiny   = pygame.font.SysFont("consolas", 12)


# ── Game State ───────────────────────────────────────────────────────────────
def new_game():
    return {
        "board":        [""] * 9,
        "turn":         HUMAN,
        "over":         False,
        "winner":       None,
        "win_combo":    None,
        "log":          ["  BFS AI ready.", "  Your turn — click a cell."],
        "scores":       {"X": 0, "O": 0, "Draw": 0},
        "ai_thinking":  False,
        "last_move":    None,
    }

state = new_game()
state["scores"] = {"X": 0, "O": 0, "Draw": 0}   # persist scores across games


# ── Drawing helpers ──────────────────────────────────────────────────────────

def cell_rect(idx):
    row, col = divmod(idx, 3)
    return pygame.Rect(
        BOARD_X + col * CELL,
        BOARD_Y + row * CELL,
        CELL, CELL
    )


def draw_board():
    # Background panel
    pygame.draw.rect(screen, STATUS_BG,
                     pygame.Rect(BOARD_X - 10, BOARD_Y - 10,
                                 BOARD_SIZE + 20, BOARD_SIZE + 20), border_radius=12)

    # Highlight last AI move
    if state["last_move"] is not None and not state["over"]:
        r = cell_rect(state["last_move"])
        pygame.draw.rect(screen, (40, 60, 100), r.inflate(-4, -4), border_radius=8)

    # Grid lines
    for i in range(1, 3):
        pygame.draw.line(screen, GRID,
                         (BOARD_X, BOARD_Y + i * CELL),
                         (BOARD_X + BOARD_SIZE, BOARD_Y + i * CELL), 3)
        pygame.draw.line(screen, GRID,
                         (BOARD_X + i * CELL, BOARD_Y),
                         (BOARD_X + i * CELL, BOARD_Y + BOARD_SIZE), 3)

    # Symbols
    for idx, val in enumerate(state["board"]):
        r = cell_rect(idx)
        cx, cy = r.centerx, r.centery
        if val == HUMAN:
            offset = 30
            pygame.draw.line(screen, X_COL,
                             (cx - offset, cy - offset),
                             (cx + offset, cy + offset), 6)
            pygame.draw.line(screen, X_COL,
                             (cx + offset, cy - offset),
                             (cx - offset, cy + offset), 6)
        elif val == AI:
            pygame.draw.circle(screen, O_COL, (cx, cy), 34, 6)

    # Winning line
    if state["win_combo"]:
        a, b = cell_rect(state["win_combo"][0]), cell_rect(state["win_combo"][2])
        pygame.draw.line(screen, WIN_LINE,
                         a.center, b.center, 8)

    # Cell index hints (small, for understanding)
    for idx in range(9):
        r = cell_rect(idx)
        if state["board"][idx] == "":
            hint = font_tiny.render(str(idx), True, (50, 70, 100))
            screen.blit(hint, (r.x + 6, r.y + 6))


def draw_status():
    if state["over"]:
        if state["winner"] == HUMAN:
            msg, col = "  You won! 🎉", X_COL
        elif state["winner"] == AI:
            msg, col = "  AI wins! 🤖", O_COL
        else:
            msg, col = "  It's a draw!", TEXT_WHITE
    else:
        if state["turn"] == HUMAN:
            msg, col = "  Your turn  (X)", X_COL
        else:
            msg, col = "  AI thinking...", O_COL

    pygame.draw.rect(screen, STATUS_BG,
                     pygame.Rect(BOARD_X - 10, BOARD_Y + BOARD_SIZE + 10,
                                 BOARD_SIZE + 20, 36), border_radius=8)
    s = font_med.render(msg, True, col)
    screen.blit(s, (BOARD_X, BOARD_Y + BOARD_SIZE + 16))


def draw_scores():
    y = BOARD_Y + BOARD_SIZE + 60
    labels = [("You (X)", state["scores"]["X"], X_COL),
              ("AI  (O)", state["scores"]["O"], O_COL),
              ("Draws",   state["scores"]["Draw"], TEXT_DIM)]
    for label, val, col in labels:
        txt = font_small.render(f"  {label}: {val}", True, col)
        screen.blit(txt, (BOARD_X, y))
        y += 24


def draw_log():
    pygame.draw.rect(screen, LOG_BG,
                     pygame.Rect(LOG_X - 8, LOG_Y - 8, LOG_W + 16, LOG_H + 16),
                     border_radius=10)
    pygame.draw.rect(screen, LOG_BORDER,
                     pygame.Rect(LOG_X - 8, LOG_Y - 8, LOG_W + 16, LOG_H + 16),
                     2, border_radius=10)

    title = font_small.render("  BFS SEARCH LOG", True, HIGHLIGHT)
    screen.blit(title, (LOG_X, LOG_Y - 4))

    pygame.draw.line(screen, LOG_BORDER,
                     (LOG_X, LOG_Y + 16), (LOG_X + LOG_W, LOG_Y + 16), 1)

    # Show last N lines that fit
    line_h = 16
    max_lines = (LOG_H - 24) // line_h
    lines = state["log"][-max_lines:]
    for i, line in enumerate(lines):
        col = HIGHLIGHT if line.startswith("  CHOSEN") or "WIN" in line else TEXT_DIM
        if line.startswith("="):
            col = LOG_BORDER
        surf = font_tiny.render(line, True, col)
        screen.blit(surf, (LOG_X, LOG_Y + 22 + i * line_h))


def draw_restart_btn():
    mx, my = pygame.mouse.get_pos()
    btn = pygame.Rect(BOARD_X, WIN_H - 44, 140, 34)
    col = BTN_HOV if btn.collidepoint(mx, my) else BTN_COL
    pygame.draw.rect(screen, col, btn, border_radius=8)
    txt = font_small.render("  New Game", True, BTN_TEXT)
    screen.blit(txt, (btn.x + 10, btn.y + 8))
    return btn


def draw_header():
    title = font_med.render("Tic-Tac-Toe  —  BFS AI", True, TEXT_WHITE)
    screen.blit(title, (BOARD_X, 14))
    sub = font_tiny.render(
        "CIA-1 Part 5  |  Neha Yadav  |  Roll: 5024143  |  ITPCC510/AI",
        True, TEXT_DIM)
    screen.blit(sub, (BOARD_X, 36))


# ── AI Move ──────────────────────────────────────────────────────────────────

def ai_move():
    move, bfs_log = bfs_best_move(state["board"])
    state["log"] = bfs_log
    state["board"][move] = AI
    state["last_move"] = move

    # Print to terminal as well
    print("\n".join(bfs_log))

    if check_winner(state["board"], AI):
        state["over"]    = True
        state["winner"]  = AI
        state["scores"]["O"] += 1
        # Find winning combo for line drawing
        from bfs import WIN_CONDITIONS
        for combo in WIN_CONDITIONS:
            if all(state["board"][i] == AI for i in combo):
                state["win_combo"] = combo
                break
        state["log"].append("  AI wins this round!")
    elif is_draw(state["board"]):
        state["over"]   = True
        state["winner"] = None
        state["scores"]["Draw"] += 1
        state["log"].append("  It's a draw!")
    else:
        state["turn"] = HUMAN
        state["log"].append("  Your turn — click a cell.")


# ── Main Loop ────────────────────────────────────────────────────────────────

clock = pygame.time.Clock()
ai_move_pending = False
ai_move_timer   = 0

while True:
    screen.fill(BG)
    draw_header()
    draw_board()
    draw_status()
    draw_scores()
    draw_log()
    btn = draw_restart_btn()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Restart button
            if btn.collidepoint(mx, my):
                scores = state["scores"]
                state  = new_game()
                state["scores"] = scores
                ai_move_pending = False
                print("\n--- New Game Started ---")
                continue

            # Human clicks a cell
            if not state["over"] and state["turn"] == HUMAN:
                for idx in range(9):
                    r = cell_rect(idx)
                    if r.collidepoint(mx, my) and state["board"][idx] == "":
                        state["board"][idx] = HUMAN
                        state["last_move"]  = None
                        print(f"\n[Human] Played cell {idx}")

                        if check_winner(state["board"], HUMAN):
                            state["over"]   = True
                            state["winner"] = HUMAN
                            state["scores"]["X"] += 1
                            from bfs import WIN_CONDITIONS
                            for combo in WIN_CONDITIONS:
                                if all(state["board"][i] == HUMAN for i in combo):
                                    state["win_combo"] = combo
                                    break
                            state["log"] = ["  You won! Great game."]
                        elif is_draw(state["board"]):
                            state["over"]   = True
                            state["winner"] = None
                            state["scores"]["Draw"] += 1
                            state["log"] = ["  It's a draw!"]
                        else:
                            state["turn"]    = AI
                            state["log"]     = ["  AI is thinking..."]
                            ai_move_pending  = True
                            ai_move_timer    = pygame.time.get_ticks()
                        break

    # Small delay so player can see their move before AI responds
    if ai_move_pending and not state["over"]:
        if pygame.time.get_ticks() - ai_move_timer > 400:
            ai_move_pending = False
            ai_move()

    pygame.display.flip()
    clock.tick(60)
