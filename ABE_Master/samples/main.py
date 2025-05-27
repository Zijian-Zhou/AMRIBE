'''
:Authors:         Shashank Agrawal
:Date:            5/2016
'''


from charm.toolbox.pairinggroup import PairingGroup, GT
from ABE_Master.ABE.ac17 import AC17CPABE
from ABE_Master.ABE.bsw07 import BSW07
from ABE_Master.ABE.cgw15 import CGW15CPABE
from ABE_Master.ABE.waters11 import Waters11

def main():
    # instantiate a bilinear pairing map
    pairing_group = PairingGroup('MNT224')

    # AC17 CP-ABE under DLIN (2-linear)
    #cpabe = AC17CPABE(pairing_group, 2)

    #cpabe = BSW07(pairing_group)

    #cpabe = CGW15CPABE(pairing_group, 2, 4)

    cpabe = Waters11(pairing_group, 4)

    # run the set up
    (pk, msk) = cpabe.setup()
    cpabe.debug = True

    # generate a key
    attr_list = ['ONE', 'TWO', 'THREE']

    #CGW15 & Waters 11
    #attr_list = [str(i) for i in range(1, 5)]
    attr_list = [str(i) for i in range(1, 5)]

    key = cpabe.keygen(pk, msk, attr_list)

    # choose a random message
    msg = pairing_group.random(GT)

    print("MESSAGE: ", msg)
    print("BETY_LENG: ", len(str(msg).encode("utf-8")))


    # generate a ciphertext
    policy_str = '((ONE and THREE) and (TWO OR FOUR))'
    #CGW15 & waters 11
    policy_str = '((1 and 3) and (2 OR 4))'


    ctxt = cpabe.encrypt(pk, msg, policy_str)

    # decryption
    rec_msg = cpabe.decrypt(pk, ctxt, key)
    print(key)
    if debug:
        if rec_msg == msg:
            print ("Successful decryption.")
        else:
            print ("Decryption failed.")


if __name__ == "__main__":
    debug = True
    main()
