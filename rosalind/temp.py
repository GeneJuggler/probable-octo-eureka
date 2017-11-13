from textImport import getTextFile

n = 5
k = 3

baby_pairs = 1
adult_pairs = 0
final_months = 5
rabbits_litters = 3

month = 0

while month <= final_months:
    adult_pairs += baby_pairs
    baby_pairs += (adult_pairs - baby_pairs) * rabbits_litters

