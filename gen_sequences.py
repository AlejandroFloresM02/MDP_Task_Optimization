import numpy as np
import time
import os

path_name = "path_1"

file_name = "data/"+ path_name + ".txt"
output = "data/refined_data/"+ path_name + ".csv"

batt_high = 3.6 #Lower limit
batt_mid = 3.40 #Lower limit

batt_low = 3.32 #Lower limit
batt_crit = 3.32 #Upper limit
#Values assigned through observation

def get_state(voltage):
    if voltage > batt_high:
        return "4"
    elif voltage > batt_mid:
        return "3"
    elif voltage > batt_low:
        return "2"
    elif voltage > 0:
        return "1"
    else:
        return "-1"

with open(file_name, "r") as file:
    with open(output, "wb+") as out_file:
        line = file.readline()
        prev_line = "\n"
        while line != "":
            values = line.split(" ")
            if prev_line == "\n":
                out_file.write(bytes(get_state(float(values[0]))+ ",", "utf8"))
                out_file.write(bytes(get_state(float(values[1]))+ ",", "utf8"))
            elif line != "\n":
                out_file.write(bytes(get_state(float(values[1]))+ ",", "utf8"))
            else:
                out_file.seek(-1,2)
                out_file.truncate()
                out_file.write(b"\n")
            prev_line = line
            line = file.readline()
        out_file.seek(-1,2)
        out_file.truncate()

