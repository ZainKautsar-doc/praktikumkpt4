import os
import sys
import re
import time
from collections import Counter
from mpi4py import MPI
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Stopwords minimal sesuai petunjuk (soal nomor 4)
STOPWORDS = {"dan", "yang", "di", "the", "of", "and"}

def process_single_file(file_path):
    """Fungsi untuk membaca file (I/O) dan melakukan tokenisasi kata + pembuangan stopwords (CPU Regex)"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
        
        # Tokenisasi menggunakan Regex
        words = re.findall(r'\b[a-z_]+\b', content)
        
        # Pembuangan stopwords
        filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 1]
        return Counter(filtered_words)
    except Exception as e:
        return Counter()

def chunk_list(lst, n_parts, idx):
    """Membagi daftar file secara merata antar-rank MPI"""
    base = len(lst) // n_parts
    rem = len(lst) % n_parts
    start = idx * base + min(idx, rem)
    end = start + base + (1 if idx < rem else 0)
    return lst[start:end]

if __name__ == "__main__":
    # Mode eksekusi: 'thread' (ThreadPoolExecutor) atau 'process' (ProcessPoolExecutor)
    mode = sys.argv[1] if len(sys.argv) > 1 else "thread"
    DATA_DIR = "text_dataset"
    
    if os.path.exists(DATA_DIR):
        all_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    else:
        all_files = []

    # Membagi file ke rank MPI saat ini
    my_files = chunk_list(all_files, size, rank)

    t0 = time.time()
    local_counter = Counter()

    if my_files:
        if mode == "process":
            # Versi (b): ProcessPoolExecutor
            with ProcessPoolExecutor() as executor:
                results = executor.map(process_single_file, my_files)
                for res in results:
                    local_counter.update(res)
        else:
            # Versi (a): ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                results = executor.map(process_single_file, my_files)
                for res in results:
                    local_counter.update(res)

    t1 = time.time()
    local_time = t1 - t0

    # Pengumpulan hasil global dengan MPI Reduce
    global_counts = comm.reduce(local_counter, op=MPI.SUM, root=0)
    max_makespan = comm.reduce(local_time, op=MPI.MAX, root=0)

    # Menampilkan output hanya pada Rank 0
    if rank == 0:
        print(f"==================================================")
        print(f"GLOBAL WORD COUNT (MPI Ranks={size} | Mode={mode.upper()})")
        print(f"Total File Diproses : {len(all_files)}")
        print(f"Total Waktu Exec    : {max_makespan:.4f} detik")
        print(f"==================================================")