import numpy as np
import random
from functools import reduce
from py_ecc.bn128 import G1, G2, curve_order, multiply, add, eq, neg, field_modulus, pairing
import galois

print("Initializing a large field, this may take a while...")
# modulus = curve_order
modulus = 71

GF = galois.GF(modulus)

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


def trusted_setup(m, t_x, U_polys, V_polys, W_polys):
    encrypted_G1 = list()
    encrypted_G2 = list()
    t_x_h_x_enc = list()

    tau = random.randint(1, modulus)
    pow_of_tau = 1  # tau ** 0

    alpha = random.randint(1, modulus)
    beta = random.randint(1, modulus)
    Alpha = multiply(G1, alpha)
    Beta = multiply(G2, beta)

    t_x_eval = t_x(tau)
    pow_tau_C = list()
    for i in range(0, m):
        encrypted_G1.append(multiply(G1, pow_of_tau))
        encrypted_G2.append(multiply(G2, pow_of_tau))

        pow_tau_C.append(multiply(G1,
                                  int(
                                      GF(beta) * U_polys[i](pow_of_tau) + GF(alpha) *
                                      V_polys[i](pow_of_tau) + W_polys[i](pow_of_tau))
                                  ))

        if i <= m-2:
            t_x_h_x_enc.append(multiply(encrypted_G1[i], int(t_x_eval)))

        pow_of_tau = pow_of_tau*tau

    pow_tau_C_sum = reduce(add, pow_tau_C)

    return encrypted_G1, encrypted_G2, t_x_h_x_enc, Alpha, Beta, pow_tau_C_sum


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

    return reduce(add, res)


t_x = generate_target_polynomial(len(A[0]))
U_polys = interpolate_polynomials(A)
V_polys = interpolate_polynomials(B)
W_polys = interpolate_polynomials(C)

poly1 = inner_product_polynomials_with_witness(U_polys, w)
poly2 = inner_product_polynomials_with_witness(V_polys, w)
poly3 = inner_product_polynomials_with_witness(W_polys, w)


(encrypted_G1, encrypted_G2, t_x_h_x_enc, alpha, beta,
 pow_tau_C_sum) = trusted_setup(len(A[0]), t_x, U_polys, V_polys, W_polys)

h_x = ((poly1 * poly2) - poly3) // t_x

encrypted_U_polys = encrypt_polynomials(U_polys, encrypted_G1, True)
encrypted_V_polys = encrypt_polynomials(V_polys, encrypted_G2, True)
encrypted_W_polys = encrypt_polynomials(pow_tau_C_sum, encrypted_G1, True)

encrypted_t_x_h_x = reduce(add, t_x_h_x_enc)

A_1 = add(reduce(add, encrypted_U_polys), alpha)
B_2 = add(reduce(add, encrypted_V_polys), beta)
C_1 = add(reduce(add, encrypted_W_polys), t_x_h_x_enc)

assert pairing(B_2, A_1) == pairing(beta, alpha) + \
    pairing(G2, C_1), "Fail"
