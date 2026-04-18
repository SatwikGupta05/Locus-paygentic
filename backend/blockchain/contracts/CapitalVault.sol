// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./AgentRegistry.sol";
import "./Reputation.sol";

/// @title CapitalVault
/// @notice Sandbox isolation vault simulating real capital boundaries. Restricts an agent strictly to maximum allocated drawdowns in alignment with its operational capabilities.
contract CapitalVault {
    AgentRegistry public registry;
    Reputation public reputationContract;

    mapping(address => uint256) public agentAllocations;
    mapping(address => uint256) public tradeMaxLimits;

    event AllocationUpdated(address indexed agent, uint256 newAllocation, uint256 newMaxLimit);
    event AgentSlashed(address indexed agent, string reason);

    modifier onlyManager() {
        // Implement standard RBAC here 
        _;
    }

    constructor(address _registry, address _reputation) {
        registry = AgentRegistry(_registry);
        reputationContract = Reputation(_reputation);
    }

    /// @notice Seeds an agent with operational capital parameters 
    function seedAgent(address agentWallet, uint256 totalAllocation, uint256 maxPerTradeLimit) external onlyManager {
        require(registry.isAgentActive(agentWallet), "Cannot fund inactive agent");

        agentAllocations[agentWallet] = totalAllocation;
        tradeMaxLimits[agentWallet] = maxPerTradeLimit;

        emit AllocationUpdated(agentWallet, totalAllocation, maxPerTradeLimit);
    }

    /// @notice Simulates an allocation requirement block. If an agent tries sending an intent larger than limits or their reputation falls low, they get slashed/locked.
    function validateCapitalUsage(address agentWallet, uint256 requestValue) external returns (bool) {
        if (!registry.isAgentActive(agentWallet)) return false;
        
        // Strict boundary checking 
        if (requestValue > tradeMaxLimits[agentWallet]) {
            emit AgentSlashed(agentWallet, "Requested capability overrides maximum defined trade limit");
            return false;
        }

        // Reputation dependency validation to prevent rogue behavior
        (, , , , , uint256 score, ) = reputationContract.systemReputations(agentWallet);
        if (score > 0 && score < 30) {
            emit AgentSlashed(agentWallet, "Reputation index has fallen below operational threshold");
            return false;
        }

        return true;
    }
}
