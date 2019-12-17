from time import sleep

import sys, select



_wait_strs = '\|/-\|/-'

class WaitInput:
    def __init__(self,text,wait_time=5,update_interval=1):
        self.text = text
        self.wait_time=wait_time


    def start(self):
        resttime = self.wait_time
        while resttime>0:
            print(f"You have {resttime} seconds to answer!")
            i, o, e = select.select( [sys.stdin], [], [], 2 )

if (i):
    print("You said", sys.stdin.readline().strip())
else:
    print("You said nothing!")
