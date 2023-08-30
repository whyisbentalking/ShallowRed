
import pandas as pd
import numpy as np
import tabula 
from Projections import importProjections as ip
from math import *
import random
import tkinter as Tk
from tkinter import *
from tkinter import ttk
from pandastable import Table, TableModel

class DraftApp(Frame):
        """Basic test frame for the table"""
        def __init__(self,df = None, parent=None):
            self.parent = parent
            Frame.__init__(self)
            #self.title("")
            # tabControl = ttk.Notebook(self)
            # tab1 = ttk.Frame(tabControl)#app#ttk.Frame(app,text = "Projections")
            # tab2 = ttk.Frame(tabControl)
            # tabControl.add(tab1,text="Projections")
            # tabControl.add(tab2,text="Draft")
            # ttk.Label(tab1)
            # ttk.Label(tab2,text="Let's Draft").grid(column=0,row=0,padx=30,pady=30)
            self.main = self.master
            self.main.geometry('400x600+200+100')
            self.main.title('Table app')
            f = Frame(self.main)
            f.pack(side="left",fill=BOTH,expand=1)
            #df = TableModel.getSampleData()
            self.table = pt = Table(f, dataframe=df,
                                    showtoolbar=True, showstatusbar=True)

            pt.show()

            num_competitors = int(input("Enter Number of Competitors: "))

            num_rounds = int(input("Enter the Number of Rounds: "))

            draft_position = int(input("Enter your draft position: "))
            draft_type = input("Draft Type: ")

            draft_position = draft_position-1

            #draft(num_competitors,num_rounds,3,df)

            NflPlayer = NFLPlayer
            freeagents = [NflPlayer(*p) for p in df.itertuples(index=False, name=None)]
            #num_competitors = 10
            rosters = [[] for _ in range(num_competitors)] # empty rosters to start with
            #num_rounds = 16
            turns = []
            # generate turns by snake order
            for i in range(num_rounds):
                turns += reversed(range(num_competitors)) if i % 2 else range(num_competitors)
                
            print(turns)    
            state = DraftState(rosters, turns, freeagents)
            iterations = 800
            vis_df = self.table.model.df


            #print(state)

            while state.GetMoves() != [] and draft_type == "sim":
                move, _ = UCT(state, iterations)
                print("Best Move: " + str(move) )#print(move, end=".")
                state.DoMove(move)
                        #self.table.redraw()
                    #state.DoMove(move)


            while state.GetMoves() != [] and draft_type != "sim":
                if turns[0] == draft_position:
                    move, _ = UCT(state, iterations)
                    print("Best Move: " + str(move) )#print(move, end=".")
                    illegal = 1
                    while illegal ==1:
                        manualMove = input("Enter your pick: ")
                        if manualMove in vis_df['name'].values: #vis_df['name'].str.contains(manualMove).any()
                            illegal = 0
                        else:
                            print("bad name pick again")
                    state.DoMoveManual(manualMove)
                    vis_df.drop(vis_df[vis_df.name == manualMove].index, inplace=True)
                    self.table.redraw()

                    #state.DoMove(move)
                else:
                    illegal = 1
                    while illegal ==1:
                        #move = UCT(state, iterations)
                        manualMove = input(f"Enter player{turns[0]+1} pick: ")
                        # a['Names'].str.contains('Mel').any():
                        if manualMove in vis_df['name'].values:
                            illegal = 0
                        else:
                            print("bad name pick again")

                    state.DoMoveManual(manualMove)
                    vis_df.drop(vis_df[vis_df.name == manualMove].index, inplace=True)
                    self.table.redraw()

            pd.DataFrame({"Team " + str(i + 1): r for i, r in enumerate(state.rosters)}).to_csv("Projections\\sim_results.csv") 
                                
            return 
              


class NFLPlayer:
    def __init__(self, name, team, position, points):
        self.name = name
        self.team = team
        self.position = position
        self.points = points

    def __repr__(self):
        return "|".join([self.name, self.team, self.position, str(self.points)])
    
