from py_ecc.bn128 import G1, G2, multiply, pairing, add, final_exponentiate

# p1 = pairing(G2, multiply(G1, 4))
# p2 = pairing(multiply(G2, 4), G1)
# p3 = pairing(G2, multiply(G1, 8))


# assert p1 == p2, "Fail 1"
# assert final_exponentiate(p1 * p2) == p3, "Fail 2"


p1 = pairing(G2, multiply(G1, 3))
p2 = pairing(G2, G1)
p3 = pairing(G2, G1)
p4 = pairing(G2, G1)

assert final_exponentiate(p1) == final_exponentiate(p2 * p3 * p4), "FAIL"
