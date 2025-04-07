from os.path import join
import numpy as np
from numba import cuda


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE+2, SIZE+2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        "mean_temp": mean_temp,
        "std_temp": std_temp,
        "pct_above_18": pct_above_18,
        "pct_below_15": pct_below_15,
    }

@cuda.jit
def jacobi_kern(u, u_new, interior_mask):
    i,j = cuda.grid(2)

    if interior_mask[i, j]:
        # u_new = (u[:-2, 1:-1] + u[2:, 1:-1] + u[1:-1, :-1] + u[1:-1, 1:]) / 4
        u_new[i+1, j+1] = (u[i, j+1] + u[i+2, j+1] + u[i+1, j] + u[i+1, j+2]) / 4


def cuda_jacobi(u, interior_mask, max_iter):
    # Copy data to GPU
    d_u = cuda.to_device(u)
    d_u_new = cuda.device_array_like(d_u)
    d_interior_mask = cuda.to_device(interior_mask)

    threads_per_block = (16,16)
    blocks_per_grid_x = int(np.ceil(interior_mask.shape[0] / threads_per_block[0]))
    blocks_per_grid_y = int(np.ceil(interior_mask.shape[1] / threads_per_block[1]))
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)

    for _ in range(max_iter):
        jacobi_kern[blocks_per_grid, threads_per_block](d_u, d_u_new, d_interior_mask)
        cuda.synchronize()

        # Swap for next iteration
        d_u, d_u_new = d_u_new, d_u
    
    return d_u.copy_to_host()



if __name__ == '__main__':
    import numpy as np
    from os.path import join

    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    N = 100  # Default number of buildings

    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')

    for i, bid in enumerate(building_ids[:N]):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    MAX_ITER = 20000
    ABS_TOL = 1e-4

    all_u = np.empty_like(all_u0)

    all_u_new = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = cuda_jacobi(u0, interior_mask, MAX_ITER)
        all_u[i] = u

        
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))

    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
    print("Done")
    
    


