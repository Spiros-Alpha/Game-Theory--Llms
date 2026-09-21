# engine/classic_strategies.py

def tit_for_tat(history):
    """Round 1: Cooperates. Round N: Mirrors opponent's N-1 move."""
    if not history:
        return "C"
    return history[-1][1]

def always_cooperate(history):
    """The purest altruist. Always returns 'C'."""
    return "C"

def always_defect(history):
    """The pure rational baseline. Always returns 'D'."""
    return "D"

def grim_trigger(history):
    """Cooperates until the opponent defects even once. Then defects forever."""
    # Scan the history to see if the opponent ever played 'D'
    for my_move, opp_move in history:
        if opp_move == 'D':
            return 'D'
    return 'C'

def win_stay_lose_shift(history):
    """
    Also known as Pavlov. Starts with C. 
    If the last round was a 'win' (C,C or D,C), it repeats its last move.
    If the last round was a 'loss' (C,D or D,D), it switches its move.
    In Prisoner's Dilemma math, this simplifies to: Cooperate if both players 
    made the same move last round, otherwise Defect.
    """
    if not history:
        return "C"
    
    my_last, opp_last = history[-1]
    if my_last == opp_last:
        return "C"
    else:
        return "D"

def tit_for_two_tats(history):
    """Extremely forgiving. Only defects if the opponent defected in both of the last two rounds."""
    if len(history) < 2:
        return "C"
    
    if history[-1][1] == 'D' and history[-2][1] == 'D':
        return "D"
    return "C"

def suspicious_tit_for_tat(history):
    """Starts by defecting on Round 1. Then mirrors the opponent's previous move."""
    if not history:
        return "D"
    return history[-1][1]


# Routing dictionary for E3
ALGORITHMIC_STRATEGIES = {
    "BOT_Tit_For_Tat": tit_for_tat,
    "BOT_Always_Cooperate": always_cooperate,
    "BOT_Always_Defect": always_defect,
    "BOT_Grim_Trigger": grim_trigger,
    "BOT_Pavlov_WSLS": win_stay_lose_shift,
    "BOT_Tit_For_Two_Tats": tit_for_two_tats,
    "BOT_Suspicious_TFT": suspicious_tit_for_tat
}
