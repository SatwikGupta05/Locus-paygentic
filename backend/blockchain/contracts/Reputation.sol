// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./AgentRegistry.sol";

/// @title Reputation
/// @notice Implements verifiable on-chain reputation logging evaluating AI agent decision consistency, accuracy, and overarching risk handling.
contract Reputation {
    AgentRegistry public registry;
    address public oracle; // Centralized trusted oracle for hackathon purposes that calculates and verifies PnL

    struct AgentReputation {
        uint256 sharpeRatioScore;     // 30% weighting
        uint256 winRateScore;         // 25% weighting
        uint256 drawdownControlScore; // 20% weighting
        uint256 executionAccScore;    // 15% weighting
        uint256 consistencyScore;     // 10% weighting
        uint256 totalScore;           // Merged 100-point index
        uint256 lastUpdated;
    }

    mapping(address => AgentReputation) public systemReputations;

    event ReputationUpdated(address indexed agent, uint256 newTotalScore);

    modifier onlyOracle() {
        require(msg.sender == oracle, "Only the designated protocol oracle can push reputation updates");
        _;
    }

    constructor(address _registryAddress, address _trustedOracle) {
        registry = AgentRegistry(_registryAddress);
        oracle = _trustedOracle;
    }

    /// @notice Submits updated composite score vectors for an agent 
    function submitScore(
        address agent,
        uint256 _sharpe,
        uint256 _winRate,
        uint256 _drawdown,
        uint256 _execution,
        uint256 _consistency
    ) external onlyOracle {
        require(registry.isAgentActive(agent), "Agent not active");

        // Calculate 100-point index combining individual components based on predefined weighting.
        uint256 composite = (_sharpe * 30 / 100) + 
                            (_winRate * 25 / 100) + 
                            (_drawdown * 20 / 100) + 
                            (_execution * 15 / 100) + 
                            (_consistency * 10 / 100);

        systemReputations[agent] = AgentReputation({
            sharpeRatioScore: _sharpe,
            winRateScore: _winRate,
            drawdownControlScore: _drawdown,
            executionAccScore: _execution,
            consistencyScore: _consistency,
            totalScore: composite,
            lastUpdated: block.timestamp
        });

        emit ReputationUpdated(agent, composite);
    }
}
