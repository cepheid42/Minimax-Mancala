import copy
import random
from operator import itemgetter
import sys

INFINITY = 1.0e06
ab_nodes = 0
mm_nodes = 0


def game_over(board):
    if sum(board[0:6]) == 0 or sum(board[7:13]) == 0:
        return True
    else:
        return False


def valid_move(board, action, turn):
    start = 0 if turn else 7
    end = 6 if turn else 13
    if start <= action < end and board[action] > 0:
        return True
    else:
        return False


def make_move(board, action, turn):
    start = 0 if turn else 7
    end = 6 if turn else 13
    num_stones = board[action]
    cur_pit = action + 1
    # Set initial pit to zero
    board[action] = 0
    for _ in range(num_stones):
        # If current pit is opponents store, place next stone in cur_pit +1
        # then skip two to catch up
        if (cur_pit % 14) == (end + 7) % 14:
            board[(cur_pit + 1) % 14] += 1
            cur_pit += 2
        else:
            board[cur_pit % 14] += 1
            cur_pit += 1
    # Captures opponents stones if landing on empty pit
    if board[(cur_pit - 1) % 14] == 1 and start <= (cur_pit - 1) % 14 < end:
        opposite = steal_stones((cur_pit - 1) % 14)
        if board[opposite] != 0:
            board[end] += board[opposite] + 1
            board[opposite] = 0
            board[(cur_pit - 1) % 14] = 0
    # Changes turn unless landing on own store
    new_turn = not turn if (cur_pit - 1) % 14 != end else turn

    return board, new_turn


def steal_stones(pit):
    pairs = [(0, 12), (1, 11), (2, 10), (3, 9), (4, 8), (5, 7)]
    for pair in pairs:
        if pit in pair:
            return pair[1] if pit == pair[0] else pair[0]


def result(board, action, turn):
    new_board = copy.deepcopy(board)
    return make_move(new_board, action, turn)


def move_list(board, turn):
    start = 0 if turn else 7
    end = 6 if turn else 13
    moves = []
    for pit in range(start, end):
        if board[pit] > 0:
            moves.append(pit)
    return moves


def utility(state):
    return state[6] - state[13]


def minimax(board, maximizing_player, turn, depth):
    global mm_nodes
    if depth == 0 or game_over(board):
        return utility(board)
    if maximizing_player:
        value = -INFINITY
        actions = move_list(board, turn)
        for a in actions:
            new_board, new_turn = result(board, a, turn)
            mm_nodes += 1
            # If not repeat turn, changes max player
            maximizing_player = False if new_turn != turn else True
            value = max(value, minimax(new_board, maximizing_player, new_turn, depth - 1))
        return value
    else:
        value = INFINITY
        actions = move_list(board, turn)
        for a in actions:
            new_board, new_turn = result(board, a, turn)
            mm_nodes += 1
            # If not repeat turn, changes max player
            maximizing_player = True if new_turn != turn else False
            value = min(value, minimax(new_board, maximizing_player, new_turn, depth - 1))
        return value


def alphabeta(board, maximizing_player, turn, depth, alpha, beta):
    global ab_nodes
    if depth == 0 or game_over(board):
        return utility(board)
    if maximizing_player:
        v = -INFINITY
        for a in move_list(board, turn):
            new_s, new_turn = result(board, a, turn)
            ab_nodes += 1
            # If not repeat turn, changes max player
            maximizing_player = False if new_turn != turn else True
            v = max(v, alphabeta(new_s, maximizing_player, new_turn, depth - 1, alpha, beta))
            alpha = max(alpha, v)
            if alpha >= beta:
                break
    else:
        v = INFINITY
        for a in move_list(board, turn):
            new_s, new_turn = result(board, a, turn)
            ab_nodes += 1
            # If not a repeat turn, changes max player
            maximizing_player = True if new_turn != turn else False
            v = min(v, alphabeta(new_s, maximizing_player, new_turn, depth - 1, alpha, beta))
            beta = min(beta, v)
            if alpha >= beta:
                break
    return v


def pb(board):
    reverse = board[::-1]
    num1 = '  S    6    5    4    3    2    1\n'
    top = "    -------------------------------\n"
    row1 = " {:02} | {:02} | {:02} | {:02} | {:02} | {:02} | {:02} |\n".format(*reverse[:7])
    mid = "---------------------------------------\n"
    row2 = "    | {:02} | {:02} | {:02} | {:02} | {:02} | {:02} | {:02} \n".format(*board[:7])
    bot = "    -------------------------------     \n"
    num2 = '      1    2    3    4    5    6    S\n'
    return num1 + top + row1 + mid + row2 + bot + num2


def who_won(board):
    score = utility(board)
    if score > 0:
        print('Player 1 wins!')
        return 1
    elif score == 0:
        print('Draw!')
        return 0
    else:
        print('Player 2 wins!')
        return -1


def run_turn(board, player, turn):
    if player == 'human':
        p_move = int(input(f"Player {player} select pit: ", file=sys.stderr)) - 1
        if not turn:
            p_move = p_move + 7
        while not valid_move(board, p_move, turn):
            p_move = int(input('Invalid move, please try again: ', file=sys.stderr)) - 1
            if not turn:
                p_move = p_move + 7
    elif player == 'alphabeta':
        moves = []
        for a in move_list(board, turn):
            moves.append((a, alphabeta(board, False, turn, 12, -INFINITY, INFINITY)))
        p_move = max(moves, key=itemgetter(1))[0]
    elif player == 'minimax':
        moves = []
        for a in move_list(board, turn):
            moves.append((a, minimax(board, False, turn, 12)))
        p_move = max(moves, key=itemgetter(1))[0]
    else:  # Random
        pit_start = 0 if turn else 7
        pit_end = 6 if turn else 13
        p_move = random.choice(range(pit_start, pit_end))
        while not valid_move(board, p_move, turn):
            p_move = random.choice(range(pit_start, pit_end))
    if turn:
        print(f'{p_move + 1}')
    else:
        print(f' {p_move - 6}')
    print(pb(board), file=sys.stderr)
    return make_move(board, p_move, turn)


def driver(one, two, num_stones):
    board = [num_stones]*12
    board[6] = 0
    board[13] = 0
    turn = True
    while True:
        if turn:
            board, turn = run_turn(board, one, turn)
            if game_over(board):
                return who_won(board)
        else:
            board, turn = run_turn(board, two, turn)
            if game_over(board):
                return who_won(board)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('Not enough argument, please specify players.')
    allowed = ['human', 'random', 'minimax', 'alphabeta']
    if sys.argv[1].lower() not in allowed or sys.argv[2].lower() not in allowed:
        sys.exit('Invalid player type, please try again.')
    p1 = sys.argv[1].lower()
    p2 = sys.argv[2].lower()
    result = driver(p1, p2, num_stones=2)
