import numpy as np
import pandas as pd
import csv 
import threading
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper
from cflib.positioning import position_hl_commander

from sys_eq import *
from follow_coords import *
from gen_sequences import get_state



def keepPos(scf, pos):
    T = threading.current_thread()
    while True:
        scf.cf.commander.send_position_setpoint(pos[0],pos[1],pos[2],0)
        time.sleep(0.1)
        if getattr(T,"finish", False):
            break

def state_cb(timestamp, data, logconf):
    global is_flying, batt, charging
    is_flying = data["sys.isFlying"]>0
    batt = data["pm.vbat"]
    charging = data["pm.state"] == 1 or data["pm.state"] == 2
    #print(data['supervisor.info'])
    #print(data['sys.canfly'])


def start_logging_state(scf):
    log_conf = LogConfig(name='State', period_in_ms=100)
    log_conf.add_variable('sys.isFlying', 'uint8_t')
    log_conf.add_variable('pm.vbat', 'float')
    log_conf.add_variable('pm.state', 'int8_t')
    log_conf.add_variable('supervisor.info', 'int16_t')
    log_conf.add_variable('sys.canfly', 'uint8_t')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(state_cb)
    log_conf.start() 

if __name__ == '__main__':
    is_flying = 0
    batt = -1

    batt_high = 3.6 #Lower limit
    batt_mid = 3.40 #Lower limit
    batt_low = 3.32 #Lower limit
    batt_crit = 3.32 #Upper limit
    v_drop = 0.4
    v_drop_c = 0.56
    charging = 0

    queue = [1,2,2,0,0,2,1,1,2]
    decision =[]
    state_hist = []
    actions = ["path_1", "path_2", "path_3"]
    prev_state, state = -1, -1
    backwrd = 0
    uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
    print("Loading drivers")
    cflib.crtp.init_drivers(enable_debug_driver=False)
    print("Drivers loaded")
    invalid = 0
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        start_logging_state(scf)
        print("Resetting estimator")
        reset_estimator(scf)
        start_position_printing(scf)
        while len(queue)>0:
            action_set = set(queue)
            prev_state = state
            if is_flying:
                state = int(get_state(batt))
            elif charging:
                state = int(get_state(batt-v_drop_c))
            else:
                state = int(get_state(batt-v_drop))
            if state == prev_state and not invalid:
                backwrd += 1
            else:
                backwrd = 0
            #print(action_set)
            #state = int(input("Current state: "))
            #backwrd =int(input("Current backward: "))
            if not (1<=state<=4 and backwrd>=0):
                print("invalid args")
                invalid = 1
                continue
            print(["State = ", state, "backward = ", backwrd])
            try:
                pos = [1.0,0.5,1.5]
                thread = threading.Thread(target=keepPos, args=[scf,pos])
                thread.daemon = True
                if not charging:
                    thread.start()
                df = getPolicy(list(action_set))
                action = df.loc[(df["State"] == state) & (df["Backward"] == backwrd)]["Action index"].item()
                if thread.is_alive():
                    thread.finish = True
                    thread.join()
            except:
                print("invalid args")
                invalid = 1
                continue
            print(action)
            if action != 3:
                if charging:
                    print("Unplug now!")
                    while charging:
                        scf.cf.commander.send_stop_setpoint()
                    print("Unplugged")
                    now = time.time()
                    while now + 5 >= time.time():
                        scf.cf.commander.send_stop_setpoint()
                        time.sleep(0.1)
                    print("Resetting estimator")
                    reset_estimator(scf)
                queue.remove(action)
                with open("actions/"+ actions[action] + ".txt","r")as path_file:
                    path = path_file.read()
                sequence = eval(path)
                run_sequence(scf,sequence, "path_" + str(action+1))
                for i in range(0,50):
                    scf.cf.commander.send_position_setpoint(1.0,0.5,1.5,0)
                    time.sleep(0.1) 
            else:
                for i in range(0,20):
                    if is_flying:
                        scf.cf.commander.send_position_setpoint(0.5,0.5,0.15,0) 
                    time.sleep(0.1)
                print("Stopped")
                #if not charging:
                    #input("Validate drone is now charging")
                now = time.time()
                print("Plug the drone now!")
                while not charging:
                    scf.cf.commander.send_stop_setpoint()
                print("Charging")
                while now + 240 >= time.time():
                    scf.cf.commander.send_stop_setpoint()
                    time.sleep(0.1)
            decision.append(action)
            state_hist.append(state)
            #print(decision)
            invalid = 0
        for i in range(0,50):
            scf.cf.commander.send_position_setpoint(0.5,0.5,0.15,0)
            time.sleep(0.1)
        scf.cf.commander.send_stop_setpoint()
        print(decision)
        print(state_hist)

            