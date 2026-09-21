import re
from .llm_client import GAME_RULES, PROMPT_WRAPPER
from .helper import get_move

class AuditManager:
    def __init__(self, llm_function):
        self.llm = llm_function 

    def comprehension_check(self):
        # Phase 1: Verify the model understands all 4 payoff possibilities.
        scenarios = [
            {"q": "If you choose C and your opponent chooses C, how many points do you get?", "a": "4"},
            {"q": "If you choose C and your opponent chooses D, how many points do you get?", "a": "1"},
            {"q": "If you choose D and your opponent chooses C, how many points do you get?", "a": "6"},
            {"q": "If you choose D and your opponent chooses D, how many points do you get?", "a": "2"}
        ]

        correct_count = 0     
        for s in scenarios:
            prompt = f"{GAME_RULES}\n\nQuestion: {s['q']}\nRespond only with the number."
            response_text, metadata = self.llm(prompt)

            print(f"\n--- COMP CHECK Q: {s['q']} ---")
            print(f"EXPECTED ANSWER: '{s['a']}'")
            print(f"RAW LLM OUTPUT: '{response_text}'")
            
            if s['a'] in response_text:
                correct_count += 1
    
        return correct_count

    def fidelity_test(self, genotype_name, genotype_rules):
        #Tests if the genotype produces the 'Expected phenotype'.                
        test_scenarios = {
            # Opponent cooperates for the last 4 consecutive rounds.Expected: D (Rule 5: Defect once to test short-term yield).
            "P1_Rational_Maximizer": "R1:(C,C), R2:(C,C), R3:(C,D), R4:(D,C), R5:(C,C), R6:(C,C), R7:(C,C), R8:(C,C), R9:(C,C), R10:(C,C)",            
            # Opponent defects for 3 consecutive rounds (R8-R10).Expected: D (Rule 4: Only defect if opponent defects 3 times in a row).
            "P2_Collective_Welfare_Maximizer": "R1:(C,C), R2:(C,C), R3:(C,C), R4:(C,C), R5:(C,C), R6:(C,C), R7:(C,C), R8:(C,D), R9:(C,D), R10:(C,D)",       
            # Opponent defects R9, but cooperates R10.Expected: C (Rule 4: Forgive immediately upon return to cooperation).
            "P3_Forgiving_Reciprocator": "R1:(C,C), R2:(C,C), R3:(C,C), R4:(C,C), R5:(C,C), R6:(C,C), R7:(C,C), R8:(C,C), R9:(C,D), R10:(D,C)",           
            # Opponent betrays once in R3, then cooperates flawlessly.Expected: D (Rule 3/4: Never forgive, maintain permanent defection).
            "P4_Grim_Punisher": "R1:(C,C), R2:(C,C), R3:(C,D), R4:(D,C), R5:(D,C), R6:(D,C), R7:(D,C), R8:(D,C), R9:(D,C), R10:(D,C)",
            # Opponent shows reliable cooperation in last 3 rounds (R8-R10).Expected: C (Rule 2: At least 3 cooperative moves needed to trust).
            "P5_Suspicious_Strategist": "R1:(D,C), R2:(D,D), R3:(D,D), R4:(D,C), R5:(D,D), R6:(D,D), R7:(D,D), R8:(D,C), R9:(D,C), R10:(D,C)",
            # Opponent cooperates for 2 consecutive rounds (R9-R10).Expected: D (Rule 3: Defect to exploit).
            "P6_Opportunist": "R1:(D,D), R2:(D,D), R3:(D,D), R4:(D,D), R5:(D,D), R6:(D,D), R7:(D,D), R8:(D,D), R9:(D,C), R10:(D,C)",
            # Opponent defects repeatedly. You defected in R10. Expected: C (Rule 5: Never defect twice in a row, must repair reputation).
            "P7_Reputation_Builder": "R1:(C,C), R2:(C,C), R3:(C,C), R4:(C,C), R5:(C,C), R6:(C,C), R7:(C,C), R8:(C,D), R9:(C,D), R10:(D,D)",
            # Opponent defected R7, you punished R8-R9. Opponent cooperated R9-R10.Expected: C (Rule 5: Return to cooperation after 2 opponent C's).
            "P8_Anti-Manipulation_Defender": "R1:(C,C), R2:(C,C), R3:(C,C), R4:(C,C), R5:(C,C), R6:(C,C), R7:(C,D), R8:(D,D), R9:(D,C), R10:(D,C)",
            # Opponent cooperates R9, but makes an isolated defection in R10.Expected: C (Rule 3: Treat single defection as noise).
            "P9_Noise-Tolerant_Cooperator": "R1:(C,C), R2:(C,C), R3:(C,C), R4:(C,C), R5:(C,C), R6:(C,C), R7:(C,C), R8:(C,C), R9:(C,C), R10:(C,D)",
            # Opponent defected R8, cooperated R9-R10 (only 2 C's).Expected: D (Rule 4: Needs exactly 3 consecutive C's to feel safe).
            "P10_Risk-Averse_Agent": "R1:(D,D), R2:(D,D), R3:(D,D), R4:(D,D), R5:(D,D), R6:(D,D), R7:(D,D), R8:(D,D), R9:(D,C), R10:(D,C)",
            # Note: 11 rounds provided here so the LLM is predicting Round 12.Expected: D (Rule 4: Every 4th round (e.g., 12), explore by choosing opposite of opponent's last move, which was C).
            "P11_Exploration-Oriented_Agent": "R1:(C,C), R2:(C,C), R3:(C,C), R4:(C,C), R5:(C,C), R6:(C,C), R7:(C,C), R8:(C,C), R9:(C,C), R10:(C,C), R11:(C,C)",
            # will be implemented later.
            "P12_Norm_Follower": "Neighbors: Node 1: C, Node 2: C, Node 3: C, Node 4: D, Node 5: C"
        }
            
        history = test_scenarios.get(genotype_name)
            
        prompt = PROMPT_WRAPPER.format(
            rules=GAME_RULES, 
            genotype_rules=genotype_rules, 
            history=history
        )
        

        response_text, metadata = self.llm(prompt)
        
        print("\n--- DEBUG RESPONSE ---")
        print(f"'{response_text}'")
        print(f"Metadata: {metadata}")

        return get_move(response_text), response_text, metadata
        