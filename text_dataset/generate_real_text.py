# generate_real_text.py
import os
import urllib.request

def create_dataset():
    os.makedirs("text_dataset", exist_ok=True)
    print("Membuat 30 file teks nyata di folder 'text_dataset'...")
    
    # Contoh teks berita / esai sederhana
    sample_text = """
    Komputasi paralel dan terdistribusi adalah cabang dari ilmu komputer yang mempelajari penggunaan beberapa elemen pemroses secara bersamaan untuk menyelesaikan masalah komputasi yang besar.
    Dalam artikel ini, kita membahas tentang keunggulan dari penggunaan MPI atau Message Passing Interface dan threading.
    Sistem komputasi hybrid memungkinkan pemrosesan data dalam jumlah besar dengan waktu yang sangat cepat dan efisien.
    Penggunaan regex untuk tokenisasi kata dan pembuangan stopwords seperti dan, yang, di, the, of, and sangat penting dalam analisis teks.
    """
    
    for i in range(1, 31):
        file_path = os.path.join("text_dataset", f"article_{i}.txt")
        # Mengisi file dengan variasi teks
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sample_text * (i * 5))
            
    print("Selesai membuat 30 file!")

if __name__ == "__main__":
    create_dataset()