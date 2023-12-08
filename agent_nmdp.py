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
    print(batt)
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

def ask_input():
    T = threading.current_thread()
    T.input = -1
    T.input  = input("Enter 1 to continue or any input to wait")=="1"
    while not getattr(T,"finish", False):
        continue
    
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
    queue = [2,1,1,2]
    queue.reverse()
    actions = ["path_1", "path_2", "path_3"]
    uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
    print("Loading drivers")
    cflib.crtp.init_drivers(enable_debug_driver=False)
    print("Drivers loaded")
    invalid = 0
    
    
    while len(queue) > 0:
        input("Press enter to continue")
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            start_logging_state(scf)
            print("Resetting estimator")
            reset_estimator(scf)
            start_position_printing(scf)
            while len(queue) > 0:
                thread = threading.Thread(target=ask_input)
                thread.daemon = True
                thread.start()
                while getattr(thread,"input", -1) == -1:
                    scf.cf.commander.send_position_setpoint(1.0,0.5,1.5,0)
                    time.sleep(0.1)
                desicion = thread.input
                thread.finish = True
                thread.join()
                if desicion == 0:
                    break
                action = queue.pop()
                with open("actions/"+ actions[action] + ".txt","r")as path_file:
                    path = path_file.read()
                sequence = eval(path)
                run_sequence(scf, sequence, "path_" + str(action+1))
                for i in range(0,50):
                    scf.cf.commander.send_position_setpoint(1.0,0.5,1.5,0)
                    time.sleep(0.1) 
            for i in range(0,50):
                scf.cf.commander.send_position_setpoint(0.5,0.5,0.15,0)
                time.sleep(0.1)   
            scf.cf.commander.send_stop_setpoint() 
        print("Queue finished")
    print("Test Finished")
            