
def median(a, b, c):
    """Returns the median of three numbers."""
    if (a >= b and a <= c) or (a <= b and a >= c):
        return a
    elif (b >= a and b <= c) or (b <= a and b >= c):
        return b
    else:
        return c

def solve(N, A):
    """Solves a single test case."""
    # Initialize the result array with 0s
    res = [0] * N
    
    # Set the first and last elements
    res[0] = A[0]
    res[N - 1] = A[N - 1]
    
    # Calculate the median for the rest
    for i in range(1, N - 1):
        res[i] = median(res[i - 1], A[i], A[i + 1])
        
    # Print the result array separated by spaces
    return res

def main():
    T = int(input())
    for _ in range(T):
        N = int(input())
        A = list(map(int, input().split()))
        result = solve(N, A)
        print(' '.join(str(x) for x in result))


if __name__ == '__main__':
    main()