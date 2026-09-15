import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;

class Solution {
    /** 
     * Find the index of the first asteroid hit by the laser.
     * 		
     * K: Number of asteroids
     * N, M: Bounds for x- and y-coordinates
     * P, Q: Laser movement (P along y-axis, Q along x-axis)
     * X: List of x-coordinates of asteroids
     * Y: List of y-coordinates of asteroids
     */

    static long[] egcd(long a, long b) {
        long x0 = 1, y0 = 0, x1 = 0, y1 = 1;
        while (b != 0) {
            long q = a / b;
            long temp = a % b;
            a = b;
            b = temp;

            temp = x1;
            x1 = x0 - q * x1;
            x0 = temp;

            temp = y1;
            y1 = y0 - q * y1;
            y0 = temp;
        }
        return new long[]{a, x0, y0};
    }

    static long gcd(long a, long b) {
        while (b != 0) {
            long temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    static long solveSingle(long a, long b, long m, long n, long x, long y, long p, long q) {
        a = ((a - x) % n + n) % n;
        b = ((b - y) % m + m) % m;

        long g_p_m = gcd(p, m);
        long g_q_n = gcd(q, n);

        if (b % g_p_m != 0) return Long.MAX_VALUE;
        if (a % g_q_n != 0) return Long.MAX_VALUE;

        p /= g_p_m;
        b /= g_p_m;
        m /= g_p_m;

        q /= g_q_n;
        a /= g_q_n;
        n /= g_q_n;

        long[] resP = egcd(p, m);
        long p_i = resP[1];
        
        long[] resQ = egcd(q, n);
        long q_i = resQ[1];

        b = (b * ((p_i % m + m) % m)) % m;
        a = (a * ((q_i % n + n) % n)) % n;

        long[] resMN = egcd(n, m);
        long g_m_n = resMN[0];
        long c = resMN[1];
        long d = resMN[2];

        if ((a - b) % g_m_n != 0) {
            return Long.MAX_VALUE;
        }

        long l = (a - b) / g_m_n;

        long M = (n * m) / g_m_n;
        return (((a - n * c * l) % M) + M) % M;
    }

    static int solve(int K, int N, int M, int P, int Q, int[] X, int[] Y) {
        int best_i = 0;
        long best_time = Long.MAX_VALUE;
        
        // The starting coordinate of the laser
        long x0 = X[0];
        long y0 = Y[0];
        
        for (int i = 1; i < K; i++) {
            long t = solveSingle(X[i], Y[i], M, N, x0, y0, P, Q);
            if (t < best_time) {
                best_time = t;
                best_i = i;
            }
        }
        
        return best_i;
    }

    static BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
    static PrintWriter out = new PrintWriter(System.out);

    public static void main(String[] args) throws IOException {
        int T = Integer.parseInt(in.readLine());
        while (T-- > 0) {
            String[] temp = in.readLine().split(" ");
            int K = Integer.parseInt(temp[0]);
            int N = Integer.parseInt(temp[1]);
            int M = Integer.parseInt(temp[2]);
            int P = Integer.parseInt(temp[3]);
            int Q = Integer.parseInt(temp[4]);

            int[] X = new int[K];
            int[] Y = new int[K];
            for (int i = 0; i < K; i++) {
                String[] point = in.readLine().split(" ");
                X[i] = Integer.parseInt(point[0]);
                Y[i] = Integer.parseInt(point[1]);
            }

            out.println(solve(K, N, M, P, Q, X, Y));
        }

        out.flush();
    }
}

