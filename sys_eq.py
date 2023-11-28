import numpy as np
import pandas as pd
import csv 


def joinMats(name_arr):
    mat = []
    for i in range(len(name_arr)):
        curr_trans = np.array([[float(x) for x in rec] for rec in csv.reader(open(name_arr[i]))])
        #print(curr_trans)
        mat.append(curr_trans)
    #print(mat)
    return mat
        
def loadTransMats(arr, act_num):
    step = len(arr[0])//act_num
    mat = np.array([arr[:,0:4]])
    #print(mat)
    #print(arr[:,0:4])
    for i in range(1,act_num):
        act_mat = arr[:,i*step:(i+1)*step]
        #print(act_mat)
        mat = np.vstack((mat,[act_mat]))
        #print("\n")
    return mat
    
def findUniquePairs(arr):
    joined_arr = np.array([])
    for i in arr:
        if joined_arr.size == 0:
            joined_arr = i[:,0:2]
        else:
            joined_arr = np.vstack([joined_arr, i[:,0:2]])
    #print(joined_arr)
    res = np.unique(joined_arr,axis=0)
    return res

def findActionPairIndex(trans_mat, pair):
    _trans_mat = trans_mat.tolist()
    _pair = pair.tolist()
    return _trans_mat.index(_pair)
    
def getPolicy(actions):
    actions_struct = {
        "navigate1":0,
        "navigate2":1,
        "navigate3":2,
        "recharge":3,
    }
    all_actions = list(actions_struct.keys())
    actions = [all_actions[act] for act in actions]
    #print(actions)
    actions.append("recharge")
    difference = list(set(actions_struct.keys())-set(actions))
    for action in difference: actions_struct.pop(action)
    actions = actions_struct 
    #print(actions)

    state_names = ["CRITICAL","LOW","MEDIUM","HIGH"]

    #trans_mats_arr = np.array([[float(x) for x in rec] for rec in csv.reader(open("data/trans_mats.csv"))])
    trans_mats = joinMats(["SM_trans_mat_path_1.csv","SM_trans_mat_path_2.csv","SM_trans_mat_path_3.csv","SM_trans_mat_recharge.csv"]) #Make sure this is the same order as the actions
    u_pairs = findUniquePairs(trans_mats)
    #print(trans_mats[0])

    discount_fact = 0.85

    rewards = np.array([[int(x) for x in rec] for rec in csv.reader(open("data/rewards.csv"))])

    iter_limit = 100
    states_amount = len(u_pairs)



    state_values = np.zeros(states_amount)
    #action_amount = len(actions)
    #Origin state, next state, action
    #print(rewards[0])
    for iter in range(iter_limit):
        #print("iteration", iter)
        new_state_values = np.zeros(states_amount)
        for state in range(states_amount):
            action_values = np.zeros(len(all_actions))
            for key in actions:
                #print(u_pairs[state])
                action_val = rewards[int(u_pairs[state][0]-1), actions[key]]
                for next_state in range(len(state_names)):
                    #print(trans_mats[actions[key]])
                    try:
                        pair_index = findActionPairIndex(trans_mats[actions[key]][:,0:2],u_pairs[state])
                    except:
                        continue
                    if u_pairs[state][0]-1 == next_state:
                        backward = u_pairs[state][1] + 1
                    else:
                        backward = 0 
                    #print(trans_mats[actions[key]][:,0:2])
                    try:
                        next_pair_index = findActionPairIndex(trans_mats[actions[key]][:,0:2],np.array([next_state+1,backward]))
                    except:
                        continue
                    #print("state/bckwrd", u_pairs[state])
                    #print("next state/bckwrd", trans_mats[actions[key]][next_pair_index][0:2])
                    action_val += discount_fact * trans_mats[actions[key]][pair_index][next_state+2] * state_values[next_state]
                #print("Last for done")
                action_values[actions[key]] = action_val
            #print("Second to last for done")
            new_state_values[state] = np.max(action_values)
        state_values = new_state_values

    #print(state_values)


    optimal_policy = np.zeros(states_amount, dtype=int)  # Inicializa una política arbitraria

    for state in range(states_amount):
        action_values = np.zeros(len(all_actions))
        for key in actions:
            action_val = rewards[int(u_pairs[state][0]-1), actions[key]]
            for next_state in range(len(state_names)):
                try:
                    pair_index = findActionPairIndex(trans_mats[actions[key]][:,0:2],u_pairs[state])
                except:
                    continue
                #print(trans_mats[actions[key]][pair_index][next_state+2])
                action_val += discount_fact * trans_mats[actions[key]][pair_index][next_state+2] * state_values[next_state]
            action_values[actions[key]] = action_val
        optimal_policy[state] = np.argmax(action_values)

    optimal_policy_names = []
    actions_list = list(actions)
    #print(action_values)
    for i in range(len(optimal_policy)):
        optimal_policy_names.append(all_actions[optimal_policy[i]])
    ext_names = []
    for i in u_pairs:
        ext_names.append(state_names[int(i[0])-1])
        
    frame = pd.DataFrame({"State name":ext_names,"State":u_pairs[:,0].astype(int),"Backward":u_pairs[:,1].astype(int),"Action index":optimal_policy,"Action":optimal_policy_names})
    frame = frame.sort_values(["State", "Backward"],ascending=[False, True])
    #print(frame.to_string(index=False))
    return frame

if __name__ == '__main__':
    getPolicy(["navigate1","navigate2","navigate3"])
    