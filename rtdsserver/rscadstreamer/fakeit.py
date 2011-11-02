import json
import random
import socket
import sys
import time

RNG = random.SystemRandom()
def getmeasure(v,s):
    return "%6f" % (RNG.gauss(v,s),)

def getnonperturb():
    return {'bus_1': {'v': getmeasure(0,0), 't': 0.0, 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_2': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_3': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_4': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_5': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_6': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_7': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_8': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'bus_9': {'v': getmeasure(0,0), 't': getmeasure(0,0), 'p':getmeasure(0,0), 'q': getmeasure(0,0)},
            'gen_1': {'p': getmeasure(0,0), 'q': getmeasure(0,0)},
            'gen_2': {'p': getmeasure(0,0), 'q': getmeasure(0,0)},
            'gen_3': {'p': getmeasure(0,0), 'q': getmeasure(0,0)},
            'load_5': {'p': getmeasure(0,0), 'q': getmeasure(0,0)},
            'load_6': {'p': getmeasure(0,0), 'q': getmeasure(0,0)},
            'load_8': {'p': getmeasure(0,0), 'q': getmeasure(0,0)},
            'pflow_1':{'p':getmeasure(0,0)},
            'pflow_2':{'p':getmeasure(0,0)},
            'pflow_3':{'p':getmeasure(0,0)},
            'pflow_4':{'p':getmeasure(0,0)},
            'pflow_5':{'p':getmeasure(0,0)},
            'pflow_6':{'p':getmeasure(0,0)},
            'pflow_7':{'p':getmeasure(0,0)},
            'pflow_8':{'p':getmeasure(0,0)},
            'pflow_9':{'p':getmeasure(0,0)}
           }

def getperturb():
    return {'bus_1': {'v': getmeasure(1.0,1.0), 't': 0.0, 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_2': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_3': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_4': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_5': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_6': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_7': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_8': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'bus_9': {'v': getmeasure(1.0,1.0), 't': getmeasure(1.0,1.0), 'p':getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'gen_1': {'p': getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'gen_2': {'p': getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'gen_3': {'p': getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'load_5': {'p': getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'load_6': {'p': getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'load_8': {'p': getmeasure(1.0,1.0), 'q': getmeasure(1.0,1.0)},
            'pflow_1':{'p':getmeasure(1.0,1.0)},
            'pflow_2':{'p':getmeasure(1.0,1.0)},
            'pflow_3':{'p':getmeasure(1.0,1.0)},
            'pflow_4':{'p':getmeasure(1.0,1.0)},
            'pflow_5':{'p':getmeasure(1.0,1.0)},
            'pflow_6':{'p':getmeasure(1.0,1.0)},
            'pflow_7':{'p':getmeasure(1.0,1.0)},
            'pflow_8':{'p':getmeasure(1.0,1.0)},
            'pflow_9':{'p':getmeasure(1.0,1.0)}
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
            d = json.dumps(get())
            n = s.send(d)
            print "sent:", len(d),"of",n,"bytes"
            time.sleep(1)
    except KeyboardInterrupt, e:
        s.close()

if __name__ == '__main__':
    main()

