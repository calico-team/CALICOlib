import java.io.*;

class Solution {
    /*
     * E: The name of the event
     * D: Day
     * M: Month
     * Y: Year
     */
    static String solve(String E, int D, int M, int Y) {
        int gtaD = 19, gtaM = 11, gtaY = 2026;
        if (Y < gtaY || (Y == gtaY && (M < gtaM || (M == gtaM && D < gtaD)))) {
            return "we got " + E + " before gta6";
        } else {
            return "we got gta6 before " + E;
        }
    }
    static BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
    static PrintWriter out = new PrintWriter(System.out);

    public static void main(String[] args) throws IOException {
        int T = Integer.parseInt(in.readLine());
        for (int i = 0; i < T; i++) {
            String E = in.readLine();   
            String[] temp = in.readLine().split(" ");
            int Y = Integer.parseInt(temp[0]), M = Integer.parseInt(temp[1]), D = Integer.parseInt(temp[2]);
            out.println(solve(E, D, M, Y));
        }
        out.flush();
    }
}

