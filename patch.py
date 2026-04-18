import sys
import re

path = 'backend/workers/trading_engine_v2.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Imports
text = text.replace('from backend.ml.predictor import Predictor\n', 'from backend.ml.predictor import Predictor\nfrom backend.ml.agent_narrative import AgentNarrativeGenerator\n')

# 2. Init
target_init = '        self.decision_engine = DecisionEngine()\n        \n        # Initialize blockchain components'
replacement_init = '        self.decision_engine = DecisionEngine()\n        self.narrative_gen = AgentNarrativeGenerator()\n        \n        # Initialize blockchain components'
text = text.replace(target_init, replacement_init)

# 3. Payload
target_payload = '''            decision_trace = f"Score {decision['score']} derived from ML {ml_result['prob_up']} and TA {analyst['technical_score']}"

            snapshot_payload = {
                "symbol": symbol,
                "price": price,
                "features": features,
                "ml_result": ml_result,
                "scout": scout,
                "analyst": analyst,
                "decision": decision,
                "feature_importance": feature_importance,
                "decision_trace": decision_trace
            }'''
replacement_payload = '''            decision_trace = f"Score {decision['score']} derived from ML {ml_result['prob_up']} and TA {analyst['technical_score']}"

            narrative_obj = self.narrative_gen.generate_narrative(
                decision=decision["action"],
                prob_up=float(ml_result["prob_up"]),
                volatility=0.03,
                signal_fusion_result={"fused_strength": float(decision["confidence"]), "consensus_confidence": float(decision["confidence"]), "narrative": decision_trace},
                portfolio_state={},
                recent_performance={}
            )
            narrative_dict = {
                "decision": narrative_obj.decision,
                "confidence_level": narrative_obj.confidence_level,
                "capital_allocation": narrative_obj.capital_allocation,
                "risk_warning": narrative_obj.risk_warning,
                "opportunity_description": narrative_obj.opportunity_description,
                "expected_edge": narrative_obj.expected_edge,
                "exit_condition": narrative_obj.exit_condition,
            }

            snapshot_payload = {
                "symbol": symbol,
                "price": price,
                "features": features,
                "ml_result": ml_result,
                "scout": scout,
                "analyst": analyst,
                "decision": decision,
                "feature_importance": feature_importance,
                "decision_trace": decision_trace,
                "narrative": narrative_dict
            }'''
text = text.replace(target_payload, replacement_payload)

# 4. Broadcast
target_broadcast = '''                    "feature_importance": event["feature_importance"],
                    "decision_trace": event["decision_trace"]
                },'''
replacement_broadcast = '''                    "feature_importance": event["feature_importance"],
                    "decision_trace": event["decision_trace"],
                    "narrative": event.get("narrative", {})
                },'''
text = text.replace(target_broadcast, replacement_broadcast)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated trading engine.')
