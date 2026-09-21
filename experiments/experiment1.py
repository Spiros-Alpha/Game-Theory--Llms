from functools import partial
from engine.audit import AuditManager
from engine.logger import ExperimentLogger
from engine.llm_client import call_ollama
import os

# These are the moves each genotype MUST play given the audit histories
EXPECTED_ACTIONS = {
    "P1_Rational_Maximizer": "D",          
    "P2_Collective_Welfare_Maximizer": "D",           
    "P3_Forgiving_Reciprocator": "C",      
    "P4_Grim_Punisher": "D",            
    "P5_Suspicious_Strategist": "C",         
    "P6_Opportunist": "D",        
    "P7_Reputation_Builder": "C",         
    "P8_Anti-Manipulation_Defender": "C",  
    "P9_Noise-Tolerant_Cooperator": "C",      
    "P10_Risk-Averse_Agent": "D",        
    "P11_Exploration-Oriented_Agent": "D",      
    "P12_Norm_Follower": "C"       
}

def init_e1(model_name):

    model_specific_call = partial(call_ollama, model_name=model_name)
    logger = ExperimentLogger(experiment_name=f"E1_Audit_{model_name.replace(':', '-')}")
    audit = AuditManager(model_specific_call)
    return logger, audit
    

def run_e1(model_name):

    logger, audit = init_e1(model_name)
    comp_score = audit.comprehension_check()
    if comp_score < 4:
        print("Model did not perfectly understand the rules.")

    GENOTYPE_DIR = "./genotypes/main_genotypes"
    for filename in os.listdir(GENOTYPE_DIR):
        if filename.endswith(".txt"):
            genotype_name = filename.replace(".txt", "")
            with open(os.path.join(GENOTYPE_DIR, filename), "r") as f:
                genotype_rules = f.read()

            move, raw_resp , metadata = audit.fidelity_test(genotype_name, genotype_rules)

            target = EXPECTED_ACTIONS.get(genotype_name)
            logger.log_audit(
                genotype=genotype_name,
                fidelity_move=move,
                target_move=target,
                raw_responses=raw_resp,
                metadata = metadata
            )

    logger.save_summary()
    return logger # post-run inspection


