from pypbc import Parameters, Pairing, Element, G1, G2, Zr
import numpy as np
import time

# 统一的阶
UNIFIED_DEGREE = 20


# 初始化非对称双线性配对
def bilinear_pairing_example():
    # 参数初始化
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

    # 生成元素
    g1 = Element.random(pairing, G1)
    g2 = Element.random(pairing, G2)
    a = Element.random(pairing, Zr)
    b = Element.random(pairing, Zr)

    # 计算配对
    start_time = time.time()
    e1 = pairing.apply(g1 ** a, g2 ** b)  # e(g1^a, g2^b)
    end_time = time.time()

    print(f"Bilinear pairing result: {e1}")
    print(f"Bilinear pairing time: {end_time - start_time:.6f} seconds")


# 多项式计算
def polynomial_computation_example():
    # 随机生成多项式的系数
    coeffs = np.random.randint(1, 10, UNIFIED_DEGREE + 1)
    x_value = 3  # 随机取一个点

    start_time = time.time()
    result = np.polyval(coeffs, x_value)
    end_time = time.time()

    print(f"Polynomial coefficients: {coeffs}")
    print(f"Polynomial evaluation result at x={x_value}: {result}")
    print(f"Polynomial computation time: {end_time - start_time:.6f} seconds")


if __name__ == "__main__":
    print("Bilinear Pairing Example:")
    bilinear_pairing_example()

    print("\nPolynomial Computation Example:")
    polynomial_computation_example()
