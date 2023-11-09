// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.2 <0.9.0;

contract Homework4 {
    struct G1_ECPoint {
        uint256 x;
        uint256 y;
    }

    struct G2_ECPoint {
        uint256[2] x;
        uint256[2] y;
    }

    uint256 constant PRIME_Q =
        21888242871839275222246405745257275088696311157297823662689037894645226208583;

    G1_ECPoint G1 = G1_ECPoint(1, 2);

    G1_ECPoint Alpha_G1;
    G2_ECPoint Beta_G2;
    G2_ECPoint Gamma_G2;
    G2_ECPoint Delta_G2;

    constructor(
        G1_ECPoint memory alpha_G1,
        G2_ECPoint memory beta_G1,
        G2_ECPoint memory gamma_G2,
        G2_ECPoint memory delta_G2
    ) {
        Alpha_G1 = alpha_G1;
        Beta_G2 = beta_G1;
        Gamma_G2 = gamma_G2;
        Delta_G2 = delta_G2;
    }

    function ec_add(
        G1_ECPoint memory A,
        G1_ECPoint memory B
    ) public view returns (G1_ECPoint memory) {
        (bool success, bytes memory result) = address(6).staticcall(
            abi.encode(A.x, A.y, B.x, B.y)
        );
        require(success, "Point addition failed!");
        G1_ECPoint memory sum = abi.decode(result, (G1_ECPoint));
        return sum;
    }

    function ec_multiply(
        G1_ECPoint memory P,
        uint256 scalar
    ) public view returns (G1_ECPoint memory) {
        (bool ok, bytes memory result) = address(7).staticcall(
            abi.encode(P.x, P.y, scalar)
        );
        require(ok, "Multiplication failed");
        G1_ECPoint memory res = abi.decode(result, (G1_ECPoint));
        return res;
    }

    function negate(
        G1_ECPoint memory p
    ) internal pure returns (G1_ECPoint memory) {
        // The prime q in the base field F_q for G1
        if (p.x == 0 && p.y == 0) {
            return G1_ECPoint(0, 0);
        } else {
            return G1_ECPoint(p.x, PRIME_Q - (p.y % PRIME_Q));
        }
    }

    function verify_pairing(
        G1_ECPoint calldata A_1,
        G2_ECPoint calldata B_2,
        G1_ECPoint calldata C_1,
        uint256 x_1,
        uint256 x_2,
        uint256 x_3
    ) public view returns (bool) {
        G1_ECPoint memory G1 = G1;
        G1_ECPoint memory x_1G_1 = ec_multiply(G1, x_1);
        G1_ECPoint memory x_2G_1 = ec_multiply(G1, x_2);
        G1_ECPoint memory x_3G_1 = ec_multiply(G1, x_3);
        G1_ECPoint memory X_1 = ec_add(ec_add(x_1G_1, x_2G_1), x_3G_1);

        uint256[24] memory input;

        G1_ECPoint memory neg_A_1 = negate(A_1);

        input[0] = neg_A_1.x;
        input[1] = neg_A_1.y;

        input[2] = B_2.x[1];
        input[3] = B_2.x[0];
        input[4] = B_2.y[1];
        input[5] = B_2.y[0];

        input[6] = Alpha_G1.x;
        input[7] = Alpha_G1.y;

        input[8] = Beta_G2.x[1];
        input[9] = Beta_G2.x[0];
        input[10] = Beta_G2.y[1];
        input[11] = Beta_G2.y[0];

        input[12] = X_1.x;
        input[13] = X_1.y;

        input[14] = Gamma_G2.x[1];
        input[15] = Gamma_G2.x[0];
        input[16] = Gamma_G2.y[1];
        input[17] = Gamma_G2.y[0];

        input[18] = C_1.x;
        input[19] = C_1.y;

        input[20] = Delta_G2.x[1];
        input[21] = Delta_G2.x[0];
        input[22] = Delta_G2.y[1];
        input[23] = Delta_G2.y[0];

        (bool success, bytes memory data) = address(8).staticcall(
            abi.encode(input)
        );
        if (success) return abi.decode(data, (bool));

        revert("Wrong pairing");
    }
}
