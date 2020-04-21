# Convenience utilities for the Monte Carlo computation of Pi

import math, statistics, random, time, sys

def monte_carlo_pi(num_samples, return_points=False):
	"""
	Calculate Pi using "Monte Carlo" random sampling.

	Args:
		num_samples: How many samples to take
		return_points: Return all the sample points, too
	Returns:
		The Pi approximation, xs and ys for all points. If return_points is
		false, then the returned xs and ys lists are empty.
	"""
	in_circle = 0
	xs = []
	ys = []
	for _ in range(num_samples):
		x = random.uniform(-1, 1)
		y = random.uniform(-1, 1)
		if return_points:
			xs.append(x)
			ys.append(y)
		if x**2 + y**2 < 1:
			in_circle += 1
	return 4*in_circle/num_samples, xs, ys

def compute_pi_for(Ns, compute_pi_loop):
    ns = []
    means = []
    stddevs = []
    errors = []
    durations = []
    for N in Ns:
        ns.append(N)
        print('# samples = {:9d}: '.format(N), end='', flush=True)
        start = time.time()
        pis = compute_pi_loop(N)
        durations.append(time.time() - start)
        means.append(statistics.mean(pis))
        stddevs.append(statistics.stdev(pis))
        errors.append(abs(means[-1] - math.pi)*100/math.pi)
        print('~pi = %8.6f (stddev = %7.6f), error = %7.6f%%, duration = %9.5f seconds' %
            (means[-1], stddevs[-1], errors[-1], durations[-1]))
    return ns, means, stddevs, errors, durations

def just_pi(N):
    approx_pi, xs, ys = monte_carlo_pi(N, return_points=False)
    return approx_pi

def compute_pi_loop(N):
    return [just_pi(N) for i in range(num_workers)]


def main():
	num_workers = 16  # We'll do this many calculations for a given N and average the results.

	Ns = [500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000] #,  5000000, 10000000] # for a LONG wait!


if __name__ == '__main__':
	main()