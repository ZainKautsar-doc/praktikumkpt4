"""
Generator dataset dummy untuk Praktikum 1: Hybrid Pipeline
Membuat 100 + 10*A = 130 file .txt dengan konten random

Parameter A = 3 (dari NIM 247006111153)
"""

import os
import random
import string
from pathlib import Path

def generate_dataset(num_files=130, data_dir="./data"):
    """
    Generate dataset dengan file .txt berisi teks random
    
    Args:
        num_files: Jumlah file yang akan dibuat (default: 130)
        data_dir: Direktori untuk menyimpan data
    """
    # Create data directory if not exists
    Path(data_dir).mkdir(exist_ok=True)
    
    print(f"Generating {num_files} files...")
    
    # Generate random text
    def random_text(length=1000):
        """Generate random text untuk file"""
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    # Create files
    for i in range(1, num_files + 1):
        filename = os.path.join(data_dir, f"file_{i:03d}.txt")
        with open(filename, 'w') as f:
            # Setiap file berisi teks random dengan ukuran berbeda (500-2000 bytes)
            file_size = random.randint(500, 2000)
            f.write(random_text(file_size))
        
        if i % 10 == 0:
            print(f"  Created {i}/{num_files} files")
    
    print(f"✓ Dataset berhasil dibuat di direktori '{data_dir}'")
    print(f"  Total files: {num_files}")

if __name__ == "__main__":
    generate_dataset()
