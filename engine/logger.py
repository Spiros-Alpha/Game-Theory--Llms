# engine/logger.py
import json
import os
from datetime import datetime

class ExperimentLogger:
    def __init__(self, experiment_name="E1_Audit"):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = f"logs/{experiment_name}_{self.timestamp}"
        os.makedirs(self.log_dir, exist_ok=True)
        self.results = []

    def log_audit(self, genotype, fidelity_move, target_move, raw_responses, metadata=None):
        """Stores the detailed result for one genotype audit."""
        entry = {
            "genotype": genotype,
            "fidelity_passed": fidelity_move == target_move,
            "produced_move": fidelity_move,
            "target_move": target_move,
            "raw_data": raw_responses,
            "metadata": metadata or {}
        }
        self.results.append(entry)

        
    def save_summary(self):
        """Saves the final fidelity table to a JSON file."""
        summary_path = os.path.join(self.log_dir, "audit_summary.json")
        with open(summary_path, "w") as f:
            json.dump(self.results, f, indent=4)
        print(f"\n[+] Audit data saved to: {summary_path}")

    def save_e2_summary(self, tournament_results):
        """Saves the final Payoff Matrix data for E2 to a JSON file."""
        summary_path = os.path.join(self.log_dir, "e2_summary.json")
        with open(summary_path, "w") as f:
            json.dump(tournament_results, f, indent=4)
        print(f"\n[+] E2 Tournament data saved to: {summary_path}")

    def save_e3_summary(self, tournament_results):
            """Saves the E3 Hybrid Tournament data to a JSON file."""
            summary_path = os.path.join(self.log_dir, "e3_summary.json")
            with open(summary_path, "w") as f:
                json.dump(tournament_results, f, indent=4)
            print(f"\n[+] E3 Tournament data saved to: {summary_path}")