def solve(K, N, M, P, Q, A):
    """
    Find the index of the first asteroid hit by the laser.
    
    K: Number of asteroids
    N, M: Bounds for x- and y-coordinates
    P, Q: Laser movement (P along y-axis, Q along x-axis)
    A: List of tuples (x_i, y_i) representing asteroid coordinates
    """
    
    start = A[0]
    currX = start[0]
    currY = start[1]
    while True:
        currX = (currX + Q) % N
        currY = (currY + P) % M
        for i in range(K):
            if (A[i][0] == currX) and (A[i][1] == currY):
                return i

def main():
    
    T = int(input())
    
    for _ in range(T):
        line = input().split()
        K = int(line[0])
        N = int(line[1])
        M = int(line[2])
        P = int(line[3])
        Q = int(line[4])
        
        A = []
        for _ in range(K):
            coords = input().split()
            a_i = int(coords[0])
            b_i = int(coords[1])
            A.append((a_i, b_i))

        print(solve(K, N, M, P, Q, A))

if __name__ == '__main__':
    main()