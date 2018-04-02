# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 12:00:16 2017

@author: Arthur
"""
from random import randint
from math import sqrt, log, inf
from copy import deepcopy
 

class MCTS_Tree:
    def __init__(self, plateau, id_p, id_c, parent = None, value = None):
        self.root = plateau
        self.value = value
        #id of the AI
        self.id = id_p
        #ID corresponding to the state (i.e. whose turn it is to play)
        self.id_current = id_c
        self.nb_simulations = 0
        self.nb_successes = 0
        self.children = []
        self.parent = parent
        self.c = sqrt(2)
        self.is_terminal = False
        self.tie = False
    
    def select(self):
        if self.children == []:
            return self
        else:
            assess_values = [s.assess() for s in self.children]
            max_val = max(assess_values)
            i_max = assess_values.index(max_val)
            selected_child = self.children[i_max]
            return selected_child.select()
    
    def assess(self):
        wi = self.nb_successes
        ni = self.nb_simulations
        Ni = self.parent.nb_simulations
        if ni == 0:
            return inf
        return wi/ni + self.c*sqrt(log(Ni)/ni)
    
    def get_state(self):
        """This function returns the state of the plateau corresponding to the
        node in the tree"""
        p = self.parent
        if p is not None:
            p.get_state()
            self.root.play(self.value, p.id_current)
        else:
            pass
    
    def undo_get_state(self):
        p = self.parent
        if p is not None:
            self.root.unPlay(self.value)
            p.undo_get_state()
    
    def possible_plays(self):
        self.get_state()
        possible_plays = self.root.possible_plays()
        self.undo_get_state()
        return possible_plays
    
    def expand(self):
        """This method takes care of the expension step. It returns the node
        that should be used for simulation. If the node is terminal then we
        return that same node (simulation will then be trivial!). If not, if
        the node has not been simulated, we return that same node. If it has
        been simulated, we actually do the expension and return the first 
        child. If the node has no children after expension, we return the 
        node itself"""
        if self.is_terminal:
            return self
        elif self.nb_simulations == 0:
            return self
        else:
            self.get_state()
            possible_plays = self.root.possible_plays()
            for p in possible_plays:
                self.children.append(MCTS_Tree(self.root, self.id, 3-self.id_current, 
                                               self, p))
            for child in self.children:
                self.root.play(child.value, self.id_current)
                connect = self.root.connectsFour(self.id_current)
                if connect:
                    child.is_terminal = True
                self.root.unPlay(child.value)
            self.undo_get_state()
            if self.children == []:
                self.tie = True
                return self
            else:
                return self.children[0]
    
    def simulate(self):
        """This function simulates does the simulation step for the node. It
        returns the success value, which is 1 (success), 0 (not success), or
        -1 (neutral, i.e. end of game but without any winner"""
        if self.is_terminal:
            return 0
        if self.tie == []:
            return -1
        self.get_state()
        #Random play
        id_current = self.id_current
        l=[]
        while True:
            possible_plays = self.root.possible_plays()
            if possible_plays == []:
                self.root.unplay_list(l)
                self.undo_get_state()
                return -1
            i = randint(0, len(possible_plays)-1)
            p = possible_plays[i]
            l.append(p)
            play = self.root.play(p, id_current)
            connect = self.root.connectsFour2(id_current, play)
            if connect:
                self.root.unplay_list(l)
                self.undo_get_state()
                if self.id_current == id_current:
                    return 1
                else:
                    return 0
            id_current = 3-id_current
    
    def backpropagate(self, success):
        """The parameter success means success for the current node here. As
        nb_successes denotes the number of succes the current node gives for 
        the parent node we need to do 1-success."""
        if success != -1:
            success = 1-success
            self.nb_successes = self.nb_successes + success
        self.nb_simulations = self.nb_simulations + 1
        p = self.parent
        if p is not None:
            p.backpropagate(success)
    
    def get_play(self):
        values = [c.nb_successes/c.nb_simulations for c in self.children]
        i_max = values.index(max(values))
        return self.children[i_max].value
    