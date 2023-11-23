import numpy as np
import pytest

from py_ecc.bn128 import G1, G2, multiply, pairing, add, curve_order, eq
from ape import project


class G1_ECPoint:
    def __init__(self, P):
        self.x = repr(P[0])
        self.y = repr(P[1])


class G2_ECPoint:
    def __init__(self, P):
        self.x = list([repr(P[0].coeffs[0]), repr(P[0].coeffs[1])])
        self.y = list([repr(P[1].coeffs[0]), repr(P[1].coeffs[1])])


@pytest.fixture
def account1(accounts):
    return accounts[0]


@pytest.fixture
def homework6_contract(account1):
    contract = account1.deploy(project.Homework6)
    return contract


def test_verify_pairing(homework6_contract):
    # x*2 + x + 3

    # v_1 = x * x
    # out = (v_1 + x + 3) * 1
    #
    # [1, x, out, v_1]

    L = np.array([
        [0, 1, 0, 0],
        [3, 1, 0, 1]
    ])

    R = np.array([
        [0, 1, 0, 0],
        [1, 0, 0, 0],
    ])

    O = np.array([
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ])

    s = np.array([1, 2, 9, 4])
    np.testing.assert_array_equal(
        np.matmul(L, s) * np.matmul(R, s), np.matmul(O, s))

    s_G1 = np.array(list(map(lambda x: multiply(G1, x), s)))
    s_G2 = np.array(list(map(lambda x: multiply(G2, x), s)))

    # check for the same discrete logarithm
    # for element1, element2 in zip(s_G1, s_G2):
    #     is_eq = eq(pairing(G2, element1), pairing(element2, G1))
    #     print(is_eq)
    #     assert is_eq

    def ecc_matmul(mat, s_G):
        result = [None] * len(mat)

        for i, mat_el in enumerate(mat):
            for j, s_el in enumerate(s_G):
                temp = multiply(s_el, mat_el[j])
                if temp is not None:
                    if result[i] is None:
                        result[i] = temp
                    else:
                        result[i] = add(result[i], temp)

        return result

    L = ecc_matmul(L, s_G1)
    R = ecc_matmul(R, s_G2)
    O = ecc_matmul(O, s_G1)

    # for i in range(len(L)):
    #     print(eq(pairing(R[i], L[i]), pairing(G2, O[i])))

    # homework6_contract.verify_pairing(
    #     list([G1_ECPoint(L[0])]),
    #     list([G2_ECPoint(R[0])]),
    #     list([G1_ECPoint(O[0])]),
    # )
    homework6_contract.verify_pairing(
        [G1_ECPoint(p) for p in L],
        [G2_ECPoint(p) for p in R],
        [G1_ECPoint(p) for p in O],
    )
