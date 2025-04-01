import time
import random
from pypbc import *
import numpy as np

def test_operations():
    # 1. Initialize bilinear pairing parameters
    # Generate pairing parameters of type A
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
    pairing = Pairing(params)
    t = []

    # 4. Randomly generate group base points
    g1 = Element.random(pairing, G1)
    g2 = Element.random(pairing, G1)
    g_hat = Element.random(pairing, G1)  # Base point in the isomorphic group
    h = Element.random(pairing, GT)  # An element in GT

    # 5. Generate a random scalar (within the group order)
    scalar = random.randint(1, pairing.order() - 1)

    # 6. Test scalar multiplication in G and G_hat
    #print("Testing scalar multiplication (G, G_hat):")
    start_time = time.time()
    result_g = g1 ** scalar  # Scalar multiplication in G
    end_time = time.time()
    #print(f"Scalar multiplication in G took: {(end_time - start_time) * 1000:.3f} ms")
    t.append((end_time - start_time) * 1000)

    start_time = time.time()
    result_g_hat = g_hat ** scalar  # Scalar multiplication in G_hat
    end_time = time.time()
    #print(f"Scalar multiplication in G_hat took: {(end_time - start_time) * 1000:.3f} ms")
    t.append((end_time - start_time) * 1000)

    start_time = time.time()
    result_g_t = h ** scalar  # Scalar multiplication in G_hat
    end_time = time.time()
    #print(f"Scalar multiplication in G_T took: {(end_time - start_time) * 1000:.3f} ms")
    t.append((end_time - start_time) * 1000)

    # 7. Test pairing operation (G x G_hat -> G_T)
    #print("\nTesting pairing operation (e: G x G_hat -> G_T):")
    start_time = time.time()
    pairing_result = pairing.apply(g1, g_hat)  # Pairing operation
    end_time = time.time()
    #print(f"Pairing operation took: {(end_time - start_time) * 1000:.3f} ms")
    t.append((end_time - start_time) * 1000)

    # 8. Verify bilinear property (optional)
    #print("\nVerifying bilinear property:")
    pairing_check_1 = pairing.apply(g1 ** scalar, g_hat)
    pairing_check_2 = pairing_result ** scalar
    if pairing_check_1 == pairing_check_2:
        pass
        #print("Bilinear property verified: e(g^a, h) == e(g, h)^a")
    else:
        pass
        #print("Bilinear property verification failed!")

    return t


def test_poly():

    # Define coefficients for a 15th order polynomial (example: 2x^15 + 3x^14 + ... + 5)
    coefficients = np.random.randint(-10, 10, size=16)  # Random coefficients between -10 and 10
    #print("Polynomial Coefficients (highest degree first):", coefficients)

    # Function to evaluate polynomial using NumPy's polyval
    def evaluate_polynomial(coeffs, x_val):
        return np.polyval(coeffs, x_val)

    # Test the polynomial with a sample value
    x_value = 2  # Test at x = 2

    # Evaluate the polynomial
    start_time = time.time()
    result = evaluate_polynomial(coefficients, x_value)
    end_time = time.time()

    # Time taken in milliseconds
    time_taken_ms = (end_time - start_time) * 1000

    # Display Results
    #print(f"Evaluating at x = {x_value}")
    #print(f"Polynomial Result: {result}, Time Taken: {time_taken_ms:.3f} ms")

    return time_taken_ms

def avg(s):
    return sum(s) / len(s)

if __name__ == "__main__":
    T = [[], [], [], [], []]
    times = 10000
    for i in range(times):
        t1, t2, t3, t4 = test_operations()
        t = test_poly()

        T[0].append(t1)
        T[1].append(t2)
        T[2].append(t3)
        T[3].append(t4)
        T[4].append(t)

    with open("time_test_%s.txt" % (time.time()), "w") as f:
        for t in T:
            f.write(f"{t}\n")
            f.write("%s\n" % avg(t))
            print(avg(t))
        f.write("%s\n" % (avg(T[0] + T[1] + T[2] + T[3]) / avg(T[-1])))

    print(avg(T[0] + T[1] + T[2]) / avg(T[-1]))