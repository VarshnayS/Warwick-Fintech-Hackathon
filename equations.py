import math
from top50Markets import FindTop50Markets


k = 0.1

def calc_whale_metric(average_ratio, this_ratio):
    difference = this_ratio - average_ratio
    score = 1 / (1 + math.exp(-k * difference))
    return score

print(calc_whale_metric(25, 30))