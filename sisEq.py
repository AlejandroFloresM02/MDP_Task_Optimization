import numpy as np
from scipy.io import loadmat
import pandas as pd

actions = {
    "navigate1":1,
    "navigate2":2,
    "navigate3":3,
    "recharge":4,
}
state_names = ["CRITICAL","LOW","MEDIUM","HIGH"]
systemData = loadmat('system_data.mat')
trans_mats = systemData["transition_mats"]
discount_fact = systemData["discount"][0]
rewards = systemData["rewards"]
#print(rewards)
#print(systemData)
#print(systemData["transition_mats"][:,:,3][0,0])
#print(actions)
#print(len(systemData["states"][0]))
iter_limit = 1000
states_amount = len(systemData["states"][0])
state_values = np.zeros(states_amount)
action_amount = len(actions)
    #Origin state, next state, action
#print(rewards[0])
for iter in range(iter_limit):
    new_state_values = np.zeros(states_amount)
    for state in range(states_amount):
        action_values = np.zeros(action_amount)
        for key in actions:
            action_val = rewards[state, actions[key]-1]
            for next_state in range(states_amount):
                action_val += discount_fact * trans_mats[state, next_state, actions[key]-1] * state_values[next_state]
            action_values[actions[key]-1] = action_val
        new_state_values[state] = np.max(action_values)
    state_values = new_state_values
    
#print(state_values)


optimal_policy = np.zeros(states_amount, dtype=int)  # Inicializa una política arbitraria

for state in range(states_amount):
    action_values = np.zeros(action_amount)
    for key in actions:
        action_val = rewards[state, actions[key]-1]
        for next_state in range(states_amount):
            action_val += discount_fact * trans_mats[state, next_state, actions[key]-1] * state_values[next_state]
        action_values[actions[key]-1] = action_val    
    optimal_policy[state] = np.argmax(action_values)

optimal_policy_names = []
actions_list = list(actions)
#print(actions_list[optimal_policy[0]])
for i in range(len(optimal_policy)):
    optimal_policy_names.append(actions_list[optimal_policy[i]])

frame = pd.DataFrame({"State name":state_names,"Action index":optimal_policy,"Action":optimal_policy_names})
print(frame.to_string(index=False))
