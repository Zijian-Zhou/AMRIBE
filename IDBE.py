import hashlib
import json
import os.path
import random
import string
import struct
import time
from math import floor

import numpy
import numpy as np
from numpy import dtype

from Hash import Hash
from BloomFilter import BloomFilter
from Lagrange import Poly, RCPoly, RePoly

import DBModel


class AC:
    def __init__(self):
        self.model = DBModel.AC_Model()
        self.conf = self._loadconf()
        self.base_degree = self.conf["Public-Parameters"]["degree"]
        self.bloom = None
        self.gbloom = None
        self._SetBloom()

    def _SetBloom(self):
        conf = self.conf["AC"]["Bloom"]
        user_nums = self.model.Counter("user")
        self.bloom = BloomFilter(conf["size"] + user_nums, conf["hash-count"])
        gnums = self.model.Counter("user_group")
        self.gbloom = BloomFilter(conf["size"] + gnums, conf["hash-count"])

        users = self.model.Get("SELECT sk FROM user")
        ug = self.model.Get("SELECT curves FROM user_group")
        for user in users:
            self.bloom.add(user["sk"])
        for g in ug:
            self.gbloom.add(g["curves"])

    def _loadconf(self):
        conf = None
        with open("conf.json", "r") as f:
            conf = json.loads(f.read())
        return conf

    def setup(self, Nu, n):
        gid = []
        for i in range(len(Nu)):
            setup_begin = time.time()
            poly = Poly(n)
            coe = poly.GetCoe()
            while self.gbloom.check(json.dumps(coe)):
                poly._SetCurve__()
                coe = poly.GetCoe()
            setup_time = time.time() - setup_begin
            pk = []
            V = []
            #print("oricoe: ", sum(poly.curve.coefficients.tolist()))
            for u in Nu[i]:
                vuk = []
                sk = self.model.Get("SELECT sk FROM user WHERE name='%s'" % u)
                if len(sk) == 0:
                    return False, "user %s not found" % u
                sk = json.loads(sk[0]["sk"])
                pk_k = [poly.curve(sk_i) for sk_i in sk]
                pk.append(pk_k)
                cu = RePoly(self.base_degree, sk, pk_k)
                for j in range(self.base_degree):
                    vuk.append(poly.curve[j] - cu.curve[j])
                vuk = numpy.array(vuk, dtype=np.float64)
                V.append(vuk)

            self.model.Insert("user_group", (
                ("group_users", "curves", "version", "pk"),
                (json.dumps(Nu[i]), json.dumps([coe]), 1, json.dumps(pk)),
            ))
            gid.append(self.model.Get(
                "SELECT gid from user_group WHERE group_users = '%s'"
                % json.dumps(Nu[i])
            )[0]["gid"])
            self.gbloom.add(json.dumps(coe))
        return True, gid, pk, V, setup_time

    # KeyGen
    def RegisterUser(self, username):
        ex = self.model.Get("SELECT * FROM user WHERE name='%s'" % username)
        if len(ex) != 0:
            return False, "user existed"

        try:
            sk = [random.uniform(-1000, 1000) for _ in range(self.base_degree + 1)]
            while self.bloom.check(json.dumps(sk)):
                sk = [random.uniform(-1000, 1000) for _ in range(self.base_degree + 1)]
            self.bloom.add(json.dumps(sk))
            self.model.Insert("user", (
                ("sk", "name"), (json.dumps(sk), username)
            ))
            return True, sk
        except Exception as e:
            return False, e

    def Negotiate(self, ug):
        result = self.model.Get("SELECT * FROM user_group")
        for tug in ug:
            jug = json.dumps(tug)
            for res in result:
                if jug == res["group_users"]:
                    return 0, res["gid"]
            return self.setup(ug, self.base_degree)

    def Enc(self, filepath, gid):
        start_time = time.time()
        fhash = Hash().HF(filepath)
        #print("src hash: ", fhash)

        records = self.model.Get(
            "SELECT curves, version FROM user_group WHERE gid='%s'" % gid
        )
        if len(records) == 0:
            return False, "non-exist group"

        try:
            records = records[0]
            records["curves"] = json.loads(records["curves"])
            coe = None
            for ver in range(records["version"]):
                if ver == 0:
                    coe = records["curves"][ver]
                else:
                    for i in range(len(coe)):
                        coe[i] += records["curves"][ver][i]

            poly = RCPoly(self.base_degree, coe)

            s = random.randint(-1000, 1000)
            # \sum{c_i * \sigma}
            sy = floor(poly.curve(s))
            #print("ENC-s-sy: ", s, sy)
            # \delta^* = H(H(F) + \sum{c_i * \sigma})
            fhash_ = Hash().HT(str(fhash) + str(sy))

            #print("ENCC", sum(poly.curve.coefficients.tolist()))
            #print("ENC-*", fhash_)

            key = "0"
            for i in range(32):
                key = Hash().HT(
                    str(int(key, 16) + poly.curve(int(fhash_[i * 2: (i + 1) * 2], 16)))
                )
            key = str(int(key, 16))

            #print(key)
            bs = struct.pack('q', s)
            with open(filepath, "rb") as f:
                with open("esrc/%s.dat" % fhash_, "wb") as ec:
                    ec.write(fhash_.encode("utf-8"))
                    ec.write(bs)
                    for chunk in iter(lambda: f.read(32), b""):
                        chunk = bytes(
                            [b1 ^ b2 for b1, b2 in zip(key.encode('utf-8'), chunk)]
                        )
                        ec.write(chunk)

            pi = Hash().HF("esrc/%s.dat" % fhash_)
            pi = Hash().HT(str(pi) + str(fhash_) + str(s))

            self.model.Insert("filemap",
                              (("fid", "loc", "s"), (fhash_, "esrc/%s.dat" % fhash_, struct.unpack('q', bs)[0]))
                              )
            return True, time.time() - start_time, fhash_, pi
        except Exception as e:
            return False, e


