# -*- coding: utf-8 -*-
###############################################
#Connect 4 game with AI based on min-max algo #
#Arthur P. Guillaumin                            #
###############################################
import pygame, sys
import copy
from math import inf
from mcts import MCTS_Tree
from random import randint
import pygame.time

class Application:
    """Classe gérant l'application."""
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.main_surface = pygame.display.set_mode((self.width,self.height))
        self.plateau = Plateau()
        self.j1 = HumanPlayer("Arthur")
#        self.j1 = AlphaComputerPlayer("Alpha", 7)
        self.j2 = MCTSPlayer("Computer", 10000)
        self.round = randint(1,2)
        self.pointeur = 1
        self.last_round = self.round
        self.__main_loop()

    def __main_loop(self):
        fin = False
        while True:
            if self.last_round != self.round:
                print("testVictoire")
                if self.plateau.connectsFour(self.last_round):
                    print("Victoire")
                    fin = True
            self.last_round = self.round
            if not fin:
#                if self.round == self.j1.getId():
#                    self.plateau.play(self.j1.play(self.plateau), self.j1.getId())
                if self.round == self.j2.getId():
                    self.plateau.play(self.j2.play(self.plateau), self.j2.getId())
                    self.round = 3-self.round
            #Gestion centralisée des évènements
            for event in pygame.event.get():
                self.__handle_event(event)
            #On dessine...
            self.main_surface.blit(self.plateau.get_drawn_surface(self.width,
                                                                  self.height,
                                                                  self.j1,
                                                                  self.j2), \
                                   (0,0))
            self._draw_arrow()
            pygame.display.update()

    def __handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONUP:
            pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.pointeur = max(self.pointeur-1, 1)
            elif event.key == pygame.K_RIGHT:
                self.pointeur = min(self.pointeur+1, 7)
            elif event.key == pygame.K_SPACE:
                if self.plateau.canPlayColumn(self.pointeur-1):
                    if self.round == self.j1.id:
                        self.plateau.play(self.pointeur-1, self.round)
                        self.round = 3-self.round

    def _draw_arrow(self):
        """Fonction qui dessine la flèche"""
        pygame.draw.line(self.main_surface, pygame.Color(0,0,0), (int(self.width/9.0)*(self.pointeur), 10),\
                         (int(self.width/9.0)*(self.pointeur), 30), 5)

class Plateau:
    """Classe gérant le contenu du plateau de puissance 4"""
    def __init__(self):
        self.cases = [[0 for k in range(7)] for i in range(6)]

    def play(self, j, player_id):
        """Exécute un coup. Pas de vérification."""
        assert self.canPlayColumn(j)
        assert player_id == 1 or player_id == 2
        #On cherche la première case vide de la colonne
        i_ = None
        for i in range(6):
            if self.cases[i][j] == 0:
                self.cases[i][j] = player_id
                i_ = i
                break
        return (i_,j)

    def unPlay(self, j):
        """Annule le dernier coup joué en la colonne j."""
        for i in range(1, 6):
            if self.cases[i][j] == 0:
                self.cases[i-1][j] = 0
                break
        if self.cases[5][j] != 0:
            self.cases[5][j] = 0
    
    def unplay_list(self, l):
        for j in l:
            self.unPlay(j)

    def canPlayColumn(self, j):
        return self.cases[5][j] == 0
    
    def possible_plays(self):
        return [i for i in range(7) if self.canPlayColumn(i)]
    
    def count(self, player_id, nb):
        compteur = 0
        for i in range(6):
            for j in range(7-nb+1):
                #Horizontale
                c = 0
                k = j
                while k < 7 and self.cases[i][k] == player_id:
                    c += 1
                    k += 1
                    if c == nb:
                        compteur +=  1
                #Diagonale (1,1)
                c = 0
                k = i
                l = j
                while k < 6 and l < 7 and self.cases[k][l] == player_id:
                    c += 1
                    k += 1
                    l += 1
                    if c== nb:
                        compteur += 1
                #Diagonale (1,-1)
                c = 0
                k = i
                l = j
                while k >= 0 and l < 7 and self.cases[k][l] == player_id:
                    c += 1
                    k -= 1
                    l += 1
                    if c== nb:
                        compteur += 1
        for i in range(6-nb+1):
            for j in range(7):
                #Verticale
                c = 0
                k = i
                while k <6 and self.cases[k][j] == player_id:
                    c += 1
                    k += 1
                    if c == nb:
                        compteur +=  1
        return compteur
    
    def connectsFour(self, playerId):
        """This function returns True if the playerId has 4 connected"""
        return self.count(playerId, 4) > 0
    
    def connectsFour2(self, playerId, pos):
        i,j = pos
        #Horizontal check
        c, c2, c3 = 0,0,0
        left = max(0, j-3)
        right = min(6, j+3)
        for j2 in range(left, right):
            if self.cases[i][j2] == playerId:
                c = c+1
                if c == 4:
                    return True
            else:
                c = 0
        #Other 3 directions
        c = 0
        bottom = max(0, i-3)
        top = min(5, i+3)
        for i2 in range(bottom, top+1):
            #Vertical check
            if self.cases[i2][j] == playerId:
                c = c+1
                if c == 4:
                    return True
            else:
                c = 0
            if self.cases[i2][j+i2-i] == playerId:
                c2 = c2+1
                if c2 == 4:
                    return True
            else:
                c2=0
            if self.cases[i2][j-(i2-i)] == playerId:
                c3 = c3+1
                if c3 == 4:
                    return True
            else:
                c3=0
        return False
        

    def get_drawn_surface(self, width, height, j1, j2):
        """Retourne une surface sur laquelle est dessinée
        le plateau."""
        surface = pygame.Surface((width, height))
        #On dessine le fond
        surface.fill(pygame.Color(255, 255, 255))
        #On dessine les cases
        centerW = width/2
        centerH = height/2
        radius1 = int(0.7 * width / 14.0)
        radius2 = int(0.7 * height / 12.0)
        radius = min(radius1, radius2)
        for i in range(6):
            for j in range(7):
                if self.cases[i][j] == j1.id:
                    c = j1.color
                elif self.cases[i][j] == j2.id:
                    c = j2.color
                else:
                    c = pygame.Color(0, 0, 0)
                x = int(width/9.0)*(j+1)
                y = height-int(height/8.0)*(i+1)
                pygame.draw.circle(surface, c, (x, y), radius)
        return surface

