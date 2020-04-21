# Convenience utilities for the Monte Carlo computation of Pi

import math, statistics, random, time, sys, ray

def monte_carlo_pi(num_samples, return_points=False):
    """
    Calculate Pi using "Monte Carlo" random sampling.

    Args:
        num_samples: How many samples to take
        return_points: Return all the sample points, too
    Returns:
        The Pi approximation, xs and ys for all points inside or on the circle
        and xs and ys for all points outside the circle. If return_points is
        false, then the returned xs and ys lists are empty.
    """
    in_circle_count = 0
    xs_in  = []
    ys_in  = []
    xs_out = []
    ys_out = []
    for _ in range(num_samples):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x**2 + y**2 <= 1:
            in_circle_count += 1
            if return_points:
                xs_in.append(x)
                ys_in.append(y)
        elif return_points:
            xs_out.append(x)
            ys_out.append(y)
    return 4*in_circle_count/num_samples, xs_in, ys_in, xs_out, ys_out

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
    approx_pi, xs_in, ys_in, xs_out, ys_out = monte_carlo_pi(N, return_points=False)
    return approx_pi

def compute_pi_loop(N):
    return [just_pi(N) for i in range(N)]

@ray.remote
def ray_just_pi(N):
    return just_pi(N)   # No need to redefine, just call just_pi.

# No @ray.remote needed here, at least for our first optimizations.
def ray_compute_pi_loop(N):
    ids = [ray_just_pi.remote(N) for i in range(N)]  # ids = [...remote(N)... is new
    return ray.get(ids)       # Blocks until all the tasks for the ids are finished.

def main():
    num_workers = 16  # We'll do this many calculations for a given N and average the results.

    Ns = [500, 1000, 5000, 10000] #, 50000, 100000, 500000, 1000000] #,  5000000, 10000000] # for a LONG wait!

    print("Results without Ray:")
    ns, means, stddevs, errors, durations = compute_pi_for(Ns, compute_pi_loop)

    ray.init()
    print("Results with Ray:")
    ray_ns, ray_means, ray_stddevs, ray_errors, ray_durations = compute_pi_for(Ns, ray_compute_pi_loop)

if __name__ == '__main__':
    main()