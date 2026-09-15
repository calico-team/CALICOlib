#include <iostream>

using namespace std;

int median(int a, int b, int c) {
    if ((a >= b && a <= c) || (a <= b && a >= c)) {
        return a;
    } else if ((b >= a && b <= c) || (b <= a && b >= c)) {
        return b;
    } else {
        return c;
    }
}

void solve(int N, int arr[]) {
    int res[N];
    res[0] = arr[0];
    res[N - 1] = arr[N - 1];
    for (int i = 1; i < N - 1; i++) {
        res[i] = median(res[i - 1], arr[i], arr[i + 1]);
    }
    for (int i = 0; i < N; i++) {
        cout << res[i] << " ";
    }
    cout << endl;
}

int main() {
    int T;
    cin >> T;
    for (int i = 0; i < T; i++) {
        int N;
        cin >> N;
        int arr[N];
        for (int j = 0; j < N; j++) {
            cin >> arr[j];
        }
        solve(N, arr);
    }
}
