n = int(input('How many months will the experiment go on for?\n-->'))
k = int(input('How many pairs per event are generated?\n-->'))

juvenile = 2
newadult = 0
adult = 0

while n >= 0:
    print(f"Month count is {n}, juvenile {juvenile}, newadult {newadult}, and adult {adult}.")
    n -= 1
    adult += newadult
    newadult = juvenile
    juvenile = k * 2 * int(adult/2)

print(f"Month count is {n}, juvenile {juvenile}, newadult {newadult}, and adult {adult}.")

print(newadult + adult)
