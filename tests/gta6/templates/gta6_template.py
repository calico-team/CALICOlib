def solve(E: str, D: int, M: int, Y: int) -> str:
    """

    E: The name of the event
    D: Day
    M: Month
    Y: Year 
    """
    # YOUR CODE HERE
    return ""

def main():
    T = int(input())
    for _ in range(T):
        E = input()
        temp = input().split()
        D, M, Y = int(temp[0]), int(temp[1]), int(temp[2])
        print(solve(E, D, M, Y))

if __name__ == 'main':
    main()