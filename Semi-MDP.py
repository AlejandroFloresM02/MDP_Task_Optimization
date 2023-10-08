import numpy as np
from scipy.io import loadmat
import pandas as pd
import csv

"""actions = {
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
state_sequence =[] """

def maxBackward(list):
    unique_set = sorted(set(list))
    max_back = len(unique_set)
    #print(max_back)
    reps = np.zeros(max_back)
    curr_back = 0
    for i in range(1,len(list)-1):
        if list[i] == list[i-1]:
            curr_back += 1
            #print(max(curr_back,reps[list[i]-1]))
            reps[list[i]-1] = max(curr_back,reps[list[i]-1])
        else:
            curr_back = 0
    return reps

def getBackwardArray(state_list):
    backward = np.zeros(np.size(state_list))
    for i in range(1,len(state_list)):
        if state_list[i-1] == state_list[i]:
            backward[i] = backward[i-1]+1
        else:
            backward[i] = 0
    return backward
            
def SMDPTransMat(state_list):
    max_back_arr = maxBackward(state_list)
    state_num = len(max_back_arr)
    #print(max_back_arr)
    rows = int(sum(max_back_arr))
    struct_mat = np.zeros([2,rows+state_num])
    item_num = 0
    struct_mat[1,0] = 1
    counter = 0
    for i in range(1,rows+state_num+1):
        counter +=1
        #print(struct_mat, "\n\n")
        if counter <= max_back_arr[item_num]:
            struct_mat[0,i] = counter
        else:
            #print("change")
            item_num+=1
            counter = 0
        if i < len(struct_mat[1]): struct_mat[1,i] = item_num+1
    #print(struct_mat)
        
    trans_mat = np.zeros([rows+state_num,state_num])
    #print(trans_mat)

    """for i in range(len(trans_mat)):
        #for i in [0]:
        desired_back = struct_mat[0,i]
        origin = struct_mat[1,i]
        #print("desired_back", desired_back, "origin", origin)
        #initialize elements to check backward
        for j in range(len(state_list)-1):
            if state_list[j] == origin:
                backward = 0
                current_index = j
                while backward <= desired_back:
                    if current_index - 1 >= 0:
                        #print("entered")
                        if state_list[current_index-1] == origin:
                            backward +=1
                            current_index-=1
                        else:
                            break
                    else:
                        break
                if backward == desired_back:
                    trans_mat[i,state_list[j+1]-1] += 1
                    
        #print("-----------------")"""
    backward = getBackwardArray(state_list)
    #print(backward)
    for i in range(len(trans_mat)):
        #for i in [0]:
        desired_back = struct_mat[0,i]
        origin = struct_mat[1,i]
        #print("desired_back", desired_back, "origin", origin)
        #initialize elements to check backward
        for j in range(len(state_list)-1):
            if state_list[j] == origin:
                if backward[j] == desired_back:
                    trans_mat[i,state_list[j+1]-1] += 1            
        trans_mat[i] = trans_mat[i]/sum(trans_mat[i])
    index = []
    for i in range(len(struct_mat[0])):
        index.append(str(int(struct_mat[0,i]))+"/"+str(int(struct_mat[1,i])))
    cols = []
    for i in range(state_num):
        cols.append(i+1)
    frame = pd.DataFrame(trans_mat.round(2), index=index, columns=cols)
    print(frame)
    pd.DataFrame(trans_mat.round(2)).to_csv('SM_trans_mat',header=False,index=False)


                            
if __name__ =="__main__":
    file = open("exp/reduced_states_circles.csv","r")
    data = [4,4,4,4,3,3,4,3,4,3,3,3,4,3,3,3,3,3,2,2,2,3,2,2,2,2,2,2,2,1,1,1,2,1,1,1,1,1]
    #data = [[int(x) for x in rec] for rec in csv.reader(file)][0]
    #print (data)
    SMDPTransMat(data)
