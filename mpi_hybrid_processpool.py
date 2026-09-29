import sys
import time
import numpy as np
from mpi4py import MPI
from concurrent.futures import ThreadPoolExecutor

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def mc_pi(n_samples, seed):
    rng = np.random.default_rng(seed)
    x = rng.random(n_samples)
    y = rng.random(n_samples)
    inside = (x*x + y*y) <= 1.0
    return inside.sum()

def worker_task(args):
    samples, seed = args
    return mc_pi(samples, seed)

def chunk_range(total, parts, idx):
    base = total // parts
    rem = total % parts
    start = idx * base + min(idx, rem)
    end = start + base + (1 if idx < rem else 0)
    return start, end

if __name__ == "__main__":
    TOTAL_TASKS = 8
    SAMPLES_PER_TASK = 230000  # A = 3 (200000 + 10000*3)
    
    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    start, end = chunk_range(TOTAL_TASKS, size, rank)
    my_tasks = range(start, end)

    tasks_args = [(SAMPLES_PER_TASK, 1234 + rank * 1000 + k) for k in my_tasks]

    t0 = time.time()
    if len(my_tasks) > 0:
        # Menggunakan ThreadPoolExecutor agar kompatibel sempurna dengan MS-MPI di Windows
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            hits = list(ex.map(worker_task, tasks_args))
    else:
        hits = []

    local_hits = sum(hits)
    local_samples = len(my_tasks) * SAMPLES_PER_TASK
    t1 = time.time()

    global_hits = comm.reduce(local_hits, op=MPI.SUM, root=0)
    global_samp = comm.reduce(local_samples, op=MPI.SUM, root=0)
    local_time = t1 - t0
    makespan = comm.reduce(local_time, op=MPI.MAX, root=0)

    if rank == 0:
        pi_est = 4.0 * global_hits / global_samp
        print(f"[MPI ranks={size} | max_workers={max_workers}] tasks={TOTAL_TASKS}, per_task={SAMPLES_PER_TASK}")
        print(f"Makespan     : {makespan:.4f} s")
        print(f"Total samples: {global_samp:,}")
        print(f"Estimasi pi  : {pi_est:.6f}\n")