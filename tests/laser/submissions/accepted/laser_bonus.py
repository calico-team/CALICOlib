import math


def egcd(a, b):
    """
    Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd
    """
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b != 0:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0

def solve(K, N, M, P, Q, X, Y):
    """
    Find the index of the first asteroid hit by the laser.
    
    K: Number of asteroids
    N, M: Bounds for x- and y-coordinates
    P, Q: Laser movement (P along y-axis, Q along x-axis)
    X: List of x-coordinates of asteroids
    Y: List of y-coordinates of asteroids
    """
    def solve_single(a, b, m, n, x, y, p, q):
        a = (a - x) % n
        b = (b - y) % m

        g_p_m = math.gcd(p, m)
        g_q_n = math.gcd(q, n)

        if b % g_p_m != 0 or a % g_q_n != 0:
            return float('inf')

        p //= g_p_m
        b //= g_p_m
        m //= g_p_m

        q //= g_q_n
        a //= g_q_n
        n //= g_q_n

        _, p_i, _ = egcd(p, m)
        _, q_i, _ = egcd(q, n)

        b = (b * p_i) % m
        a = (a * q_i) % n

        g_m_n, c, _ = egcd(n, m)
        
        if (a - b) % g_m_n != 0:
            return float('inf')

        l = (a - b) // g_m_n

        M = (n * m) // g_m_n
        return (a - n * c * l) % M

    best_time = float('inf')
    best_i = 0
    
    # The starting coordinate of the laser
    x0, y0 = X[0], Y[0]
    
    # Check all target asteroids
    for i in range(1, K):
        t = solve_single(X[i], Y[i], M, N, x0, y0, P, Q)
        if t < best_time:
            best_time = t
            best_i = i
            
    return best_i

def main():
    T = int(input())

    for _ in range(T):
        line = input().split()
        K = int(line[0])
        N = int(line[1])
        M = int(line[2])
        P = int(line[3])
        Q = int(line[4])
        
        X = []
        Y = []
        for _ in range(K):
            coords = input().split()
            a_i = int(coords[0])
            b_i = int(coords[1])
            X.append(a_i)
            Y.append(b_i)

        print(solve(K, N, M, P, Q, X, Y))

if __name__ == '__main__':
    main()