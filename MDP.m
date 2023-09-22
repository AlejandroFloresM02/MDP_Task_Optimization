%"Markov Decision Process for Battery usage optimization"
%States, where bigger is more charged
states = [1,2,3,4];
actions = ["navigate1","navigate2","idle","recharge"]; 
rewards =  [[10,6,4,-10],...
            [7,5,4,-5],...
            [2,4,5,1],...
            [-15,-10,-7,10]]; %Maybe? idk - YE
discount = 0.85; 
load("trans_mats")
disp(matrices)

