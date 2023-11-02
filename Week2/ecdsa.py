from random import randint
from hashlib import sha3_256
from py_ecc.secp256k1.secp256k1 import N, G, add, multiply


print(G + G)
def sign(privKey, msg):
    h = int(sha3_256(msg).hexdigest(), 16)
    k = randint(2, N - 1)
    R = multiply(G, k)
    r = R[0] % N
    k_inv = pow(k, -1, N)

    s = (k_inv * (h + r * privKey)) % N

    return (r, s)


def verify(r, s, msg, pubKey):
    s_inv = pow(s, -1, N)
    h = int(sha3_256(msg).hexdigest(), 16)

    R = add(multiply(G, (h * s_inv) % N), multiply(pubKey, r * s_inv % N))
    assert R[0] == r
    print("Verified !")


msg = b"this is a message"
privKey = randint(2, N - 1)
pubKey = multiply(G, privKey)

signed_msg = sign(privKey, msg)
print("Signature\n")
print(f"m: {msg}")
print(f"r: {signed_msg[0]}")
print(f"s: {signed_msg[1]}")
print(f"public key: {pubKey}")

verify(signed_msg[0], signed_msg[1], msg, pubKey)
