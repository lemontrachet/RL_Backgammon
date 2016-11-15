from board import Board
from player import Player
import numpy
import time
import pickle
from time import strftime

class Game_Manager():
    
    def __init__(self):
        self.board = Board()
        try:
            with open('player1.pkl', 'rb') as f1:
                self.board.x = pickle.load(f1)
                print("loaded x")
            f1.close()
        except Exception: pass
        try:
            with open('player2.pkl', 'rb') as f2:
                self.board.y = pickle.load(f2)
                print("loaded y")
            f2.close()
        except Exception: pass
        self.x = self.board.x
        self.y = self.board.y
        
    def play_game(self):
        turn = 1
        x_moves = []
        y_moves = []
        while True:
            #time.sleep(3)
            if turn % 2 != 0:
                # x choose move
                new_state = self.x.take_turn(self.board)
                x_moves.append(new_state)
                
                # update board
                self.board.update_board(new_state)
                
                # get reward
                reward = self.x.calculate_reward(new_state)
                print("reward:", reward)
                
                # check if won
                if len([i for i in self.board.board if i > 0]) == 0:
                    print("x wins")
                    # update q-tables
                    self.x.apply_win_bonus(x_moves, self.y, y_moves)
                    with open('player1.pkl', 'wb') as f1:
                        pickle.dump(self.x, f1)
                    f1.close()
                    with open('player2.pkl', 'wb') as f2:
                        pickle.dump(self.y, f2)
                    f2.close()
                    with open('results.csv', 'a') as r:
                        r.write("{0},{1},{2},{3}\n".format(strftime(
                                                  "%Y-%m-%d %H:%M:%S"),
                                   "x", sum(self.x.q.values()), "v1.0"))
                    r.close()
                    break
                
                else:
                    # update q table
                    self.x.update_q_table(self.board, reward)
                
            else:
                # y choose move
                new_state = self.y.take_turn(self.board)
                y_moves.append(new_state)
                
                # update board
                self.board.update_board(new_state)
                
                # get reward
                reward = self.y.calculate_reward(new_state)
                print("reward", reward)
                
                if len([i for i in self.board.board if i < 0]) == 0:
                    print("y wins")
                    # update q-table
                    self.y.apply_win_bonus(y_moves, self.x, x_moves)
                    with open('player1.pkl', 'wb') as f1:
                        pickle.dump(self.x, f1)
                    f1.close()
                    with open('player2.pkl', 'wb') as f2:
                        pickle.dump(self.y, f2)
                    f2.close()
                    with open('results.csv', 'a') as r:
                        r.write("{0},{1},{2},{3}\n".format(strftime(
                                     "%Y-%m-%d %H:%M:%S"), "y",
                                     sum(self.x.q.values()), "v1.1"))
                    r.close()
                    break
                else: # update q table
                    self.y.update_q_table(self.board, reward)

            turn += 1

while True:
    gm = Game_Manager()
    gm.play_game()
