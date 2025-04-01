import json

import matplotlib.pyplot as plt

def Draw(x, y):
    for key in y.keys():
        ty = [y[key][idx][0] for idx  in range(len(y[key]))]
        plt.plot(x, ty, label="%s" % key)
    plt.legend()

    plt.figure()
    for key in y.keys():
        ty = [y[key][idx][1] for idx in range(len(y[key]))]
        plt.plot(x, ty, label="%s" % key)
    plt.legend()

    plt.figure()
    for key in y.keys():
        ty = [y[key][idx][2] for idx in range(len(y[key]))]
        plt.plot(x, ty, label="%s" % key)
    plt.legend()

    plt.figure()
    for key in y.keys():
        ty = [y[key][idx][3] for idx in range(len(y[key]))]
        plt.plot(x, ty, label="%s" % key)
    plt.legend()

    plt.show()

def readdata():
    with open("save_data.dat", "r") as f:
        data = f.read()
    return data

if __name__ == "__main__":
    data = readdata()
    data = data[data.find("]")+1:]
    data = json.loads(data)
    print(data)
    Draw([i for i in range(4, 101, 2)], data)