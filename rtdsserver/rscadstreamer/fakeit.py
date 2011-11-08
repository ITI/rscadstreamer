import json
import random
import socket
import sys
import time

RNG = random.SystemRandom()
def getmeasure(v,s):
    s = s * v
    res = "%6f" % (RNG.gauss(v,s),)
    return res[:6]

def getnonperturb():
    return {'bus_1': {'v': getmeasure(1.04,0.007), 't': 0.0, 'p':getmeasure(0.7164,0.007), 'q': getmeasure(27.91,0.007)},
            'bus_2': {'v': getmeasure(1.025,0.007), 't': getmeasure(9.3489,0.007), 'p':getmeasure(163.0,0.007), 'q': getmeasure(4.90,0.007)},
            'bus_3': {'v': getmeasure(1.0250,0.007), 't': getmeasure(5.1401,0.007), 'p':getmeasure(85.0,0.007), 'q': getmeasure(-11.44,0.007)},
            'bus_4': {'v': getmeasure(1.0253,0.007), 't': getmeasure(-2.2177,0.007), 'p':getmeasure(0,0.007), 'q': getmeasure(0.0,0.007)},
            'bus_5': {'v': getmeasure(0.9997,0.007), 't': getmeasure(-3.6809,0.007), 'p':getmeasure(-125.0,0.007), 'q': getmeasure(-50.0,0.007)},
            'bus_6': {'v': getmeasure(1.0123,0.007), 't': getmeasure(-3.5668,0.007), 'p':getmeasure(-90.0,0.007), 'q': getmeasure(-30.0,0.007)},
            'bus_7': {'v': getmeasure(1.0268,0.007), 't': getmeasure(3.7944,0.007), 'p':getmeasure(0,0.007), 'q': getmeasure(0.0,0.007)},
            'bus_8': {'v': getmeasure(1.0173,0.007), 't': getmeasure(1.3355,0.007), 'p':getmeasure(-100,0.007), 'q': getmeasure(-35.0,0.007)},
            'bus_9': {'v': getmeasure(1.0327,0.007), 't': getmeasure(2.4430,0.007), 'p':getmeasure(0,0.007), 'q': getmeasure(0.0,0.007)},
            'gen_1': {'p': getmeasure(71.64,0.007), 'q': getmeasure(27.91,0.007)},
            'gen_2': {'p': getmeasure(163.0,0.007), 'q': getmeasure(4.90,0.007)},
            'gen_3': {'p': getmeasure(85.0,0.007), 'q': getmeasure(-11.44,0.007)},
            'load_5': {'p': getmeasure(-125.0,0.007), 'q': getmeasure(-50.0,0.007)},
            'load_6': {'p': getmeasure(-90.0,0.007), 'q': getmeasure(-30.0,0.007)},
            'load_8': {'p': getmeasure(-100.0,0.007), 'q': getmeasure(-35.0,0.007)},
            'pflow_1': {'p':getmeasure((0.7164)*100.0,0.007)},
            'pflow_2': {'p':getmeasure((1.6300)*100.0,0.007)},
            'pflow_3': {'p':getmeasure((0.8500)*100.0,0.007)},
            'pflow_4': {'p':getmeasure((0.4330)*100.0,0.007)},
            'pflow_5': {'p':getmeasure((0.2834)*100.0,0.007)},
            'pflow_6': {'p':getmeasure((-0.8198)*100.0,0.007)},
            'pflow_7': {'p':getmeasure((-0.6181)*100.0,0.007)},
            'pflow_8': {'p':getmeasure((0.7885)*100.0,0.007)},
            'pflow_9': {'p':getmeasure((-0.2166)*100.0,0.007)}
           }

def getperturb():
    return {'bus_1': {'v': getmeasure(1.0,0.007), 't': 0.0, 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'bus_2': {'v': getmeasure(1.0,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'bus_3': {'v': getmeasure(1.0,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'bus_4': {'v': getmeasure(1.0253 + 0.0010,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'bus_5': {'v': getmeasure(0.9997 + -0.0078,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'bus_6': {'v': getmeasure(1.0123 + 0.0007,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'bus_7': {'v': getmeasure(1.0268 + -0.0018,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(0.0,0.007)},
            'bus_8': {'v': getmeasure(1.0173 + -0.0013,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'bus_9': {'v': getmeasure(1.0327 + -0.0005,0.007), 't': getmeasure(1.0,0.007), 'p':getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'gen_1': {'p': getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'gen_2': {'p': getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'gen_3': {'p': getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'load_5': {'p': getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'load_6': {'p': getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'load_8': {'p': getmeasure(1.0,0.007), 'q': getmeasure(1.0,0.007)},
            'pflow_1': {'p':getmeasure((0.7164 + 0.0003 )*100.0,0.007)},
            'pflow_2': {'p':getmeasure((1.6300 + -0.0000)*100.0,0.007)},
            'pflow_3': {'p':getmeasure((0.8500 + 0.0000 )*100.0,0.007)},
            'pflow_4': {'p':getmeasure((0.4330 + -0.0391)*100.0,0.007)},
            'pflow_5': {'p':getmeasure((0.2834 + 0.0394 )*100.0,0.007)},
            'pflow_6': {'p':getmeasure((-0.8198 + -0.0387)*100.0,0.007)},
            'pflow_7': {'p':getmeasure((-0.6181 + 0.0390 )*100.0,0.007)},
            'pflow_8': {'p':getmeasure((0.7885 + -0.0411)*100.0,0.007)},
            'pflow_9': {'p':getmeasure((-0.2166 + -0.0406)*100.0,0.007)}
           }

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sys.argv[1], int(sys.argv[2])))
    s.setblocking(False)
    get = getnonperturb
    try:
        while True:
            try:
                data = s.recv(1024)
                print "got data:", data
                if data.strip() == "kick_the_system":
                    get = getperturb
                else:
                    get = getnonperturb
            except:
                pass
            d = json.dumps(get()) + "\n"
            n = s.send(d)
            print "sent:", len(d),"of",n,"bytes"
            time.sleep(1)
    except KeyboardInterrupt, e:
        s.close()

if __name__ == '__main__':
    main()