class DraftState:
    def __init__(self, rosters, turns, freeagents, playerjm=None):
        self.rosters = rosters
        self.freeagents = freeagents
        self.turns = turns
        self.playerJustMoved = playerjm


    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm.
        """
        if playerjm is None: return 0
        
        pos_wgts = {
            ("QB"): [.6, .4],#.6
            ("WR"): [.7, .7, .4, .2],#.7
            ("RB"): [.7, .7, .4, .2],#.7
            ("TE"): [.6, .4],#.6
            ("RB", "WR", "TE"): [.6, .4],#.6
            ("D/ST"): [.5, .3, .1],#.5
            ("K"): [.5, .2, .2, .1]#.4
        }
        result = 0
        # map the drafted players to the weights
        for p in self.rosters[playerjm]:
            max_wgt, _, max_pos, old_wgts = max(
                ((wgts[0], -len(lineup_pos), lineup_pos, wgts) for lineup_pos, wgts in pos_wgts.items()
                    if p.position in lineup_pos),
                default=(0, 0, (), []))
            if max_wgt > 0:
                result += max_wgt * p.points
                old_wgts.pop(0)
                if not old_wgts:
                    pos_wgts.pop(max_pos)
                    
        # map the remaining weights to the top three free agents
        for pos, wgts in pos_wgts.items():
            result += np.mean([p.points for p in self.freeagents if p.position in pos][:3]) * sum(wgts)
        return result
    
    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        pos_max = {"QB": 2, "WR": 5, "RB": 5, "TE": 2, "D/ST": 2, "K": 1}
        if len(self.turns) == 0: return []
        roster_positions = np.array([p.position for p in  self.rosters[self.turns[0]]], dtype=str)
        moves = [pos for pos, max_ in pos_max.items() if np.sum(roster_positions == pos) < max_]
        return moves

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        player = next(p for p in self.freeagents if p.position == move)
        #print(player.name)
        rosterId = self.turns.pop(0)
        self.rosters[rosterId].append(player)
        self.playerJustMoved = rosterId
        self.freeagents.remove(player)

    def DoMoveManual(self, PlayerName):
        player = next(p for p in self.freeagents if p.name == PlayerName)
        self.freeagents.remove(player)
        rosterId = self.turns.pop(0)
        self.rosters[rosterId].append(player)
        self.playerJustMoved = rosterId

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        rosters = [r[:] for r in self.rosters]
        st = DraftState(rosters, self.turns[:], self.freeagents[:],
                self.playerJustMoved)
        return st
    
class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves() # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        
    def __repr__(self):
        return "[M:" + str(self.move) + " S:" + str(self.wins/self.visits) + " U:" + str(self.untriedMoves) + "]"
    
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        UCTK = 200
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result
    
    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose = False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
    """
    rootnode = Node(state = rootstate)
    for i in range(itermax):
        #print(i)
        node = rootnode
        state = rootstate.Clone()
        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)
        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves) 
            state.DoMove(m)
            node = node.AddChild(m,state) # add child and descend tree
        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []: # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))
        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    nodes = sorted(rootnode.childNodes, key = lambda c: -c.wins / c.visits)
    return nodes[0].move if nodes else None, nodes
    #return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited


def main():

    

    df = ip.get_Projections()
    df.rename(columns={"FF Pt":"points","Name":"name","Team":"team","Pos":"position"},inplace=True)
    nfl_players = df.drop(columns={"id","Pos Rk","G","P Att","Comp","P Yds","P TD","INT","Sk","Carry",'Ru Yds',"Ru TD","Targ","Rec","Re Yd","Re TD","Car%","Targ%","SCK","FR","TD","PA","YA"})
    #print(nfl_players.head(5))

    app = DraftApp(nfl_players)

    #launch the app
    app.mainloop()



if __name__ == '__main__':
    main()





