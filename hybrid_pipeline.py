import os
import random
import string
import pathlib
import time
import queue
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
import matplotlib.pyplot as plt

# --- FUNGSI UTAMA PIPELINE ---
def cpu_task(path):
    t0 = time.time()
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode(errors="ignore").lower()
    alpha = sum(c in string.ascii_lowercase for c in text)
    latency = time.time() - t0
    return {"path": path, "alpha": alpha, "latency": latency}

def loader_worker(q, files):
    for p in files:
        q.put(p)
    q.put(None)

def run_pipeline(data_dir, n_loader_threads, n_workers, q_max):
    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    chunks = [files[i::n_loader_threads] for i in range(n_loader_threads)]
    q = queue.Queue(maxsize=q_max)

    loaders = []
    for ch in chunks:
        t = threading.Thread(target=loader_worker, args=(q, ch), daemon=True)
        loaders.append(t)
        t.start()

    done = 0
    results = []
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        while done < n_loader_threads:
            item = q.get()
            if item is None:
                done += 1
            else:
                futures.append(executor.submit(cpu_task, item))

        for f in as_completed(futures):
            results.append(f.result())

    total_time = time.time() - start_time
    total_files = len(files)
    throughput = total_files / total_time if total_time > 0 else 0
    avg_latency = sum(r["latency"] for r in results) / len(results) if results else 0

    print(f"HYBRID PIPELINE")
    print(f"--------------------------------------------------")
    print(f"Loader Threads : {n_loader_threads}")
    print(f"CPU Workers    : {n_workers}")
    print(f"Q_MAX          : {q_max}")
    print(f"Jumlah File    : {total_files}")
    print(f"Total Time     : {total_time:.4f} s")
    print(f"Throughput     : {throughput:.4f} file/s")
    print(f"Avg Latency    : {avg_latency:.4f} s\n")

    return {
        "threads": n_loader_threads,
        "workers": n_workers,
        "q_max": q_max,
        "total_files": total_files,
        "total_time": total_time,
        "throughput": throughput,
        "avg_latency": avg_latency
    }

# --- BLOK UTAMA EKSPERIMEN ---
if __name__ == "__main__":
    DATA_DIR = "data"
    
    # Menjalankan variasi eksperimen (misal mengubah Q_MAX)
    experiments = [
        {"threads": 4, "workers": 6, "q_max": 4},
        {"threads": 4, "workers": 6, "q_max": 32},
    ]

    all_results = []
    for exp in experiments:
        print(f"--------------------------------------------------")
        print(f"Threads={exp['threads']} | Workers={exp['workers']} | Q_MAX={exp['q_max']}")
        print(f"--------------------------------------------------")
        res = run_pipeline(DATA_DIR, exp["threads"], exp["workers"], exp["q_max"])
        all_results.append(res)

    # Simpan hasil ke file CSV
    df = pd.DataFrame(all_results)
    output_csv = "hasil_b1.csv"
    df.to_csv(output_csv, index=False)

    print("--------------------------------------------------")
    print("SEMUA EKSPERIMEN SELESAI")
    print(f"Hasil tersimpan di {output_csv}")
    print("--------------------------------------------------")