#include <bits/stdc++.h>
typedef long long ll;
using namespace std;

ll egcd(ll a, ll b, ll& x, ll& y) {
    if (b == 0) {
        x = 1;
        y = 0;
        return a;
    }
    ll x1, y1;
    ll d = egcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - y1 * (a / b);
    return d;
}

ll solve(ll a, ll b, ll n, ll m, ll x, ll y, ll p, ll q) {
	a = ((a - x) % n + n) % n;
	b = ((b - y) % m + m) % m;
	/*
		we have the following system of congruences:
		pt = b (mod m)
		qt = a (mod n)

		check/divide slope
		check/divide dimensions
	*/
	ll g_p_m = gcd(p, m);
	ll g_q_n = gcd(q, n);

	if (b % g_p_m != 0) {
		return LLONG_MAX;
	}
	if (a % g_q_n != 0) {
		return LLONG_MAX;
	}

	p /= g_p_m;
	b /= g_p_m;
	m /= g_p_m;

	q /= g_q_n;
	a /= g_q_n;
	n /= g_q_n;

	ll p_i;
	ll d1; // dummy var
	ll q_i;
	ll d2; // dummy var
	egcd(p, m, p_i, d1);
	egcd(q, n, q_i, d2);

	b *= (p_i % m + m) % m;
	a *= (q_i % n + n) % n;

	b %= m;
	a %= n;

	// nc + nd = gcd(n, n)
	ll c;
	ll d;
	ll g_m_n = egcd(n, m, c, d);
	
	if ((a - b) % g_m_n != 0) {
		return LLONG_MAX;
	}

	ll l = (a - b) / g_m_n;

	ll M = n * m / g_m_n;
	ll temp1 = ((n % M) * (c % M)) % M;
	ll temp2 = (temp1 * (l % M)) % M;

	return (((a - temp2) % M) + M) % M;
}


int main() {
	int t; cin >> t;
	while (t--) {
		int k, n, m, p, q; cin >> k >> n >> m >> p >> q;
		int best_i = 0;
		ll best_time = LLONG_MAX;
		int x, y; cin >> x >> y;
		for (int i = 1; i < k; i++) {
			int a, b; cin >> a >> b;
			ll t = solve(a, b, n, m, x, y, p, q);
			if (t < best_time) {
				best_time = t;
				best_i = i;
			}
		}
		cout << best_i << "\n";
	}
	return 0;
}