class User:
    def __init__(self, id_nums):
        self.base_degree = None
        self._load_conf()
        self.idn = id_nums
        self.anon_id = []
        self.sk = []
        self.pk = []
        self.V = []

    def _load_conf(self):
        conf = None
        with open("conf.json", "r") as f:
            conf = json.loads(f.read())
            self.base_degree = conf["Public-Parameters"]["degree"]

    def anonymous(self):
        for i in range(self.idn):
            visible_chars = string.ascii_letters + string.digits + string.punctuation
            selected_chars = ''.join(random.choices(visible_chars, k=50))
            self.anon_id.append(selected_chars)

    def Dec(self, path, identity, pk, pi):
        #try:
        poly = RePoly(self.base_degree, identity, pk)
        #print("DECC0", sum(poly.curve.coefficients.tolist()))
        for i in range(self.base_degree):
            poly.curve[i] += self.V[i]
        #print("DECC1", sum(poly.curve.coefficients.tolist()))
        s = None
        fhash_ = None
        with open(path, "rb") as f:
            fhash_ = f.read(64).decode("utf-8")
            s = f.read(8)
            #print("DEC-*", fhash_)
            key = "0"
            for i in range(32):
                key = Hash().HT(
                    str(int(key, 16) +
                        poly.curve(int(fhash_[i * 2: (i + 1) * 2], 16))
                        )
                )
            key = str(int(key, 16))
            #print(key)
            with open("fsrc/decode.dat", "wb") as de:
                for chunk in iter(lambda: f.read(32), b""):
                    chunk = bytes(
                        [b1 ^ b2 for b1, b2 in zip(key.encode('utf-8'), chunk)]
                    )
                    de.write(chunk)

        s = struct.unpack('q', s)[0]
        sy = floor(poly.curve(s))
        #print("DEC-s-sy: ", s, sy)

        pi_ = Hash().HT(str(Hash().HF(path)) + str(fhash_) + str(s))

        defhash = str(Hash().HF("fsrc/decode.dat"))
        #print("DEC_Fhash: ", defhash)

        defhash = Hash().HT(str(defhash) + str(sy))
        if defhash == fhash_ and pi_ == pi:
            return True
        else:
            #print(defhash, fhash_)
            return False, "Hash Error"
        #except Exception as e:
        #    return False, e









if __name__ == '__main__':
    cnt  = 0
    tries = 10
    for i in range(tries):
        ac = AC()
        u1 = User(3)
        u2 = User(3)
        u3 = User(3)

        users = [u1, u2, u3]
        for u in users:
            u.anonymous()
            for id in u.anon_id:
                t = Hash().HT(str(id))
                flag, sk = ac.RegisterUser(t)
                if not flag:
                    #print(f"user {u} id {id} reg F!", sk)
                    u.sk.append(None)
                else:
                    u.sk.append(sk)
                u.pk.append(None)

        Gu = [[Hash().HT(u1.anon_id[0]),Hash().HT(u2.anon_id[1]),Hash().HT(u3.anon_id[2])]]

        res = ac.Negotiate(Gu)
        _, gid, pks, V, __ = res
        gid = gid[0]

        #pks = json.loads(ac.model.Get(f"SELECT pk FROM user_group WHERE gid={gid}")[0]['pk'])
        for i in range(len(pks)):
            if i == 0:
                u1.pk[0] = pks[i]
                u1.V = V[i]
            elif i == 1:
                u2.pk[1] = pks[i]
                u2.V = V[i]
            else:
                u3.pk[2] = pks[i]
                u3.V = V[i]

        #enc_res = ac.Enc(os.path.join(os.getcwd(), "e_src.txt"), gid)
        enc_res = ac.Enc(os.path.join(os.getcwd(), "test.jpg"), gid)

        #print(enc_res)

        if not enc_res[0]:
            #print("ENC ERROR, ", enc_res[1])
            exit(1)

        res = ac.model.Get(f"SELECT * FROM filemap WHERE fid = '{enc_res[2]}'")[0]
        res = u1.Dec(res["loc"], u1.sk[0], u1.pk[0], enc_res[-1])

        #print(res)
        if res == True:
            cnt += 1
    print("ACC: ", cnt / tries)