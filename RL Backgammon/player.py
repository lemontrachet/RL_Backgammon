import numpy as np
from collections import defaultdict
from random import randint, choice
import itertools


class Player():
    def __init__(self, name, board):
        self.name = name
        self.board = board
        self.q = defaultdict(int)
        self.alpha = 0.1
        self.gamma = 0.2
        self.epsilon = 0.5

    # two random numbers; four if the dice match
    def roll_dice():
        dice = (randint(1, 6), randint(1, 6))
        if dice[0] == dice[1]: dice = tuple(itertools.repeat(dice[0], 4))
        return dice

    # generate all possible moves
    def gen_moves(self, board, die):
        new_states = []
        index = np.nonzero(board)

        if self.name == "x":
            bar = board[0]
        else:
            bar = board[25]
        for space in index[0]:
            b2 = np.copy(board)
            # # x's moves: x's pieces only
            if self.name == "x" and b2[space] > 0:
                move = space + die
                # pieces into end zone
                if move > 24:
                    b2[space] -= 1
                    if b2[0] == 0 or b2[0] < bar: new_states.append(b2)
                # taking other player's piece
                elif b2[move] == -1:
                    b2[move] = 1
                    b2[space] -= 1
                    b2[25] -= 1
                    # putting a y piece on the bar
                    if b2[0] == 0 or b2[0] < bar: new_states.append(b2)
                elif b2[move] >= 0:
                    b2[move] += 1
                    b2[space] -= 1
                    if b2[0] == 0 or b2[0] < bar: new_states.append(b2)

            # y's moves
            elif self.name == "y" and b2[space] < 0:
                move = space - die
                # pieces in end zone
                if move <= 0:
                    b2[space] += 1
                    if b2[25] == 0 or b2[25] > bar: new_states.append(b2)
                # taking other player's piece
                elif b2[move] == 1:
                    b2[move] = -1
                    b2[space] += 1
                    b2[0] += 1  # x piece onto bar
                    if b2[25] == 0 or b2[25] > bar: new_states.append(b2)
                elif b2[move] <= 0:
                    b2[move] -= 1
                    b2[space] += 1
                    if b2[25] == 0 or b2[25] > bar: new_states.append(b2)
        return np.array(new_states)

    def consult_q_table(self, state_action):
        return self.q.get(tuple(state_action), 0)

    def q_learner(self, moves):
        # restrict feature set of moves
        moves_r = [Player.get_current_state(m) for m in moves]
        # get scores
        best_actions = [x for x in moves_r if self.consult_q_table(x) ==
                        max([self.consult_q_table(m) for m in moves_r])]

        # if more than one best action, pick randomly
        try:
            action = choice(best_actions)
        except IndexError:
            action = []

        # exploration
        if np.random.random() > self.epsilon and action != []:
            action = choice(moves)

        return tuple(action)

    def get_num_pieces(self, board):
        if self.name == "x":
            f = lambda x: x > 0
        else:
            f = lambda x: x < 0
        return sum([x for x in board if f(x)])

    def check_remaining(self, first_die_moves):
        for m in first_die_moves:
            if self.get_num_pieces(m) == 0:
                return m

    def take_turn(self, board):
        print(self.name, "'s move")
        dice = Player.roll_dice()
        print(self.name, "rolled", dice)
        first_die_moves = self.gen_moves(board.board, dice[0])
        fm = self.check_remaining(first_die_moves)
        if fm != None: return tuple(fm)  # convert from np array
        second_die_moves = []
        for m in first_die_moves:
            second_die_moves.extend(self.gen_moves(m, dice[1]))
        secdm = [x for x in np.ravel(second_die_moves)]
        l = int(len(secdm) / 26)
        all_moves = np.reshape(np.array(secdm), ((l, 26)))

        # deal with double rolls
        if len(dice) > 2:
            third_d = []
            for m in all_moves:
                third_d.extend(self.gen_moves(m, dice[2]))
            third_d = [x for x in np.ravel(third_d)]
            l = int(len(third_d) / 26)
            third_d = np.reshape(np.array(third_d), ((l, 26)))
            fourth_d = []
            for m in third_d:
                fourth_d.extend(self.gen_moves(m, dice[3]))
            fourth_d = [x for x in np.ravel(fourth_d)]
            l = int(len(fourth_d) / 26)
            all_moves = np.reshape(np.array(fourth_d), ((l, 26)))

        print("found", len(all_moves), "possible moves")
        # select move using q-table and return
        return self.q_learner(all_moves)

    @staticmethod
    def check_threats(player, space, board):
        # check whether opponent is threatening to take a lone piece
        if player == "x":
            for i in range(board.index(space), 26):
                if board[i] < 0:
                    print("threat at", i)
                    return True
        if player == "y":
            for i in range(0, board.index(space)):
                if board[i] > 0:
                    print("threat at", i)
                    return True

    def calculate_reward(self, board):
        reward = 0
        print(board)
        if len(board) == 0: return reward
        if self.name == "x":
            if board[0] > 0: reward -= 25  # negative reward for own pieces on the bar
            if board[25] < 0: reward += 25  # positive reward for opponent pieces on bar
            reward += 5 * (15 - len([i for i in board if i > 0]))  # 5 points for each piece in end zone
            reward -= 5 * (15 - len([i for i in board if i < 0]))  # -5 for each opponent piece in end zone
            for space in board[1:25]:

                if space == 1 and self.check_threats("x", space, board): reward -= 25  # negative reward for singles
            return reward
        else:
            if board[25] < 0: reward -= 25  # negative reward for own pieces on the bar
            if board[0] > 0: reward += 25  # positive reward for opponent pieces on bar
            reward += 5 * (15 - len([i for i in board if i < 0]))  # 5 points for each piece in end zone
            reward -= 5 * (15 - len([i for i in board if i > 0]))  # -5 for each opponent piece in end zone
            for space in board[1:25]:
                if space == 1 and self.check_threats("y", space, board): reward -= 25  # negative reward for singles
            return reward


    def update_q_table(self, board, reward):
        # generate random moves and evaluate
        av_max_score = 0
        possible_next_dice = [Player.roll_dice() for x in range(5)]
        for next_dice in possible_next_dice:
            first_die_moves = self.gen_moves(board.board, next_dice[0])
            fm = self.check_remaining(first_die_moves)
            if fm != None:
                av_max_score += 500
            else:
                second_die_moves = []
                for m in first_die_moves:
                    second_die_moves.extend(self.gen_moves(m, next_dice[1]))
                secdm = [x for x in np.ravel(second_die_moves)]
                l = int(len(secdm) / 26)
                secdm = np.reshape(np.array(secdm), ((l, 26)))
                # restrict the features
                all_moves = [Player.get_current_state(m) for m in secdm]

                # deal with double rolls
                if len(next_dice) > 2:
                    third_d = []
                    for m in all_moves:
                        third_d.extend(self.gen_moves(m, next_dice[2]))
                    third_d = [x for x in np.ravel(third_d)]
                    l = int(len(third_d) / 26)
                    third_d = np.reshape(np.array(third_d), ((l, 26)))
                    fourth_d = []
                    for m in third_d:
                        fourth_d.extend(self.gen_moves(m, next_dice[3]))
                    fourth_d = [x for x in np.ravel(fourth_d)]
                    l = int(len(fourth_d) / 26)
                    all_moves = np.reshape(np.array(fourth_d), ((l, 26)))

                # refer to q-table for scores
                try:
                    av_max_score += max([self.consult_q_table(x) for
                                         x in all_moves])
                except Exception:
                    av_max_score = 0
        av_max_score /= 5

        # the max score for the next state in the Bellman equation is
        # the average of the max scores for each random next state
        max_new_q = av_max_score

        # convert board to state
        current_state = Player.get_current_state(board.board)

        # current value
        current_value = self.consult_q_table(current_state)

        # Bellman equation
        self.q[current_state] = current_value + self.alpha * (reward +
                                                              self.gamma * max_new_q - current_value)

    @staticmethod
    def get_current_state(board):
        return tuple(min(x, 2) for x in board)

    def apply_win_bonus(self, winning_moves, loser, losing_moves):
        # note winner and loser are player instances
        for wm in winning_moves:
            current_value = self.consult_q_table(tuple(wm))
            self.q[tuple(wm)] = current_value + self.alpha * 50
            # self.q[tuple(wm)] += 25
        for lm in losing_moves:
            current_value = loser.consult_q_table(tuple(lm))
            loser.q[tuple(lm)] = current_value + self.alpha * -50
            # loser.q[tuple(lm)] -= 25
