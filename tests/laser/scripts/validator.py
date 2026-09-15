def solve(K, N, M, P, Q, X, Y):
	"""
	Find the index of the first asteroid hit by the laser.
	
	K: Number of asteroids
	N, M: Bounds for x- and y-coordinates
	P, Q: Laser movement (P along y-axis, Q along x-axis)
	X: List of x-coordinates of asteroids
	Y: List of y-coordinates of asteroids
	Return the index of the first hit asteroid
	"""

	assert (K >= 1) and (K <= 1e5)
	assert (M >= K) and (M <= 1e6)
	assert (N >= K) and (N <= 1e6)
	assert (P >= 1) and (P <= M)
	assert (Q >= 1) and (Q <= N)

	coprime = True
	try:
		pow(P, -1, Q)
	except ValueError:
		coprime = False
	
	assert coprime
	assert (len(X) == K) and (len(Y) == K)

	for x in X:
		assert (x >= 0) and (x < N)

	for y in Y:
		assert (y >= 0) and (y < M)

	paired_set = set(zip(X, Y))
	assert len(paired_set) == K, "Duplicate Found"

	return 0

def main():
	
	T = int(input())

	assert (T >= 1) and (T <= 10)

	sumK = 0

	for _ in range(T):
		line = input().split()
		K = int(line[0])
		sumK += K
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

	assert sumK <= 1e5

if __name__ == '__main__':
	main()
