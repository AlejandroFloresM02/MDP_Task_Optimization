import numpy as np

class MDP:
    def __init__(self,s,a,tp,r,df):
        """
        s - States of MDP
        a - Actions the agent can take
        tp - transition probabilities
        r - rewards
        df - discount factor
        """
        self.s = s
        self.a = a
        self.tp = tp
        self.r = r
        self.df = df
    
