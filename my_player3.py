#!/usr/bin/env python
# coding: utf-8

# In[1471]:


import collections
import sys
import itertools as it
from itertools import product
from copy import deepcopy
import numpy as np
import operator


# In[1522]:


f = open("./output.txt", "w")
old_board = []
new_board = []
with open("./input.txt", 'r') as f:
    lines = f.readlines()
    me = int(lines[0])
    old_board = [[int(i) for i in line.rstrip('\n')] for line in lines[1:6]]
    curr_board = [[int(i) for i in line.rstrip('\n')] for line in lines[6:11]]
liberty = np.array(np.ones([5,5]))
maximum = 99999
minimum = -99999


# In[1523]:





# In[1526]:


my_dead = []
for i in range(5):
    for j in range(5):
        if old_board[i][j] == me and curr_board[i][j] == 0:
            my_dead.append((i, j))


# In[1527]:


def calc_score(piece, board):
    score = 0
    for i in range(5):
        for j in range(5):
            if board[i][j] == piece:
                score += 1
    if piece == 1: return score
    else: return score+2.5


# In[1528]:


def compare(board1, board2):
    for i in range(5):
        for j in range(5):
            if board1[i][j] != board2[i][j]:
                return False
    return True


# In[1529]:


def find_next_pieces(i, j):
        next_pieces = []
        if i > 0: next_pieces.append((i-1, j))
        if i < 4: next_pieces.append((i+1, j))
        if j > 0: next_pieces.append((i, j-1))
        if j < 4: next_pieces.append((i, j+1))
        return next_pieces


# In[1530]:


def find_next_same_piece(i, j, board):
    next_pieces = find_next_pieces(i, j)
    allies = []
    for mp in next_pieces:
        if curr_board[mp[0]][mp[1]] == board[i][j]:
            allies.append(mp)
    #print("Allies", allies)
    return allies


# In[1531]:


def neighbor_check(i, j, board):
    board_search = [(i, j)]
    my_pieces = []        
    while board_search:
        piece = board_search.pop()
        my_pieces.append(piece)
        next_own_pieces = find_next_same_piece(piece[0], piece[1], board)
        for mypiece in next_own_pieces:
            if mypiece not in board_search and mypiece not in my_pieces:
                board_search.append(mypiece)
    return my_pieces


# In[1532]:


def check_liberty(i, j, board):
    same_piece = neighbor_check(i, j, board)
    for sp in same_piece:
        next_piece = find_next_pieces(sp[0], sp[1])
        for p in next_piece:
            if board[p[0]][p[1]] == 0:
                return True
    return False


# In[1533]:


def attacking_move(i, j, board):
    board[i][j] = me
    dead = []
    for a in range(5):
        for b in range(5):
            if board[a][b] == 3-me: 
                if not check_liberty(a, b, board):
                    dead.append((a,b))
    return dead 


# In[1534]:


def defensive_move(i, j, board):
    board[i][j] = 3-me
    my_deaths = []
    for a in range(5):
        for b in range(5):
            if board[a][b] == me:
                if not check_liberty(a, b, board):
                    my_deaths.append((a,b))
    return my_deaths


# In[1535]:


def KO_move(c, board):
    for i in c:
        board[i[0]][i[1]] = 0
    if my_dead and compare(old_board, board):
        return True


# In[1536]:


def suicide_move(i, j, board):
    board[i][j] = me
    for i in range(5):
        for j in range(5):
            if board[i][j] == me:
                if not check_liberty(i, j, board):
                    return True
    return False


# In[1537]:


def liberty_moves(board):
    libertylist = {}
    for i in range(5):
        for j in range(5):
            if board[i][j] == 0:
                c = 0
                np = find_next_pieces(i, j)
                for p in np:
                    if board[p[0]][p[1]] == 0:
                            c += 1
                libertylist[(i,j)] = c
    return libertylist


# In[1538]:


def calculate_liberty(board):     
    attacking_list = {}
    suicide_list = []
    invalid_moves = []
    defensive_list = {}
    for i in range(5):
        for j in range(5):
            if curr_board[i][j] == 0:
                test = deepcopy(curr_board)
                al = attacking_move(i, j, test)
                dl = defensive_move(i, j, test)
                if len(al) > 0:
                    attacking_list[(i, j)] = len(al)*10
                    attacking_list = dict( sorted(attacking_list.items(), key=operator.itemgetter(1),reverse=True))
                if suicide_move(i, j, test):
                    suicide_list.append((i,j))
                if KO_move(al, test):
                    invalid_moves.append((i, j))
                if len(dl) > 0:
                    defensive_list[(i, j)] = len(dl)*10
                    defensive_list = dict( sorted(defensive_list.items(), key=operator.itemgetter(1),reverse=True))
    return attacking_list, suicide_list, invalid_moves, defensive_list
    


