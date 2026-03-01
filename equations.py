import math

k = 1  

def calc_whale_metric(average_ratio, this_ratio):
    difference = this_ratio - average_ratio
    score = 1 / (1 + math.exp(-k * difference))
    return score
