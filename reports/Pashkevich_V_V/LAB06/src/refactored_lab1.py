def sum_squares_negatives(numbers):
    return sum(x**2 for x in numbers if x < 0)

def count_climbing_ways(n):
    if n <= 0:
        raise ValueError("Must be positive")
    if n == 1:
        return 1
    if n == 2:
        return 2
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
