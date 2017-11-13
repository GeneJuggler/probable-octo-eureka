n = int(input('How many months will we watch the rabbits?\n--> '))
k = int(input('How many litters does each pair of rabbits have?\n--> '))

#baby = 2
#teen = 0
#adult = 0
#
#while n > 0:
#    n -= 1
#    adult += teen
#    teen = baby
#    baby = int(adult / 2) * k * 2
#
#print(int((adult + teen)/2))

def fib(n, k):
    a, b = 1, 1
    for i in range(2, n):
        a, b = b, k*a + b
    return b

print(fib(n, k))
