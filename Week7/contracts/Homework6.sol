// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.2 <0.9.0;

contract Homework6 {
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

    G2_ECPoint G2 =
        G2_ECPoint({
            x: [
                10857046999023057135944570762232829481370756359578518086990519993285655852781,
                11559732032986387107991004021392285783925812861821192530917403151452391805634
            ],
            y: [
                8495653923123431417604973247489272438418190587263600148770280649306958101930,
                4082367875863433681332203403145435568316851327593401208105741076214120093531
            ]
        });

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
        G1_ECPoint[] calldata L,
        G2_ECPoint[] calldata R,
        G1_ECPoint[] calldata O
    ) public view returns (bool) {
        uint256[24] memory input; // need to be fix. dynamic length
        G2_ECPoint memory G2 = G2;
        for (uint256 i = 0; i < L.length; i++) {
            G1_ECPoint memory neg_L = negate(L[i]);
            uint256 offset = i * 12;

            input[0 + offset] = neg_L.x;
            input[1 + offset] = neg_L.y;

            input[2 + offset] = R[i].x[1];
            input[3 + offset] = R[i].x[0];
            input[4 + offset] = R[i].y[1];
            input[5 + offset] = R[i].y[0];

            input[6 + offset] = O[i].x;
            input[7 + offset] = O[i].y;

            input[8 + offset] = G2.x[1];
            input[9 + offset] = G2.x[0];
            input[10 + offset] = G2.y[1];
            input[11 + offset] = G2.y[0];
        }

        (bool success, bytes memory data) = address(8).staticcall(
            abi.encode(input)
        );
        if (success) return abi.decode(data, (bool));

        revert("Wrong pairing");
    }
}
