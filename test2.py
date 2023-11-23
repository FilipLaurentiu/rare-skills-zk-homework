import numpy as np
import pytest

from py_ecc.bn128 import G1, G2, multiply, pairing, add, curve_order, eq

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

for element1, element2 in zip(s_G1, s_G2):
    is_eq = eq(pairing(G2, element1), pairing(element2, G1))
    print(is_eq)
    assert is_eq
