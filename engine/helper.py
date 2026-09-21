import re
import os

PAYOFF_MATRIX = {
    ('C', 'C'): (4, 4),
    ('C', 'D'): (1, 5),
    ('D', 'C'): (5, 1),
    ('D', 'D'): (2, 2)
}

def get_move(response):
    clean = response.strip()
    if clean == 'C' or clean == 'D' : 
        return clean
    return  "INVALID"
    

def get_genotypes():

    genotypes = {}
    GENOTYPE_DIR = "./genotypes/main_genotypes"
    for filename in os.listdir(GENOTYPE_DIR):
        if filename.endswith(".txt"):
            name = filename.replace(".txt", "")
            with open(os.path.join(GENOTYPE_DIR, filename), "r") as f:
                genotypes[name] = f.read()

    return genotypes