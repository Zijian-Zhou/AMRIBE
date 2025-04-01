from scipy.interpolate import lagrange
import random
import numpy as np

class Poly:
    def __init__(self, dim):
        self.dim = dim + 1
        self.curve = None
        self._SetCurve__()

    # generate a random curve
    def RCurve(self, dim):
        x = []
        y = []

        for i in range(dim):
            x.append(random.uniform(-10 ** 3, 10 ** 3))
            y.append(random.uniform(-10 ** 3, 10 ** 3))

        curve = lagrange(x, y)
        return curve

    def _SetCurve__(self):
        self.curve = self.RCurve(self.dim)

    # get $dim points from curve
    def GetPoints(self):
        x = []
        y = []

        for i in range(self.dim):
            px = random.randint(-10 ** 5, 10 ** 5)
            x.append(px)
            y.append(self.curve(px))

        return x, y

    # get values in a particular curve for x
    # sc (self.curve)   Ture: use self curve
    #                   False: use custom curve from param: curve
    def Value(self, x, sc=True, curve=None):
        y = []

        if sc:
            for i in x:
                y.append(self.curve(i))
        else:
            for i in x:
                y.append(curve(i))
        return y

    # Aggregate all curves into one curve
    def CurveAgg(self, curves):
        curve = curves[0]
        for cur in curves[1:]:
            curve = np.polyadd(curve, cur)
        return curve

    def GetCoe(self):
        return self.curve.coefficients.tolist()



class RePoly(Poly):
    def __init__(self, dim, initx, inity):
        self.dim = dim + 1
        self.initx = np.array(initx, dtype=np.float64)
        self.inity = np.array(inity, dtype=np.float64)
        self._SetCurve__()

    def _SetCurve__(self):
        self.curve = lagrange(self.initx, self.inity)


class RCPoly(Poly):
    def __init__(self, dim, coe):
        self.dim = dim + 1
        self.coe = coe
        self._SetCurve__()

    def _SetCurve__(self):
        self.curve = np.poly1d(self.coe)





if __name__ == "__main__":
    p = Poly(50)
    print(p.curve)
    x, y = p.GetPoints()


    p2 = RePoly(50, x, y)
    print(p2.curve)

    print(p.CurveAgg([p.curve, p2.curve]))