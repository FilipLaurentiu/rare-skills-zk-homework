from py_ecc.bn128 import G1, G2, curve_order, multiply, add, eq, neg
import pytest
from ape import project


class G1_ECPoint:
    def __init__(self, P):
        self.x = repr(P[0])
        self.y = repr(P[1])


class G2_ECPoint:
    def __init__(self, P):
        self.x = list([repr(P[0].coeffs[1]), repr(P[0].coeffs[0])])
        self.y = list([repr(P[1].coeffs[1]), repr(P[1].coeffs[0])])


@pytest.fixture
def account1(accounts):
    return accounts[0]


@pytest.fixture
def homework4_contract(account1):
    alpha_1 = 5
    beta_2 = 6
    gamma_2 = 3
    delta_2 = 7
    contract = account1.deploy(project.Homework4,
                               G1_ECPoint(multiply(G1, alpha_1)),
                               G2_ECPoint(multiply(G2, beta_2)),
                               G2_ECPoint(multiply(G2, gamma_2)),
                               G2_ECPoint(multiply(G2, delta_2)))
    return contract


def test_verify_pairing(homework4_contract):
    a = 32
    b = 4
    c = 8

    x_1 = 6
    x_2 = 5
    x_3 = 3

    A_1 = multiply(G1, a)
    B_2 = multiply(G2, b)
    C_1 = multiply(G1, c)

    # X_1 = 6G_1 + 5G_1 + 3G_1
    # 0 = -A1*B2 + alpha1*beta2 + X1*gama2 + C1*delta2
    # 0 = -32*4 + 5*6 + (6+5+3)*3 + 8*7
    homework4_contract.verify_pairing(G1_ECPoint(
        A_1), G2_ECPoint(B_2), G1_ECPoint(C_1), x_1, x_2, x_3)
