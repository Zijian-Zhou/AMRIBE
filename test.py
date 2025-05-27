import json
import time

from scipy.interpolate import lagrange
import random
import copy
import matplotlib.pyplot as plt


def newton_method(x0, v, f, fp, epsilon=1e-12, max_iter=1000):
    x_n = x0
    for _ in range(max_iter):
        f_xn = float(f(x_n)) - v
        f_prime_xn = float(fp(x_n))
        if abs(f_xn) < epsilon:
            return x_n
        x_n = x_n - f_xn / f_prime_xn
    return x_n
    #raise ValueError("未能在最大迭代次数内收敛")

def draw(x, y, x1, y1):
    plt.plot(x, y, label='original', color='blue')
    plt.plot(x1, y1, label='attack', color='red')
    plt.legend()
    plt.show()

deg = 15
step = 1000

x1 = [random.randint(1,1000) for i in range(deg)]
y1 = [random.uniform(-1000,1000) for i in range(deg)]
x1.sort()

f = lagrange(x1, y1)
fp = copy.deepcopy(f)
for i in range(deg):
    if i == deg - 1:
        fp[i] = 0
    else:
        fp[i] = f[i+1] * (i+1)




#x2 = [random.randint(1,1000) for i in range(deg)]
x2 = [random.uniform(-1000,1000) for i in range(deg)]
y2 = []
for xi in x2:
    y2.append(f(xi))

print(x2)


es_sum = []

#for sstep in range(1, step, 10):
for sstep in [i * 0.001 for i in range(1000)]:
    x3 = [i + random.uniform(-sstep,sstep) for i in x2]
    x4 = []
    es = []
    for i in range(deg):
        value = newton_method(x3[i], y2[i], f, fp)
        x4.append(value)
        es.append(abs(value - x2[i]))
    es_sum.append(sum(es))

"""
plt.plot([sstep for sstep in range(1, step, 10) ], es_sum)
with open("step-%s-%s-%s" % (step, time.time(), deg), "w") as f:
    f.write(json.dumps([sstep for sstep in range(1, step, 10)]))
    f.write("\n")
    f.write(json.dumps(es_sum))
plt.show()
"""

plt.plot([i * 0.001 for i in range(1000)], es_sum)
with open("step-%s-%s-%s" % (step, time.time(), deg), "w") as f:
    f.write(json.dumps([i * 0.001 for i in range(1000)]))
    f.write("\n")
    f.write(json.dumps(es_sum))
plt.show()


"""
c2 = lagrange(x4, y2)

print(f)
print(c2)

for i in range(deg):
    temp = random.uniform(-1000, 1000)
    print(temp, f(temp) - c2(temp))
"""

"""
xx1 = [random.uniform(-1000,1000) for i in range(1000)]

yy1 = []
for xi in xx1:
    yy1.append(f(xi))

yy2 = []
for xi in xx1:
    yy2.append(c2(xi))

draw(xx1, yy1, xx1, yy2)

xx1.sort()
yy1 = []
for xi in xx1:
    yy1.append(f(xi))

yy2 = []
for xi in xx1:
    yy2.append(c2(xi))

draw(xx1, yy1, xx1, yy2)

plt.plot([i for i in range(len(es))], es)
plt.show()

"""


