import numpy as np
import pandas as pd
import csv 
from sys_eq import *

queue = [0,0,0,0,0,0,0]
decision =[]
while len(queue)>0:
    action_set = set(queue)
    #print(action_set)
    state = int(input("Current state: "))
    backwrd =int(input("Current backward: "))
    if not (1<=state<=4 and backwrd>=0):
        print("invalid args")
        continue
    
    try:
        df = getPolicy(list(action_set))
        action = df.loc[(df["State"] == state) & (df["Backward"] == backwrd)]["Action index"].item()
    except:
        print("invalid args")
        continue
    #print(action)
    if action != 3:
        queue.remove(action)
    decision.append(action)
    print(decision)
decision.append(3)
print(decision)
    
    