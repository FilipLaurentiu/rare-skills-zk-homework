// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.2 <0.9.0;

contract Homework3 {
    struct ECPoint {
        uint256 x;
        uint256 y;
    }

    uint256 bn128_curve_order =
        21888242871839275222246405745257275088548364400416034343698204186575808495617;

    ECPoint G1 = ECPoint(1, 2);

    function ec_multiply(
        ECPoint memory P,
        uint256 scalar
    ) public view returns (ECPoint memory) {
        (bool ok, bytes memory result) = address(7).staticcall(
            abi.encode(P.x, P.y, scalar)
        );
        require(ok, "Multiplication failed");
        ECPoint memory res = abi.decode(result, (ECPoint));
        return res;
    }

    function ec_add(
        ECPoint memory A,
        ECPoint memory B
    ) public view returns (ECPoint memory) {
        (bool success, bytes memory result) = address(0x6).staticcall(
            abi.encode(A.x, A.y, B.x, B.y)
        );
        require(success, "Point addition failed!");
        ECPoint memory sum = abi.decode(result, (ECPoint));
        return sum;
    }

    function ec_eq(
        ECPoint memory A,
        ECPoint memory B
    ) public view returns (bool) {
        return (A.x == B.x && A.y == B.y);
    }

    function rationalAdd(
        ECPoint calldata A,
        ECPoint calldata B,
        uint256 num,
        uint256 den
    ) public view returns (bool verified) {
        // return true if the prover knows two numbers that add up to num/den
        ECPoint memory sum = ec_add(A, B);

        uint256 den_inv = calculateModularInverse(den, bn128_curve_order);

        uint256 mul = mulmod(num, den_inv, bn128_curve_order);

        ECPoint memory mulG1 = ec_multiply(G1, mul);

        require(ec_eq(sum, mulG1), "Equality fail");

        return true;
    }

    /// from ChatGPT
    function calculateModularInverse(
        uint256 num,
        uint256 modulus
    ) public pure returns (uint256) {
        require(modulus > 1, "Modulus must be greater than 1");
        require(
            gcd(num, modulus) == 1,
            "The number and modulus must be coprime"
        );

        int256 a = int256(num);
        int256 m = int256(modulus);
        int256 m0 = m;
        int256 x0 = 0;
        int256 x1 = 1;

        while (a > 1) {
            int256 q = a / m;
            int256 t = m;
            m = a % m;
            a = t;

            t = x0;
            x0 = x1 - q * x0;
            x1 = t;
        }

        if (x1 < 0) {
            x1 += m0;
        }

        return uint256(x1);
    }

    function gcd(uint256 a, uint256 b) internal pure returns (uint256) {
        while (b != 0) {
            uint256 temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    function matmul(
        uint256[] calldata matrix,
        uint256 n, // n x n for the matrix
        ECPoint[] calldata s, // n elements
        uint256[] calldata o // n elements
    ) public view returns (bool verified) {
        // revert if dimensions don't make sense or the matrices are empty
        // return true if Ms == 0 elementwise. You need to do n equality checks. If you're lazy, you can hardcode n to 3, but it is suggested that you do this with a for loop
        require(matrix.length == n * n, "Invalid matrix size");
        require(s.length == n, "Invalid s length");
        require(o.length == n, "Invalid o length");

        ECPoint[] memory result_matrix = new ECPoint[](n);

        for (uint256 row = 0; row < n; row++) {
            for (uint256 column = 0; column < n; column++) {
                uint256 index = (row == 0) ? column : column + (n * row);
                ECPoint memory p = ec_multiply(s[column], matrix[index]);
                result_matrix[row] = ec_add(result_matrix[row], p);
            }
        }

        ECPoint memory g1 = G1; // gas saving
        for (uint256 i = 0; i < n; i++) {
            require(
                ec_eq(result_matrix[i], ec_multiply(g1, o[i])),
                "Matrix entry not equal"
            );
        }

        return true;
    }
}
