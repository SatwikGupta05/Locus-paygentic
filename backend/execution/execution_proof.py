import json
from dataclasses import dataclass
from typing import Any


@dataclass
class ExecutionProof:
    """Class to securely encapsulate and present verifiable Kraken CLI commands for audit."""
    execution_source: str
    command: str
    raw_response: dict[str, Any]
    latency_ms: float
    verified: bool = True

    def to_event_payload(self) -> dict[str, Any]:
        """Provides the exactly formatted WebSocket JSON structure requested by the prompt."""
        return {
            "type": "execution_proof",
            "source": self.execution_source,
            "command": self.command,
            "latency": self.latency_ms,
            "status": "verified" if self.verified else "unverified",
            "full_response": self.raw_response,
        }
