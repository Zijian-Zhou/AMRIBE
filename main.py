from scipy.interpolate import lagrange
from Lagrange import *
import random

x1 = [random.randint(1,1000) for i in range(100)]
x2 = [random.randint(1,1000) for i in range(100)]

x1.sort()
x2.sort()

print(x1, x2)

y1 = [random.uniform(-1000,1000) for i in range(100)]
p1 = lagrange(x1, y1)

y2 = []
y3 = []

for i in range(100):
    t2 = p1(x2[i])
    y2.append(t2)
    y3.append(y1[i] + t2)

c2 = lagrange(x1, y1)
c3 = lagrange(x2, y3)

for i in range(100):
    print(i, p1[i] / y1[i], c2[i] / y1[i], c3[i] / y3[i])

print(c3)
for i in range(100):
    print(c3[i])


"""
c2 = lagrange(x1, y3)
c3 = lagrange(x2, y3)



for i in range(10):
    print(p1.curve[i], c2[i], c3[i])


print(y1)
print(y2)
print(y3)
"""
