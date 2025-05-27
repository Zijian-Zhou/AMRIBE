from pypbc import *
import random
import Lagrange4ABE

#"""
p = 8780710799663312522437781984754049815806883199414208211028653399266475630880222957078625179422662221423155858769582317459277713367317481324925129998224791
h = 12016012264891146079388821366740534204802954401251311822919615131047207289359704531102844802183906537786776
r = 730750818665451621361119245571504901405976559617
exp2 = 159
exp1 = 107
parameters = "type a\n" + "q %s\nh %s\nr %s\nexp2 %s\nexp1 %s\nsign1 1\nsign0 1\n" % (p, h, r, exp2, exp1)
params = Parameters(parameters)
"""
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
"""
pairing = Pairing(params)

class ABE_AC:
    def __init__(self, u):
        self.y = None
        self.x = None
        self.s = None
        self.d = None
        self.universi_size = u
        self.g = None
        self.master_key = None
        self.Public_Params = None

    def  setup(self, d):
        self.d = d
        self.universi_size = 1000
        self.g = Element.random(pairing, G1)
        self.master_key = [Element.random(pairing, Zr) for _ in range(self.universi_size)]
        self.Public_Params = [self.g ** item for item in self.master_key]
        self.Public_Params[-1] = pairing.apply(self.g, self.g) ** (self.master_key[-1])

    def kengen(self):
        x = [Element.from_int(pairing, 0)]
        y = [self.master_key[-1]]

        for i in range(self.d - 1):
            temp = Element.random(pairing, Zr)
            while temp in x:
                temp = Element.random(pairing, Zr)
            x.append(temp)
            y.append(Element.random(pairing, Zr))

        #q = lagrange(x, y) The scipy lib can not use for Elements calculation
        q = Lagrange4ABE.langrange

        w = [self.master_key[random.randint(0, len(self.master_key)) % len(self.master_key)] for _ in range(self.d + 5)]
        q_i = [q(x, y, wi, Element, pairing) for wi in w]
        D_i = []
        for i in range(len(w)):
            D_i.append(self.g ** (q_i[i] / w[i]))

        self.x = x
        self.y = y

        return D_i, w

    def enc(self, Mess, w):
        s = Element.random(pairing, Zr)
        self.s = s

        w1 = []
        for _ in range(self.d):
            temp = w[random.randint(0, len(w) - 1)]
            while temp in w1:
                temp = w[random.randint(0, len(w) - 1)]
            w1.append(temp)

        for i in range(random.randint(0, len(self.master_key) - self.d -1)):
            temp = self.master_key[random.randint(0, len(self.master_key)) % len(self.master_key)]
            while temp in w1:
                temp = self.master_key[random.randint(0, len(self.master_key)) % len(self.master_key)]
            w1.append(temp)

        E_i = [(self.g ** item) ** s for item in w1]

        EM = Mess * (self.Public_Params[-1] ** s)

        return w1, EM, E_i, (self.Public_Params[-1] ** s)


class User:
    def __init__(self, attrs, sk, g, d):
        self.attrs = attrs
        self.sk = sk
        self.g = g
        self.d = d

    def sort_m(self, matched):
        for i in range(len(matched)):
            for j in range(i):
                if matched[i][1] < matched[j][1]:
                    matched[i], matched[j] = matched[j], matched[i]
        return matched

    def dec(self, w1, EM, E_i, x, y):
        matched = []
        S = []
        for attr in self.attrs:
            if attr in w1:
                matched.append([self.attrs.index(attr), w1.index(attr)])

                d_i = Lagrange4ABE.langrange(x, y, attr, Element, pairing)
                Dd_i = self.g ** (d_i / attr)
                if Dd_i != self.sk[matched[-1][0]]:
                    print("error")

        matched = self.sort_m(matched)
        for item in matched:
            S.append(self.attrs[item[0]])

        if len(matched) < self.d:
            raise Exception("UN-decrypt-able!")

        res = Element.from_int(pairing, 1)
        for i in range(self.d):
            yi = pairing.apply(self.sk[matched[i][0]], E_i[matched[i][1]])
            l = Lagrange4ABE.coe(S[:self.d], i, Element.from_int(pairing, 0), Element, pairing)
            res *= (yi) ** l

        return EM / res



if __name__ == '__main__':

    cnt = 0
    #times = 10000
    times = 10
    for _ in range(times):
        ac = ABE_AC(100)
        ac.setup(10)

        D_i, w = ac.kengen()

        user = User(w, D_i, ac.g, ac.d)

        message = Element.random(pairing, Zr)

        w1, EM, E_i, ys = ac.enc(message, w)

        plaint = user.dec(w1, EM, E_i, ac.x, ac.y)

        m = EM / ys
        if int(m[0]) == int(plaint[0]) and int(m[1]) == int(plaint[1]):
            cnt += 1
        else:
            print("error")
            #print(w1, EM, E_i, ys)
            #print(w, plaint, m)

    #print("ACC: ", cnt / times)