class Player:
    """Classe gérant un joueur et ses informations."""
    numJoueurs = 0
    colors = [pygame.Color(255,0,0), pygame.Color(0,0,255)]
    def __init__(self, name=""):
        assert Player.numJoueurs < 2
        Player.numJoueurs += 1
        self.id = Player.numJoueurs
        self.name = name
        self.color = self.colors[self.id-1]

    def getId(self):
        return self.id

    def getOpponentId(self):
        return self.id%2+1

    def play(self):
        pass

class HumanPlayer(Player):
    """Classe gérant le cas particulier d'un joueur humain."""
    def __init__(self, name=""):
        Player.__init__(self, name)

    def play(self):
        pass

class ComputerPlayer(Player):
    """Classe gérant un joueur de type intelligence artificielle."""
    def __init__(self, name="", level=1):
        Player.__init__(self, name)
        self.level = level

    def play(self, plateau):
        score, column = self.max_c(plateau, self.level)
        return column

    def min_c(self, plateau, depth):
        if depth == 0:
            return (self.assess(plateau),0)
            return (0,0)
        else:
            score_min = inf
            column_min = 0
            for j in range(7):
                if plateau.canPlayColumn(j):
                    play = plateau.play(j, self.getOpponentId())
                    if plateau.connectsFour2(self.getOpponentId(), play):
                        plateau.unPlay(j)
                        return (-inf, j)
                    score, temp = self.max_c(plateau, depth-1)
                    if score <= score_min:
                        score_min = score
                        column_min = j
                    plateau.unPlay(j)
        return (score_min, column_min)

    def max_c(self, plateau, depth):
        if depth == 0:
            return (self.assess(plateau),0)
        else:
            score_max = -inf
            column_max = 0
            for j in range(7):
                if plateau.canPlayColumn(j):
                    play = plateau.play(j, self.id)
                    if plateau.connectsFour2(self.id, play):
                        plateau.unPlay(j)
                        return (inf, j)
                    score, temp = self.min_c(plateau, depth-1)
                    if depth == self.level:
                        print(score)
                    if score >= score_max:
                        score_max = score
                        column_max = j
                    plateau.unPlay(j)
        return (score_max, column_max)

    def assess(self, plateau):
        """Fonction d'évaluation."""
#        On compte le nombre de séries de 3
        compteur1 = plateau.count(self.id, 3)
        compteur2 = plateau.count(self.getOpponentId(), 3)
#        compteur14 = plateau.count(self.id, 4)
#        compteur24 = plateau.count(self.getOpponentId(), 4)
#        if compteur14 > 0:
#            return inf
#        if compteur24 > 0:
#            return -inf
        return compteur1*200-compteur2*20

    

class AlphaComputerPlayer(ComputerPlayer):
    """This class implements the alpha-beta pruning algorithm to make mini-max
    computationally more efficient"""
    def __init__(self, name="", level=1):
        super().__init__(name, level)
    
    def play(self, plateau):
        score, column = self.max_c(plateau, self.level, inf)
        return column

    def min_c(self, plateau, depth, alpha):
        if depth == 0:
            return (self.assess(plateau),0)
        else:
            score_min = inf
            column_min = 0
            for j in range(7):
                if plateau.canPlayColumn(j):
                    plateau.play(j, self.getOpponentId())
                    if plateau.connectsFour(self.getOpponentId()):
                        plateau.unPlay(j)
                        return (-inf, j)
                    score, temp = self.max_c(plateau, depth-1, score_min)
                    plateau.unPlay(j)
                    if score <= score_min:
                        score_min = score
                        column_min = j
                        if score < alpha:
                            break
        return (score_min, column_min)

    def max_c(self, plateau, depth, alpha):
        if depth == 0:
            return (self.assess(plateau),0)
        else:
            score_max = -inf
            column_max = 0
            for j in range(7):
                if plateau.canPlayColumn(j):
                    plateau.play(j, self.id)
                    if plateau.connectsFour(self.id):
                        plateau.unPlay(j)
                        return (inf, j)
                    score, temp = self.min_c(plateau, depth-1, score_max)
                    plateau.unPlay(j)
                    if score >= score_max:
                        score_max = score
                        column_max = j
                        if score > alpha:
                            break
            if depth == self.level and score_max == -inf:
                if self.level > 1:
                    return self.max_c(plateau, self.level-1, inf)
        return (score_max, column_max)



class MCTSPlayer(ComputerPlayer):
    """This class implements a Monte Carlo Tree Search algorithm"""
    def __init__(self, name="", level=1000):
        super().__init__(name, level)
    
    def play(self, plateau):
        id_AI = self.getId()
        self.tree = MCTS_Tree(copy.deepcopy(plateau), id_AI, id_AI)
        for i_sim in range(self.level):
            node = self.tree.select()
            sim = node.expand()
            success = sim.simulate()
            sim.backpropagate(success)
        return self.tree.get_play()
        
        

app = Application()
    
            
