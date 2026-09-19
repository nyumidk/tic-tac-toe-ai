"""
bfs.py — BFS Search + Knowledge-Base Inference for Tic-Tac-Toe AI
-------------------------------------------------------------------
CIA-1 Part 5 | Course: ITPCC510 / AI
Fr. C. Rodrigues Institute of Technology, Vashi
Student: Neha Yadav | Roll No: 5024143

Reference Paper:
"Intelligent Agent Systems: Evolving Decision-Making Models and Applications"
Boujia & Sabbane, MSCC 2024 | DOI: 10.1109/MSCC62288.2024.10697074
"""

from collections import deque

AI    = "O"
HUMAN = "X"

WIN_CONDITIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
    [0, 4, 8], [2, 4, 6]              # diagonals
]


def check_winner(board, player):
    return any(all(board[i] == player for i in combo) for combo in WIN_CONDITIONS)


def is_draw(board):
    return all(cell != "" for cell in board)


def get_empty_cells(board):
    return [i for i, cell in enumerate(board) if cell == ""]


def get_winning_move(board, player):
    """KB inference: return immediate winning cell if it exists."""
    for i in get_empty_cells(board):
        test = board[:]
        test[i] = player
        if check_winner(test, player):
            return i
    return None


def bfs_best_move(board):
    """
    BFS-based move selection.
    Returns (best_move_index, bfs_log)
    """
    log = []
    log.append("=" * 52)
    log.append("  BFS AI THINKING...")
    log.append("=" * 52)

    # KB Step 1: Win immediately
    win = get_winning_move(board, AI)
    if win is not None:
        log.append(f"  [KB] Immediate WIN → cell {win}")
        log.append("=" * 52)
        return win, log

    # KB Step 2: Block opponent
    block = get_winning_move(board, HUMAN)
    if block is not None:
        log.append(f"  [KB] BLOCK opponent → cell {block}")
        log.append("=" * 52)
        return block, log

    # BFS
    queue = deque()
    empty = get_empty_cells(board)
    for move in empty:
        nb = board[:]
        nb[move] = AI
        queue.append((nb, move, 1))

    log.append(f"  Exploring {len(empty)} moves via BFS...")

    explored = 0
    best_move = empty[0]
    found = False
    depth_counts = {}

    while queue:
        state, first_move, depth = queue.popleft()
        explored += 1
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

        if check_winner(state, AI):
            if not found:
                best_move = first_move
                found = True
                log.append(f"  [BFS] Win at depth {depth} via cell {first_move}")
                log.append(f"  [BFS] States explored: {explored}")
                break

        if is_draw(state) or check_winner(state, HUMAN):
            continue

        for opp in get_empty_cells(state):
            os = state[:]
            os[opp] = HUMAN
            if check_winner(os, HUMAN) or is_draw(os):
                continue
            for ai_m in get_empty_cells(os):
                ns = os[:]
                ns[ai_m] = AI
                queue.append((ns, first_move, depth + 2))

    if not found:
        preference = [4, 0, 2, 6, 8, 1, 3, 5, 7]
        for cell in preference:
            if cell in get_empty_cells(board):
                best_move = cell
                break
        log.append(f"  [BFS] No forced win — strategic cell {best_move}")

    log.append(f"  Total states explored: {explored}")
    for d, c in sorted(depth_counts.items()):
        log.append(f"    Depth {d}: {c} states")
    log.append(f"  CHOSEN MOVE → cell {best_move}")
    log.append("=" * 52)
    return best_move, log
