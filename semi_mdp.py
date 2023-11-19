import numpy as np
from scipy.io import loadmat
import pandas as pd
import csv

num_states = 4
def maxBackward(list):
    #print(max_back)
    reps = np.zeros(num_states)
    curr_back = 0
    for i in range(1,len(list)):
        if list[i] == list[i-1]:
            curr_back += 1
            #print(max(curr_back,reps[list[i]-1]))
            reps[list[i]-1] = max(curr_back,reps[list[i]-1])
        else:
            curr_back = 0
    #print(reps)
    return reps

def getBackwardArray(state_list):
    backward = np.zeros(np.size(state_list))
    for i in range(1,len(state_list)):
        if state_list[i-1] == state_list[i]:
            backward[i] = backward[i-1]+1
        else:
            backward[i] = 0
    return backward

def getTransMatIndex(total_back):
    indexes = np.array([-1,-1])
    for i in range(len(total_back)):
        tempindex_arr = np.zeros(int(total_back[i]+1))+i+1
        tempback_arr = np.arange(0,total_back[i]+1,1)
        mixed_arr = np.vstack((tempindex_arr,tempback_arr))
        #print(mixed_arr)
        indexes = np.vstack((indexes,mixed_arr.T))
    return indexes[1:]
        
def SMDPTransMat(state_list, exp_name):
    struct_mats = []
    max_backs = []
    for exp in state_list:
        #Variables names could be improved :)
        #later (:
        max_back_arr = maxBackward(exp)
        max_backs.append(max_back_arr)
        state_num = len(max_back_arr)
        struct_mat = np.zeros([2,len(exp)])
        #print(exp)
        struct_mat[1] = exp
        back_counter = 0
        for i in range(len(struct_mat[0])):
            if struct_mat[1][i] == struct_mat[1][i-1] and i != 0:
                back_counter += 1
            else:
                back_counter = 0
            struct_mat[0][i] = back_counter

        struct_mats.append(struct_mat)

    total_back = np.zeros(state_num)
    for i in max_backs:
        total_back = np.fmax(total_back,i)

    
    trans_mat = np.zeros([int(sum(total_back))+state_num,state_num])

    trans_index = np.asarray(getTransMatIndex(total_back))
    
    print(struct_mats[1])

    for exp_index in range(len(state_list)):
        print(struct_mats[exp_index])
        for i in range(len(state_list[exp_index])-1):
            curr_back = int(struct_mats[exp_index][0,i])
            origin = int(struct_mats[exp_index][1,i])
            next_state = int(state_list[exp_index][i+1])
            print([origin,curr_back])
            print(next_state)
            curr_index = np.where(np.logical_and(trans_index[:,0] == origin, trans_index[:,1] == curr_back))[0]
            print(curr_index)
            trans_mat[curr_index,state_list[exp_index][i+1]-1] = trans_mat[curr_index,state_list[exp_index][i+1]-1]+1
            #print(curr_index)
        #print(struct_mats[exp_index])
    print(trans_mat)

    #print(trans_mat)
    trans_index = trans_index[~np.all(trans_mat==0,axis = 1)]
    trans_mat = trans_mat[~np.all(trans_mat==0,axis = 1)]
    for i in range(len(trans_mat)):
        if sum(trans_mat[i]) != 0:
            trans_mat[i] = trans_mat[i]/sum(trans_mat[i])

            
    #print(np.hstack((trans_index,trans_mat)))
    df = np.hstack((trans_index,trans_mat))
    print(df)
    pd.DataFrame(df.round(2)).to_csv('SM_trans_mat_'+ exp_name +'.csv',header=False,index=False)


                            
if __name__ =="__main__":
    exp = "path_3"
    file = open("data/refined_data/" + exp + ".csv","r")
    #data = [4,4,4,4,3,3,4,3,4,3,3,3,4,3,3,3,3,3,2,2,2,3,2,2,2,2,2,2,2,1,1,1,2,1,1,1,1,1]
    data = [[int(x) for x in rec] for rec in csv.reader(file)]
    #print (data)
    SMDPTransMat(data, exp)
