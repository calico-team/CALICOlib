#include <iostream>

using namespace std;

/**
 * E: Name of event
 * D: Day of event
 * M: Month of event
 * Y: Year of event
 */
 string solve(string E, int D, int M, int Y) {
    // YOUR CODE HERE
    return "";
}

int main() {
    int T;
    cin >> T;
    cin.ignore();
    for (int i = 0; i < T; i++) {
        string E;
        getline(cin, E);
        int D, M, Y;
        cin >> D >> M >> Y;
        cin.ignore();
        cout << solve(E, D, M, Y) << '\n';
    }
}