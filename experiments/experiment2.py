from engine.llm_client import GAME_RULES, call_ollama, PROMPT_WRAPPER
from engine.helper import get_move, PAYOFF_MATRIX, get_genotypes
from engine.logger import ExperimentLogger
import os
from itertools import combinations_with_replacement
import networkx as nx

def play_dyadic_match(model_name, p1_name, p1_rules, p2_name, p2_rules, num_rounds=10):
    """
    Runs a dynamic N-round match between two genotypes using a NetworkX graph.
    """
    #Initialize the Graph Board
    G = nx.Graph()
    G.add_node(0, name=p1_name, rules=p1_rules, score=0)
    G.add_node(1, name=p2_name, rules=p2_rules, score=0)
    G.add_edge(0, 1, history=[], detailed_log=[])
    
    #Game Loop
    for round_num in range(1, num_rounds + 1):
        raw_history = G[0][1]['history']
        
        if not raw_history:
            p1_hist_str = "No rounds have been played yet."
            p2_hist_str = "No rounds have been played yet."
        else:
            p1_hist_str = ", ".join([f"R{idx+1}:({m1},{m2})" for idx, (m1, m2) in enumerate(raw_history)])
            p2_hist_str = ", ".join([f"R{idx+1}:({m2},{m1})" for idx, (m1, m2) in enumerate(raw_history)])

        # PROMPTS AND RESPONSES
        prompt_p1 = PROMPT_WRAPPER.format(
            rules=GAME_RULES, genotype_rules=p1_rules, history=p1_hist_str
        )
        resp_p1, meta_p1 = call_ollama(prompt_p1, model_name=model_name)
        move_p1 = get_move(resp_p1)


        prompt_p2 = PROMPT_WRAPPER.format(
            rules=GAME_RULES, genotype_rules=p2_rules, history=p2_hist_str
        )
        resp_p2, meta_p2 = call_ollama(prompt_p2, model_name=model_name)
        move_p2 = get_move(resp_p2)

        # CRASH PREVENTION: Default to 'D' if the model produces an INVALID move
        calc_m1 = "D" if move_p1 == "INVALID" else move_p1
        calc_m2 = "D" if move_p2 == "INVALID" else move_p2

        #UPDATES
        G[0][1]['history'].append((calc_m1, calc_m2))

        G[0][1]['detailed_log'].append({
            "round": round_num,
            "p1_move": move_p1,
            "p2_move": move_p2,
            "p1_raw_response": resp_p1,
            "p2_raw_response": resp_p2,
            "p1_metadata": meta_p1 or {},
            "p2_metadata": meta_p2 or {}
        })

        pts_p1, pts_p2 = PAYOFF_MATRIX[(calc_m1, calc_m2)]
        G.nodes[0]['score'] += pts_p1
        G.nodes[1]['score'] += pts_p2

        # Optional: Print round by round play
        print(f"  Round {round_num}: P1 ({move_p1}) vs P2 ({move_p2}) | Points: +{pts_p1} / +{pts_p2}")

    return G



def run_e2(model_name, genotype_dir="./genotypes/main_genotypes"):
    """
    Executes all pairwise dyadic matches to generate the E2 Empirical Payoff Matrix data.
    """
    logger = ExperimentLogger(experiment_name=f"E2_Dyadic_Tournament_{model_name.replace(':', '-')}")
    # Load all genotypes into memory
    genotypes = get_genotypes()
    species_names = list(genotypes.keys())
    # Create all pairs
    all_pairs = list(combinations_with_replacement(species_names, 2))
    
    tournament_results = []

    print(f"\n[+] Starting E2 Tournament with {len(all_pairs)} matches...")

    # Play every match
    for p1_name, p2_name in all_pairs:

        print(f"\n--- Match: {p1_name} vs {p2_name} ---")

        p1_rules = genotypes[p1_name]
        p2_rules = genotypes[p2_name]

        # Run the 10-round graph match
        final_graph = play_dyadic_match(
            model_name=model_name,
            p1_name=p1_name,
            p1_rules=p1_rules,
            p2_name=p2_name,
            p2_rules=p2_rules,
            num_rounds=10 # Canonical E2 setting
        )

        # Extract final scores from the graph nodes
        score_p1 = final_graph.nodes[0]['score']
        score_p2 = final_graph.nodes[1]['score']
        match_history = final_graph[0][1]['history']
        match_log = final_graph[0][1]['detailed_log']

        # Store results for your logger / Payoff Matrix calculation
        tournament_results.append({
            "player_1": p1_name,
            "player_2": p2_name,
            "p1_total_score": score_p1,
            "p2_total_score": score_p2,
            "p1_average_payoff": score_p1 / 10.0,
            "p2_average_payoff": score_p2 / 10.0,
            "history": match_history,
            "match_log" : match_log
        })

    print("\n[+] E2 Tournament Complete!")
    logger.save_e2_summary(tournament_results)
    return tournament_results