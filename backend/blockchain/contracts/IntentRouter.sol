// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract IntentRouter is EIP712 {
    bytes32 private constant INTENT_TYPEHASH = keccak256(
        "TradeIntent(string symbol,string action,string size,string price,uint256 timestamp,uint256 nonce,uint256 expiry)"
    );

    mapping(bytes32 => bool) public executedIntents;
    mapping(address => uint256) public nonces;

    event IntentApproved(bytes32 indexed intentHash, address indexed signer, string symbol, string action);

    constructor() EIP712("AURORAIntentRouter", "1") {}

    struct TradeIntent {
        string symbol;
        string action;
        string size;
        string price;
        uint256 timestamp;
        uint256 nonce;
        uint256 expiry;
    }

    function verifyAndRoute(
        TradeIntent calldata intent,
        bytes calldata signature,
        address expectedSigner
    ) external returns (bytes32) {
        require(block.timestamp <= intent.expiry, "Intent expired");
        require(intent.nonce > nonces[expectedSigner], "Invalid nonce");
        
        bytes32 structHash = keccak256(abi.encode(
            INTENT_TYPEHASH,
            keccak256(bytes(intent.symbol)),
            keccak256(bytes(intent.action)),
            keccak256(bytes(intent.size)),
            keccak256(bytes(intent.price)),
            intent.timestamp,
            intent.nonce,
            intent.expiry
        ));

        bytes32 hash = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(hash, signature);
        
        require(signer == expectedSigner, "Invalid signature");
        require(!executedIntents[hash], "Intent already executed");

        // Mark executed & update nonce
        executedIntents[hash] = true;
        nonces[expectedSigner] = intent.nonce;

        emit IntentApproved(hash, signer, intent.symbol, intent.action);

        return hash;
    }
}
