import ollama
import time

GAME_RULES = """
You are playing a repeated game of Prisoner's Dilemma against one other player. 
In each round, you must choose to either 'Cooperate' (C) or 'Defect' (D).

PAYOFF MATRIX (Your payoff, Their payoff):
- Both Cooperate (C,C): (4, 4)
- You Cooperate, They Defect (C,D): (1, 5)
- You Defect, They Cooperate (D,C): (5, 1)
- Both Defect (D,D): (2, 2)

HOW TO READ THE HISTORY:
The history of past rounds is formatted as: R<RoundNumber>:(Your Move, Opponent's Move).
For example, "R1:(C,D)" means in Round 1, YOU Cooperated (C) and YOUR OPPONENT Defected (D).

GOAL: Play the game according to your assigned IDENTITY and the HISTORY of interactions.
"""

# The Wrapper used for every agent
PROMPT_WRAPPER = """
{rules}

YOUR IDENTITY:
{genotype_rules}

CURRENT HISTORY:
{history}

Respond with exactly one character: 'C' (to cooperate) or 'D' (to defect). 
Do not include any explanation, reasoning, quotes, punctuation, or additional text.
"""

def call_ollama(prompt, model_name='qwen3:8b'):
    """
    Standardized wrapper to ensure deterministic outputs.
    """
    try:
        start_time = time.time()
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0,      # Deterministic decoding 
                'num_predict': 4096,
                'seed': 42             
            }
        )
        metadata = {
            "model_used": model_name,
            "input_tokens": response.get('prompt_eval_count', 0),
            "output_tokens": response.get('eval_count', 0),
            "latency_seconds": round(time.time() - start_time, 4),
            "ollama_total_duration_ns": response.get('total_duration', 0)
        }
        
        return response['message']['content'], metadata
    
    except Exception as e:
        print(f"Error calling model: {e}")
        return "INVALID"