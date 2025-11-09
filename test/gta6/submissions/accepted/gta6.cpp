#include <iostream>
#include <tuple>

using namespace std;

/**
 * E: Name of event
 * D: Day of event
 * M: Month of event
 * Y: Year of event
 */
string solve(string E, int D, int M, int Y) {
    int gtaD = 19, gtaM = 11, gtaY = 2026;
    if (tie(Y, M, D) < tie(gtaY, gtaM, gtaD)) {
        return "we got " + E + " before gta6";
    } else {
        return "we got gta6 before " + E;
    }
}

int main() {
    int T;
    cin >> T;
    cin.ignore();
    for (int i = 0; i < T; i++) {
        string E;
        getline(cin, E);
        int D, M, Y;
        cin >> Y >> M >> D;
        cin.ignore();
        cout << solve(E, D, M, Y) << '\n';
    }
}
