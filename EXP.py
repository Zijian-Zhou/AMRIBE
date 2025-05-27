import os
import sys
import time
from pypbc import *
import ABE as fibe05
import IDBE as ours
from charm.toolbox.pairinggroup import PairingGroup, GT
from ABE_Master.ABE.ac17 import AC17CPABE
from ABE_Master.ABE.bsw07 import BSW07
from ABE_Master.ABE.cgw15 import CGW15CPABE
from ABE_Master.ABE.waters11 import Waters11
import qabe as abe23
from draw import Draw
import random
import json
from Hash import Hash


class EXP:
    def __init__(self, params):
        self.times = params['times']
        self.attnums = params['attnums']
        self.datasize = params['datasize']
        self.src_data = None

    def generate_data(self):
        size = self.datasize

        with open("src.dat", "wb") as f:
            cnt = 0
            while cnt < size:
                data = random.randint(0, 0xffffffff)
                data = data.to_bytes(8, byteorder='big')
                f.write(data)
                cnt += 8

    def generate_policy(self, attrs=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
        ans = "("
        for i in range(int(len(attrs) / 2)):
            if i != 0:
                ans += " and "
            temp = "(%s OR %s)" % (attrs[i * 2], attrs[i * 2 + 1])
            ans += temp
        ans += ")"
        return ans

    def test_our(self):
        usernums = self.attnums

        ac = ours.AC()

        users = [ours.User(1) for _ in range(usernums)]

        for u in users:
            u.anonymous()
            for id in u.anon_id:
                t = Hash().HT(str(id))
                flag, sk = ac.RegisterUser(t)
                if not flag:
                    print(f"user {u} id {id} reg F!", sk)
                    u.sk.append(None)
                else:
                    u.sk.append(sk)
                u.pk.append(None)

        Gu = [[Hash().HT(u.anon_id[0]) for u in users]]

        setup_begin = time.time()
        res = ac.Negotiate(Gu)
        setup_end = time.time()

        _, gid, pks, V, setup_time = res
        gid = gid[0]

        for i in range(len(pks)):
            users[i].pk[0] = pks[i]
            users[i].V = V[i]

        enc_begin = time.time()
        enc_res = ac.Enc(os.path.join(os.getcwd(), "src.dat"), gid)
        enc_time = time.time() - enc_begin

        res = ac.model.Get(f"SELECT * FROM filemap WHERE fid = '{enc_res[2]}'")[0]

        dec_begin = time.time()
        users[0].Dec(res["loc"], users[0].sk[0], users[0].pk[0], enc_res[-1])
        dec_time = time.time() - dec_begin

        kenggen_time = setup_end - setup_begin - setup_time

        return setup_time, kenggen_time, enc_time, dec_time

    def test_ac17(self):
        attnums = self.attnums
        datasize = self.datasize
        pairing_group = PairingGroup('MNT224')
        cpabe = AC17CPABE(pairing_group, 2)

        return self.testbase(cpabe, attnums, datasize, pairing_group)

    def test_bsw07(self):
        attnums = self.attnums
        datasize = self.datasize
        pairing_group = PairingGroup('MNT224')
        cpabe = BSW07(pairing_group)

        return self.testbase(cpabe, attnums, datasize, pairing_group)

    def test_cgw15(self):
        attnums = self.attnums
        datasize = self.datasize
        pairing_group = PairingGroup('MNT224')
        cpabe = CGW15CPABE(pairing_group, 2, attnums)

        return self.testbase(cpabe, attnums, datasize, pairing_group)

    def test_waters11(self):
        attnums = self.attnums
        datasize = self.datasize
        pairing_group = PairingGroup('MNT224')
        cpabe = Waters11(pairing_group, attnums)

        return self.testbase(cpabe, attnums, datasize, pairing_group)

    def testbase(self, cpabe, attnums, datasize, pairing_group):
        setup_begin = time.time()
        (pk, msk) = cpabe.setup()
        setup_time = time.time() - setup_begin
        cpabe.debug = False

        attr_list = [str(i) for i in range(1, attnums, 2)]

        keygen_begin = time.time()
        key = cpabe.keygen(pk, msk, attr_list)
        keygen_time = time.time() - keygen_begin


        cnt = 0
        enc = []
        dec = []
        while cnt < datasize:
            msg = pairing_group.random(GT)

            enc_begin = time.time()
            policy_str = self.generate_policy([str(i) for i in range(1, attnums)])
            try:
                ctxt = cpabe.encrypt(pk, msg, policy_str)
            except Exception as e:
                print(policy_str, attnums)
                raise e
            enc_time = time.time() - enc_begin

            dec_begin = time.time()
            rec_msg = cpabe.decrypt(pk, ctxt, key)
            dec_time = time.time() - dec_begin

            cnt += len(str(msg).encode('utf-8'))
            enc.append(enc_time)
            dec.append(dec_time)

        return setup_time, keygen_time, sum(enc), sum(dec)

    def test_abe(self):
        attr_nums = self.attnums
        datasize = self.datasize

        setup_begin = time.time()
        ac = fibe05.ABE_AC(attr_nums)
        ac.setup(int(attr_nums / 2))
        setup_time = time.time() - setup_begin

        keygen_begin = time.time()
        D_i, w = ac.kengen()
        keygen_time = time.time() - keygen_begin

        user = fibe05.User(w, D_i, ac.g, ac.d)

        enc = []
        dec = []
        cnt = 0
        while cnt < datasize:

            message = Element.random(fibe05.pairing, Zr)

            enc_begin = time.time()
            w1, EM, E_i, ys = ac.enc(message, w)
            enc_time = time.time() - enc_begin

            dec_begin = time.time()
            plaint = user.dec(w1, EM, E_i, ac.x, ac.y)
            dec_time = time.time() - dec_begin

            enc.append(enc_time)
            dec.append(dec_time)
            cnt += len(str(message).encode('utf-8'))

        return setup_time, keygen_time, sum(enc), sum(dec)

    def run(self):
        self.generate_data()
        data = {
            "our": [],
            "abe05": [],
            "bsw07": [],
            "cgw15": [],
            "waters11": [],
            "ac17": [],
        }
        for i in range(self.times):
            data['our'].append(self.test_our())
            data['abe05'].append(self.test_abe())
            data['bsw07'].append(self.test_bsw07())
            data['cgw15'].append(self.test_cgw15())
            data['waters11'].append(self.test_waters11())
            data['ac17'].append(self.test_ac17())

        self.src_data = data

    def process_data(self):
        data = {
            "our": [],
            "abe05": [],
            "bsw07": [],
            "cgw15": [],
            "waters11": [],
            "ac17": [],
        }
        for key in self.src_data.keys():
            temp = [0] * 4
            for i in range(self.times):
                temp[0] += self.src_data[key][i][0]
                temp[1] += self.src_data[key][i][1]
                temp[2] += self.src_data[key][i][2]
                temp[3] += self.src_data[key][i][3]
            for i in range(4):
                temp[i] /= self.times

            data[key] = temp

        return data

def save_data(x, y):
    with open("save_data_%s.dat" % time.time(), "w") as f:
        f.write(json.dumps(x))
        f.write(json.dumps(y))


if __name__ == '__main__':
    #"""
    # EXP1
    x = [i for i in range(4, 101, 2)]
    y = {
            "our": [],
            "abe05": [],
            "bsw07": [],
            "cgw15": [],
            "waters11": [],
            "ac17": [],
        }
    for i in range(len(x)):
        print(i, x[i])
        exp = EXP({"times": 5, "attnums": x[i], "datasize": 512})
        exp.run()
        data = exp.process_data()
        for key in data.keys():
            y[key].append(data[key])

    save_data(x, y)
    Draw(x, y)
    """
    # EXP2
    x = [i * 512 for i in range(1, 11)]
    y = {
            "our": [],
            "abe05": [],
            "bsw07": [],
            "cgw15": [],
            "waters11": [],
            "ac17": [],
        }
    for i in range(len(x)):
        print(i, x[i])
        exp = EXP({"times": 5, "attnums": 10, "datasize": x[i]})
        exp.run()
        data = exp.process_data()
        for key in data.keys():
            y[key].append(data[key])

    save_data(x, y)
    Draw(x, y)
    """