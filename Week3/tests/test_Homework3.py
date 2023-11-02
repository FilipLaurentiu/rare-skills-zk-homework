from py_ecc.bn128 import G1, curve_order, multiply, add, eq
from random import randint

class ECPoint:
    def __init__(self, P):
        self.x = repr(P[0])
        self.y = repr(P[1])


def test_rationalAdd(homework3_contract):
    num = randint(1, 20)
    den = randint(1, 20)

    print("num: " + str(num))
    print("den: " + str(den))

    prod = num * pow(den, -1, curve_order) % curve_order

    A_mul = randint(0, prod)
    B_mul = prod - A_mul
    
    A = multiply(G1, A_mul)
    B = multiply(G1, B_mul)

    homework3_contract.rationalAdd(ECPoint(A), ECPoint(B), num, den)
