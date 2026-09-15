import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.StringTokenizer;

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
    static int solve(int K, int N, int M, int P, int Q, int[] X, int[] Y) {
        // YOUR CODE HERE
        int x = X[0];
        int y = Y[0];

        while (true) {
            y = (y + P) % M;
            x = (x + Q) % N;
            for (int i = 0; i < K; i++) {
                if (x == X[i] && y == Y[i]) {
                    return i;
                }
            }
        }
    }

    static BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
    static PrintWriter out = new PrintWriter(System.out);

    public static void main(String[] args) throws IOException {
        StringTokenizer tokenizer = new StringTokenizer(in.readLine());

        int T = Integer.parseInt(tokenizer.nextToken());
        while (T-- > 0) {
            tokenizer = new StringTokenizer(in.readLine());
            int K = Integer.parseInt(tokenizer.nextToken());
            int N = Integer.parseInt(tokenizer.nextToken());
            int M = Integer.parseInt(tokenizer.nextToken());
            int P = Integer.parseInt(tokenizer.nextToken());
            int Q = Integer.parseInt(tokenizer.nextToken());

            int[] X = new int[K];
            int[] Y = new int[K];
            for (int i = 0; i < K; i++) {
                tokenizer = new StringTokenizer(in.readLine());
                X[i] = Integer.parseInt(tokenizer.nextToken());
                Y[i] = Integer.parseInt(tokenizer.nextToken());
            }

            out.println(solve(K, N, M, P, Q, X, Y));
        }

        out.flush();
    }
}
