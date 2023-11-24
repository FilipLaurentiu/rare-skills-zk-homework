import numpy as np
import random
from functools import reduce
from scipy.interpolate import lagrange

# Define the matrices
A = np.array([[0, 0, 3, 0, 0, 0],
              [0, 0, 0, 0, 1, 0],
              [0, 0, 1, 0, 0, 0]])

B = np.array([[0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 0, 0],
              [0, 0, 0, 5, 0, 0]])

C = np.array([[0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 1],
              [-3, 1, 1, 2, 0, -1]])

# pick random values for x and y
x = random.randint(1, 10)
y = random.randint(1, 10)

# this is our orignal formula
out = 3 * x * x * y + 5 * x * y - x - 2*y + 3

v1 = 3*x*x
v2 = v1 * y

# the witness vector with the intermediate variables inside
w = np.array([1, out, x, y, v1, v2])

result = C.dot(w) == np.multiply(A.dot(w), B.dot(w))
assert result.all(), "result contains an inequality"


def generate_target_polynomial(n):
    # Create a polynomial of the form (x - 1)(x - 2)(x - 3)...(x - n)
    polynomial = np.poly1d([1])
    for i in range(1, n + 1):
        polynomial *= np.poly1d([1, -i])

    return polynomial


def interpolate_polynomials(Matrix):
    result = list()
    for column_index in range(Matrix.shape[1]):
        column = Matrix[:, column_index]
        coefficients = lagrange(range(1, len(Matrix) + 1), column)
        result.append(np.poly1d(coefficients))
    return result


def inner_product_polynomials_with_witness(polys, witness):
    def mul(x, y): return np.polymul(x, y)
    def sum(x, y): return np.polyadd(x, y)
    return reduce(sum, map(mul, polys, witness))


t_x = generate_target_polynomial(len(A))
print("Target polynomial (x-1)(x-2)(x-3): ", t_x)

U_polys = interpolate_polynomials(A)
print("Interpolated polynomials for U: ", U_polys)

V_polys = interpolate_polynomials(B)
print("Interpolated polynomials for V: ", V_polys)

W_polys = interpolate_polynomials(C)
print("Interpolated polynomial for C: ", W_polys)


poly1 = inner_product_polynomials_with_witness(U_polys, w)
poly2 = inner_product_polynomials_with_witness(V_polys, w)
poly3 = inner_product_polynomials_with_witness(W_polys, w)


h_x = np.polydiv(np.polysub(np.polymul(poly1, poly2), poly3), t_x)

assert h_x[1] == np.poly1d([0]), "division has a reminder"
assert poly1 * poly2 == poly3 + t_x * h_x[0]
