import argparse
from experiments.experiment1 import run_e1
from experiments.experiment2 import run_e2
from experiments.experiment3 import run_e3

def main():
    parser = argparse.ArgumentParser(description="Evolutionary Prompt Genotypes Runner")
    parser.add_argument(
        "--model", 
        type=str, 
        default="qwen3:8b", 
        help="Name of the local Ollama model to use"
    )

    parser.add_argument(
        "--experiment", 
        type=str, 
        default="e1", 
        choices=["e1", "e2", "e3", "e4"], 
        help="Which experiment to run"
    )
    
    args = parser.parse_args()
    
    if args.experiment == "e1":
        print(f"Starting E1 Audit using {args.model}...")
        run_e1(args.model)
    elif args.experiment == "e2":
        print(f"Starting E2 Dyadic Tournament using {args.model}...")
        run_e2(args.model)
    elif args.experiment == "e3":
        print(f"Starting E3 using {args.model}...")
        run_e3(args.model, rounds=10) 

if __name__ == "__main__":
    main()