# In[1549]:


l = liberty_moves(curr_board)
test = deepcopy(curr_board)
attacking_list, suicide_list, invalid_moves, defensive_list = calculate_liberty(test)
liberty_list = dict( sorted(l.items(), key=operator.itemgetter(1),reverse=True))
for a in invalid_moves:
    if a in attacking_list:
        attacking_list.pop(a, None)
    if a in liberty_list:
        liberty_list.pop(a, None)
    if a in defensive_list:
        defensive_list.pop(a, None)
for b in suicide_list:
    if b in attacking_list:
        attacking_list.pop(b, None)
    if b in liberty_list:
        liberty_list.pop(b, None)
    if b in defensive_list:
        defensive_list.pop(b, None)
def find_move(board):    
    for i in range(5):
        for j in range(5):      
            if (i, j) not in invalid_moves and (i, j) not in suicide_list:
                if board[2][2] == 0 and (2, 2) not in suicide_list and (2, 2) not in invalid_moves:
                    move = (2, 2)
                else:
                    if attacking_list:
                        if defensive_list:
                            if list(attacking_list.values())[0] > list(defensive_list.values())[0]:
                                move = list(attacking_list.keys())[0]
                            else:
                                move = list(defensive_list.keys())[0]
                        else:
                            move = list(attacking_list.keys())[0]
                    else:
                        move = list(liberty_list.keys())[0]
    return move


# In[1548]:


move = find_move(test)
#print(move)
if move:
    with open("./output.txt", "w") as f:
        f.write('{},{}'.format(move[0],move[1]))
else:
    with open("./output.txt", "w") as f:
        f.write('PASS')


# In[1416]:


# def alpha_beta(board, d, maxPlayer, a, b):
    
#     if d == 2:
#         value = []    
#         l = liberty_moves(curr_board)
#         test = deepcopy(board)
#         attacking_list, suicide_list, invalid_moves = calculate_liberty(test)
#         liberty_list = dict( sorted(l.items(), key=operator.itemgetter(1), reverse=True))
#         for a in invalid_moves:
#             if a in attacking_list:
#                 attacking_list.pop(a, None)
#             if a in liberty_list:
#                 liberty_list.pop(a, None)
#         for i in range(5):
#             for j in range(5):
#                 if (i, j) not in invalid_moves:
#                     if attacking_list:
#                         value.append(list(attacking_list.values())[0])
#                         value.append(list(attacking_list.keys())[0][0])
#                         value.append(list(attacking_list.keys())[0][1])
#                     else:
#                         value.append(list(liberty_list.values())[0])
#                         value.append(list(liberty_list.keys())[0][0])
#                         value.append(list(liberty_list.keys())[0][1])
#                 else:
#                     value.append(-1)
#                     value.append(-1)
#                     value.append(-1)
#         return value
    
#     if maxPlayer:
#         best = []
#         best.append(minimum)
#         best.append(-1)
#         best.append(-1)
#         for i in range(5):
#             for j in range(5):
#                 if board[i][j] == 0:
#                     board[i][j] = me
#                     val = alpha_beta(board, d+1, False, a, b)
#                     best[0] = max(best[0], val[0])
#                     if best[0] == val[0]:
#                         best[1] = val[1]
#                         best[2] = val[2]
#                     a = max(a, best[0])
#                     if b <= a:
#                         break
#         return best
    
#     else:
#         best = []
#         best.append(maximum)
#         best.append(-1)
#         best.append(-1)
#         for i in range(5):
#             for j in range(5):
#                 if board[i][j] == 0:
#                     board[i][j] = 3-me
#                     val = alpha_beta(board, d+1, True, a, b)
#                     best[0] = min(best[0], val[0])
#                     b = min(b, best[0])
#                     if best[0] == val[0]:
#                         best[1] = val[1]
#                         best[2] = val[2]
#                     if b <= a:
#                         break
#         return best            


# In[1417]:


# test = deepcopy(curr_board)
# move = alpha_beta(test, 0, True, minimum, maximum)
# if move:
#     with open("./output.txt", "w") as f:
#         f.write('{},{}'.format(move[1],move[2]))
# else:
#     with open("./output.txt", "w") as f:
#         f.write('PASS')


# In[498]:


# def rl_game(i, j):
#     liberty_new = np.copy(liberty)
#     options = []
#     Q = np.array(np.zeros([5,5]))
# #     for i in range(5):
# #         for j in range(5):
# #             if not place_validity(i, j):
# #                 print
# #             else:
#     for i in range(1000):
#         current_state = np.random.randint(0, 5)
#         playable_actions = []
        
                    


# In[ ]:




