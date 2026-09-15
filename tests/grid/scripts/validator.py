def solve(N: int, row: list) -> None:
    """
    Validate a single test case for the bonus subproblem.

    N: length of the first row
    row: the first row of the grid
    """
    assert 1 <= N <= 100000
    for val in row:
        assert 1 <= val <= 10**9


def main():
    T = int(input())
    assert 1 <= T <= 10
    for _ in range(T):
        N = int(input())
        row = list(map(int, input().split()))
        assert len(row) == N
        solve(N, row)

if __name__ == '__main__':
    main()
