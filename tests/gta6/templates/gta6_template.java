import java.io.*;

class Solution {
    /*
     * E: The name of the event
     * D: Day
     * M: Month
     * Y: Year
     */
    static String solve(String E, int D, int M, int Y) {
        // YOUR CODE HERE
        return "";
    }
    static BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
    static PrintWriter out = new PrintWriter(System.out);

    public static void main(String[] args) throws IOException {
        int T = Integer.parseInt(in.readLine());
        for (int i = 0; i < T; i++) {
            String E = in.readLine();   
            String[] temp = in.readLine().split(" ");
            int D = Integer.parseInt(temp[0]), M = Integer.parseInt(temp[1]), Y = Integer.parseInt(temp[2]);
            out.println(solve(E, D, M, Y));
        }
        out.flush();
    }
}

