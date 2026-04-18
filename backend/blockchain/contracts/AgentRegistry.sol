// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AgentRegistry is ERC721, Ownable {
    uint256 private _nextTokenId;
    
    mapping(uint256 => string) private _agentHashes;

    event AgentRegistered(uint256 indexed tokenId, address indexed owner, string agentHash);

    constructor() ERC721("AURORA Agent Identity", "AAI") Ownable(msg.sender) {}

    function mintAgent(address to, string calldata agentHash) external returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _mint(to, tokenId);
        _agentHashes[tokenId] = agentHash;
        emit AgentRegistered(tokenId, to, agentHash);
        return tokenId;
    }

    function getAgentHash(uint256 tokenId) external view returns (string memory) {
        return _agentHashes[tokenId];
    }
}
