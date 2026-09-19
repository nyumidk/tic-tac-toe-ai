"""
bfs.py — BFS-based AI for Tic-Tac-Toe
---------------------------------------
The AI explores all possible game states level by level (move by move)
using Breadth-First Search to find the shallowest winning move.

CIA-1 Part 5 | Course: ITPCC510 / AI | Fr. C. Rodrigues Institute of Technology, Vashi
Reference: "Intelligent Agent Systems: Evolving Decision-Making Models and Applications"
           Boujia & Sabbane, MSCC 2024 | DOI: 10.1109/MSCC62288.2024.10697074
"""

from collections import deque
import copy


# ── Constants ────────────────────────────────────────────────────────────────
AI     = "O"   # AI player symbol
HUMAN  = "X"   # Human player symbol

# All 8 winning combinations (row, column, diagonal indices on a flat 9-list)
WIN_CONDITIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],   # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],   # columns
    [0, 4, 8], [2, 4, 6]               # diagonals
]


# ── Helper functions ─────────────────────────────────────────────────────────

def check_winner(board, player):
    """Return True if the given player has won on this board."""
    return any(all(board[i] == player for i in combo) for combo in WIN_CONDITIONS)


def is_draw(board):
    """Return True if the board is full and no one has won."""
    return all(cell != "" for cell in board)


def get_empty_cells(board):
    """Return list of indices of empty cells."""
    return [i for i, cell in enumerate(board) if cell == ""]


def get_winning_move(board, player):
    """
    Knowledge-base style immediate check:
    If the player can win in one move, return that cell index.
    This is applied BEFORE BFS runs (KB inference from Part 3).
    """
    for i in get_empty_cells(board):
        test = board[:]
        test[i] = player
        if check_winner(test, player):
            return i
    return None


# ── BFS Core ─────────────────────────────────────────────────────────────────

def bfs_best_move(board, ai_symbol=AI, human_symbol=HUMAN):
    """
    BFS-based move selection for the AI agent.

    Explores all possible future game states level by level (one move deep,
    then two moves deep, etc.) and returns the move that leads to the
    shallowest winning state for the AI.

    Returns: (best_move_index, bfs_log)
        best_move_index — the cell (0-8) the AI should play
        bfs_log         — list of strings describing BFS exploration (for demo)
    """
    bfs_log = []
    bfs_log.append("=" * 55)
    bfs_log.append("  BFS AI THINKING...")
    bfs_log.append("=" * 55)

    # ── Step 1: KB Inference — win immediately if possible ──────────────────
    win = get_winning_move(board, ai_symbol)
    if win is not None:
        bfs_log.append(f"  [KB] Immediate WIN detected → play cell {win}")
        bfs_log.append("=" * 55)
        return win, bfs_log

    # ── Step 2: KB Inference — block opponent's immediate win ───────────────
    block = get_winning_move(board, human_symbol)
    if block is not None:
        bfs_log.append(f"  [KB] Opponent WIN threat → BLOCK cell {block}")
        bfs_log.append("=" * 55)
        return block, bfs_log

    # ── Step 3: BFS over remaining state space ──────────────────────────────
    # Each queue item: (board_state, first_move_made, depth)
    queue = deque()
    initial_moves = get_empty_cells(board)

    for move in initial_moves:
        new_board = board[:]
        new_board[move] = ai_symbol
        queue.append((new_board, move, 1))

    bfs_log.append(f"  Level 0 (current): {sum(1 for c in board if c == '')} empty cells")
    bfs_log.append(f"  Exploring {len(initial_moves)} immediate moves via BFS...")

    states_explored = 0
    best_move = initial_moves[0]   # fallback
    best_move_found = False

    current_depth = 1
    depth_counts = {}

    while queue:
        state, first_move, depth = queue.popleft()
        states_explored += 1

        # Track how many states per depth level
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

        # Check if AI wins from this state
        if check_winner(state, ai_symbol):
            if not best_move_found:
                best_move = first_move
                best_move_found = True
                bfs_log.append(f"  [BFS] WIN path found at depth {depth} via cell {first_move}")
                bfs_log.append(f"  [BFS] States explored so far: {states_explored}")
                # Don't break — BFS guarantees shallowest; 
                # once we find at this depth, no shallower path exists
                break

        if is_draw(state) or check_winner(state, human_symbol):
            continue   # terminal state, don't expand

        # Expand: opponent moves next, then AI again
        for opp_move in get_empty_cells(state):
            opp_state = state[:]
            opp_state[opp_move] = human_symbol

            if check_winner(opp_state, human_symbol) or is_draw(opp_state):
                continue   # opponent wins this branch — prune

            for ai_move in get_empty_cells(opp_state):
                next_state = opp_state[:]
                next_state[ai_move] = ai_symbol
                queue.append((next_state, first_move, depth + 2))

    # If no winning path found, prefer centre → corners → any
    if not best_move_found:
        empty = get_empty_cells(board)
        preference = [4, 0, 2, 6, 8, 1, 3, 5, 7]   # centre, corners, edges
        for cell in preference:
            if cell in empty:
                best_move = cell
                break
        bfs_log.append(f"  [BFS] No forced win found — strategic fallback → cell {best_move}")

    bfs_log.append(f"  Total states explored: {states_explored}")
    for d, count in sorted(depth_counts.items()):
        bfs_log.append(f"    Depth {d}: {count} states")
    bfs_log.append(f"  CHOSEN MOVE: cell {best_move}")
    bfs_log.append("=" * 55)

    return best_move, bfs_log
