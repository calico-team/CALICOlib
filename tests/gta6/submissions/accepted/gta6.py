def solve(E: str, D: int, M: int, Y: int) -> str:
    """
    E: Name of event
    D: Day of event
    M: Month of event
    Y: Year of event
    """
    gtaD, gtaM, gtaY = 19, 11, 2026
    if (Y, M, D) < (gtaY, gtaM, gtaD):
        return f"we got {E} before gta6"
    else:
        return f"we got gta6 before {E}"

def main():
    T = int(input())
    for _ in range(T):
        E = input()
        temp = input().split()
        Y, M, D = int(temp[0]), int(temp[1]), int(temp[2])
        print(solve(E, D, M, Y))

if __name__ == '__main__':
    main()