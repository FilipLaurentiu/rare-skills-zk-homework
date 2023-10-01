import numpy as np


def get_column_as_1d(A, col_number):
    # todo
    return np.matrix(A)[:,col_number]


def get_row_as_1d(A, col_number):
    # todo
    return np.matrix(A)[col_number:]


A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

print(get_column_as_1d(A, 1))  # [2,5,8]
print(get_row_as_1d(A, 2)) # [7,8,9]
