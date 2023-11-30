import numpy as np
import random
from functools import reduce
from py_ecc.bn128 import G1, G2, curve_order, multiply, add, eq, neg, field_modulus, pairing
import galois

print("Initializing a large field, this may take a while...")
modulus = curve_order
# modulus = 71
GF = galois.GF(curve_order)
print("Galois field ready !")

# Define the matrices
A = GF([
    [0, 1, 0, 0],
    [3, 1, 0, 1]
])

B = GF([
    [0, 1, 0, 0],
    [1, 0, 0, 0],
])

C = GF([
    [0, 0, 0, 1],
    [0, 0, 1, 0],
])
# pick random values for x and y
x = GF(random.randint(1, modulus))

# x*2 + x + 3

v_1 = x * x
out = (v_1 + x + GF(3)) * 1


# the witness vector with the intermediate variables inside

w = GF([1, x, out, v_1])
result = C.dot(w) == np.multiply(A.dot(w), B.dot(w))
assert result.all(), "result contains an inequality"


def generate_target_polynomial(n):
    # Create a polynomial of the form (x - 1)(x - 2)(x - 3)...(x - n)
    polynomial = galois.Poly([1], field=GF)
    for i in range(1, n + 1):
        polynomial *= galois.Poly([1, -i], field=GF)
    return polynomial


def interpolate_polynomials(Matrix):
    result = list()
    for column_index in range(Matrix.shape[1]):
        column = Matrix[:, column_index]
        polynomial = galois.lagrange_poly(
            GF(list(range(1, len(Matrix) + 1))), column)
        result.append(polynomial)
    return result


def inner_product_polynomials_with_witness(polys, witness):
    def mul(x, y): return x * y
    def sum(x, y): return x + y
    return reduce(sum, map(mul, polys, witness))


def trusted_setup(n, t_x):
    res_G1 = list()
    res_G2 = list()
    t_x_enc = list()

    t = random.randint(1, modulus)
    t_x_eval = t_x(t)
    scalar = 1
    for i in range(0, n+1):
        temp = multiply(G1, scalar)
        res_G1.append(temp)
        t_x_enc.append(multiply(temp, int(t_x_eval)))
        res_G2.append(multiply(G2, scalar))

        scalar = scalar*t

    return res_G1, res_G2, t_x_enc


def encrypt_polynomial(poly, encrypted_points):
    encrypted_polynomial = list()
    for index, coeff in enumerate(poly.coefficients()[::-1]):
        encrypted_polynomial.append(
            multiply(encrypted_points[index], int(coeff)))
    return encrypted_polynomial


def encrypt_polynomials(polynomials, encrypted_points, multiply_with_w=False):
    encrypted_polynomials = list()
    for poly in polynomials:
        encrypted_polynomials.append(
            reduce(add, encrypt_polynomial(poly, encrypted_points)))
    if multiply_with_w is True:
        return list(map(lambda x: multiply(x[0], int(x[1])), zip(encrypted_polynomials, w)))
    else:
        return encrypted_polynomials


def inner_product_enc_tx_hx(encrypted_t_x, h_x):
    res = list()
    for index, coeff in enumerate(h_x.coefficients()[::-1]):
        res.append(multiply(encrypted_t_x[index], int(coeff)))

    return res


t_x = generate_target_polynomial(len(A))
U_polys = interpolate_polynomials(A)
V_polys = interpolate_polynomials(B)
W_polys = interpolate_polynomials(C)

poly1 = inner_product_polynomials_with_witness(U_polys, w)
poly2 = inner_product_polynomials_with_witness(V_polys, w)
poly3 = inner_product_polynomials_with_witness(W_polys, w)

h_x = ((poly1 * poly2) - poly3) // t_x

(random_points_G1, random_points_G2,
 encrypted_t_x) = trusted_setup(len(A), t_x)


encrypted_U_polys = encrypt_polynomials(U_polys, random_points_G1, True)
encrypted_V_polys = encrypt_polynomials(V_polys, random_points_G2, True)
encrypted_W_polys = encrypt_polynomials(W_polys, random_points_G1, True)

encrypted_t_x_h_x = inner_product_enc_tx_hx(encrypted_t_x, h_x)

A_1 = reduce(add, encrypted_U_polys)
B_1 = reduce(add, encrypted_V_polys)
C_1 = reduce(add, encrypted_W_polys)

assert pairing(B_1, A_1) == pairing(G2, add(C_1, encrypted_t_x_h_x[0])), "Fail"
