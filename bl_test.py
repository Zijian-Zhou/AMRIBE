from pypbc import *

import Lagrange4ABE

# Initialize a set of parameters from a string 
# check the PBC documentation (http://crypto.stanford.edu/pbc/manual/) for more information
params = Parameters(
    "type a\n"
    "q 8780710799663312522437781984754049815806883199414208211028653399266475630880222957078625179422662221423155858769582317459277713367317481324925129998224791\n"
    "h 12016012264891146079388821366740534204802954401251311822919615131047207289359704531102844802183906537786776\n"
    "r 730750818665451621361119245571504901405976559617\n"
    "exp2 159\n"
    "exp1 107\n"
    "sign1 1\n"
    "sign0 1\n"
)

# Initialize the pairing
pairing = Pairing(params)

# show the order of the pairing
# print(pairing.order())

# Generate random elements
g1 = Element.random(pairing, G1)

mess = Element.random(pairing, Zr)
s = Element.random(pairing, Zr)
d = 10

x = [Element.from_int(pairing, 0)]
y = [Element.random(pairing, Zr)]

for i in range(d - 1):
    temp = Element.random(pairing, Zr)
    while temp in x:
        temp = Element.random(pairing, Zr)
    x.append(temp)
    y.append(Element.random(pairing, Zr))

w = [Element.random(pairing, Zr) for _ in range(d)]
q_i = [Lagrange4ABE.langrange(x, y, wi, Element, pairing) for wi in w]

D_i = []
for i in range(d):
    D_i.append(g1 ** (q_i[i] / w[i]))

EM = mess * pairing.apply(g1, g1) ** (s * y[0])

E_i = [g1 ** (s * wi) for wi in w]

res = Element.from_int(pairing, 1)
ans = Element.from_int(pairing, 0)
for i in range(d):
    temp = Lagrange4ABE.coe(w, i, Element.from_int(pairing, 0), Element, pairing)
    res *= pairing.apply(D_i[i], E_i[i]) ** temp


print(EM)
print(res * mess)