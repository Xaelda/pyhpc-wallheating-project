from os.path import join
import sys
import numpy as np
import multiprocessing

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] +
                        u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior
        if delta < atol:
            break
    return u

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }

def process_chunk(chunk_building_ids, load_dir, max_iter, abs_tol):
    """Process a list of floorplans and return a list of (building_id, stats) tuples."""
    results = []
    for bid in chunk_building_ids:
        u0, interior_mask = load_data(load_dir, bid)
        u = jacobi(u0, interior_mask, max_iter, abs_tol)
        stats = summary_stats(u, interior_mask)
        results.append((bid, stats))
    return results

if __name__ == '__main__':
    # Directory and building IDs
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    N = int(sys.argv[1])

    # For timing experiments, limit to at most 100 floorplans.
    building_ids = building_ids[:N]

    # Parameters for Jacobi iteration
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    # Determine number of workers from command-line argument (default is 4)
    if len(sys.argv) < 3:
        num_workers = 4
    else:
        num_workers = int(sys.argv[2])

    # Divide the building_ids into contiguous chunks for static scheduling.
  
    chunk_size = N // num_workers
    remainder = N % num_workers
    chunks = []
    start = 0
    for i in range(num_workers):
        # Distribute the remainder among the first few workers
        extra = 1 if i < remainder else 0
        end = start + chunk_size + extra
        chunks.append(building_ids[start:end])
        start = end

    # Use a multiprocessing pool to process each chunk in parallel.
    with multiprocessing.Pool(processes=num_workers) as pool:
        # Use starmap to pass multiple arguments to process_chunk.
        results = pool.starmap(process_chunk, [(c, LOAD_DIR, MAX_ITER, ABS_TOL) for c in chunks])

    # Flatten the list of results.
    all_results = [item for sublist in results for item in sublist]

    # Print summary statistics in CSV format.
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id,' + ','.join(stat_keys))
    for bid, stats in all_results:
        print(f"{bid}," + ",".join(str(stats[k]) for k in stat_keys))
