from os.path import join
import sys
import numpy as np
import multiprocessing
import argparse

################################################################################
# FUNCTIONS
################################################################################
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


################################################################################
# COMMAND LINE ARGUMENTS
################################################################################
parser = argparse.ArgumentParser()
# parser.add_argument(
#     "mode",
#     type=str,
#     default="static",
#     choices=["static"],
#     help="Whether to parallelize statically, dynamically or with fixed chunk (depends on number of workers) (default: %(default)s)",
# )
parser.add_argument(
    "N",
    type=int,
    default=60,
    help="Number of floorplans to use (default: %(default)s)",
)
parser.add_argument(
    "-n", "--num-workers",
    type=int,
    default=1,
    help="Number of workers to use for processing (default: %(default)s)",
)
parser.add_argument(
    "-c", "--chunk-size",
    type=int,
    default=None,
    help="Set chunk size (default: %(default)s)",
)

# Parse the command line arguments
args = parser.parse_args()
print("# Options")
for key, value in sorted(vars(args).items()):
    print(key, "=", value)

################################################################################
# MAIN
################################################################################
if __name__ == '__main__':
  # Directory and building IDs
  LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
  with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
      building_ids = f.read().splitlines()

  # Number of floorplans to process
  N = args.N
  num_workers = args.num_workers
  chunk_size = args.chunk_size

  # For timing experiments, limit to at most 100 floorplans.
  building_ids = building_ids[:N]

  # Parameters for Jacobi iteration
  MAX_ITER = 20_000
  ABS_TOL = 1e-4

  # Optimize chunk distribution using numpy for better performance and readability.
  if chunk_size is None:
    chunk_size = (N + num_workers - 1) // num_workers  # Ceiling division to ensure all items are covered
  chunks = [building_ids[i:i + chunk_size] for i in range(0, N, chunk_size)]

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
