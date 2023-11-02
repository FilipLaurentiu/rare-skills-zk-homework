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

    function multiply(
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

    function rationalAdd(
        ECPoint calldata A,
        ECPoint calldata B,
        uint256 num,
        uint256 den
    ) public view returns (bool verified) {
        // return true if the prover knows two numbers that add up to num/den
        (bool success, bytes memory result) = address(0x6).staticcall(
            abi.encode(A.x, A.y, B.x, B.y)
        );
        require(success, "Point addition failed!");
        ECPoint memory sum = abi.decode(result, (ECPoint));

        uint256 den_inv = calculateModularInverse(den, bn128_curve_order);

        uint256 mul = mulmod(num, den_inv, bn128_curve_order);

        ECPoint memory mulG1 = multiply(G1, mul);
        
        require(sum.x == mulG1.x && sum.y == mulG1.y, "Equality fail");

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
}
