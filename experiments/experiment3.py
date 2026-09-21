from engine.llm_client import GAME_RULES, call_ollama, PROMPT_WRAPPER
from engine.helper import get_move, PAYOFF_MATRIX, get_genotypes
from engine.logger import ExperimentLogger
from engine.classic_strategies import ALGORITHMIC_STRATEGIES
import os
import networkx as nx

def play_hybrid_match(model_name, llm_name, llm_rules, bot_name, bot_func, num_rounds=10, window_size=10):

    G = nx.Graph()
    G.add_node(0, name=llm_name, rules=llm_rules, score=0, type="LLM")
    G.add_node(1, name=bot_name, rules="ALGORITHMIC", score=0, type="BOT")
    G.add_edge(0, 1, history=[], detailed_log=[])
    
    for round_num in range(1, num_rounds + 1):
        raw_history = G[0][1]['history']
        
        # --- LLM PLAYER LOGIC (NODE 0) ---
        if not raw_history:
            llm_hist_str = "No rounds have been played yet."
        else:
            # SLIDING WINDOW: Keep only the most recent N rounds
            recent_history = raw_history[-window_size:]
            start_round = max(0, len(raw_history) - window_size)
            
            # Format history string maintaining the correct absolute round numbers
            llm_hist_str = ", ".join(
                [f"R{start_round + idx + 1}:({m1},{m2})" for idx, (m1, m2) in enumerate(recent_history)]
            )

        prompt_llm = PROMPT_WRAPPER.format(
            rules=GAME_RULES, genotype_rules=llm_rules, history=llm_hist_str
        )
        resp_llm, meta_llm = call_ollama(prompt_llm, model_name=model_name)
        move_llm = get_move(resp_llm)
        calc_m1 = "D" if move_llm == "INVALID" else move_llm

        # --- BOT PLAYER LOGIC (NODE 1) ---
        # Bots expect history from their perspective: [(my_move, opp_move)]
        bot_history = [(m2, m1) for m1, m2 in raw_history]
        move_bot = bot_func(bot_history)
        calc_m2 = move_bot # Bots don't produce INVALID moves, but we match variable naming

        # --- UPDATES & LOGGING ---
        G[0][1]['history'].append((calc_m1, calc_m2)) 

        G[0][1]['detailed_log'].append({
            "round": round_num,
            "llm_move": move_llm,
            "bot_move": move_bot,
            "llm_raw_response": resp_llm,
            "llm_metadata": meta_llm or {},
            "llm_prompt_history_seen": llm_hist_str # Good for debugging the sliding window
        })

        pts_p1, pts_p2 = PAYOFF_MATRIX[(calc_m1, calc_m2)]
        G.nodes[0]['score'] += pts_p1
        G.nodes[1]['score'] += pts_p2

        print(f"  Round {round_num}: {llm_name} ({move_llm}) vs {bot_name} ({move_bot}) | Points: +{pts_p1} / +{pts_p2}")

    return G

def run_e3(model_name, rounds=10):

    logger = ExperimentLogger(experiment_name=f"E3_Hybrid_{model_name.replace(':', '-')}")
    
    genotypes = get_genotypes()
    llm_names = list(genotypes.keys())
    bot_names = list(ALGORITHMIC_STRATEGIES.keys())
    
    tournament_results = []

    print(f"\n[+] Starting E3 Hybrid Tournament: {len(llm_names)} LLMs vs {len(bot_names)} BOTs...")

    for llm_name in llm_names:
        for bot_name in bot_names:
            print(f"\n--- Match: {llm_name} vs {bot_name} ---")
            
            bot_logic_func = ALGORITHMIC_STRATEGIES[bot_name]
            
            final_graph = play_hybrid_match(
                model_name=model_name,
                llm_name=llm_name,
                llm_rules=genotypes[llm_name],
                bot_name=bot_name,
                bot_func=bot_logic_func,
                num_rounds=rounds 
            )

            score_llm = final_graph.nodes[0]['score']
            score_bot = final_graph.nodes[1]['score']
            match_log = final_graph[0][1]['detailed_log']

            tournament_results.append({
                "llm_player": llm_name,
                "bot_player": bot_name,
                "llm_total_score": score_llm,
                "bot_total_score": score_bot,
                "llm_average_payoff": score_llm / rounds,
                "bot_average_payoff": score_bot / rounds,
                "match_log": match_log
            })

    logger.save_e3_summary(tournament_results)
    return tournament_results