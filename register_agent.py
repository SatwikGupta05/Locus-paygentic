import logging
import sys

from backend.blockchain.contracts import ContractManager
from backend.blockchain.agent_registry import AgentRegistrar
from backend.utils.config import get_settings

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

def main():
    try:
        settings = get_settings()
        cm = ContractManager(settings)
        if not cm.connected:
            logger.error("Could not connect to Web3.")
            return

        registrar = AgentRegistrar(cm)
        logger.info("Attempting to register agent...")
        
        # Check if already registered
        if settings.agent_id > 0:
            logger.info(f"Agent already registered with ID: {settings.agent_id}")
            # Try claiming anyway
            logger.info("Proceeding to claim allocation...")
            success, tx_hash = registrar.claim_allocation(settings.agent_id)
            if success:
                logger.info(f"Allocation claimed successfully! TX: {tx_hash}")
            else:
                logger.info("Could not claim allocation (or already claimed).")
            return

        result = registrar.register()
        if result.get("success"):
            agent_id = result.get("agent_id")
            tx_hash = result.get("tx_hash")
            logger.info(f"Successfully registered agent! Agent ID: {agent_id}, TX: {tx_hash}")
            
            logger.info(f"Claiming allocation for Agent ID {agent_id}...")
            claim_success, claim_tx = registrar.claim_allocation(agent_id)
            if claim_success:
                logger.info(f"Allocation claimed successfully! TX: {claim_tx}")
            else:
                logger.error(f"Failed to claim allocation. TX: {claim_tx}")
                
            logger.info("\n" + "="*50)
            logger.info(f"IMPORTANT: Please update your .env file with AGENT_ID={agent_id}")
            logger.info("="*50 + "\n")
        else:
            logger.error(f"Failed to register agent: {result.get('error')}")
            
    except Exception as e:
        logger.exception(f"Registration failed: {e}")

if __name__ == "__main__":
    main()
