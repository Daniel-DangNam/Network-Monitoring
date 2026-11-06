import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from ai.rules import CLASS_NAMES, SNI_RULES_ADVANCED
    from ai.resnet_model import load_ai_model, features_to_tensor
    from ai.fusion_engine import parallel_fusion_predict
    from ai.online_learner import OnlineTrafficClassifier, get_online_classifier
except ImportError:
    from network_agent.ai.rules import CLASS_NAMES, SNI_RULES_ADVANCED
    from network_agent.ai.resnet_model import load_ai_model, features_to_tensor
    from network_agent.ai.fusion_engine import parallel_fusion_predict
    from network_agent.ai.online_learner import OnlineTrafficClassifier, get_online_classifier

__all__ = [
    "CLASS_NAMES",
    "SNI_RULES_ADVANCED",
    "load_ai_model",
    "features_to_tensor",
    "parallel_fusion_predict",
    "OnlineTrafficClassifier",
    "get_online_classifier"
]

