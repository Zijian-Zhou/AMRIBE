def langrange(x, y, index, E, p):
    res = E.from_int(p, 0)
    for i in range(len(x)):
        l_x = E.from_int(p, 1)
        for j in range(len(x)):
            if i != j:
                l_x *= (index - x[j]) / (x[i] - x[j])
        res += y[i] * l_x
    return res

def coe(S, i, index, E, p):
    res = E.from_int(p, 1)
    for j in range(len(S)):
        if i != j:
            a = index - S[j]
            b = S[i] - S[j]
            res *=  (a / b)
    return res