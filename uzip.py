import zipfile
import py7zr
import rarfile
import os
import tqdm
import threading
import argparse
import tarfile

CHUNK_SIZE = 1024 * 1024  # 1MB chunks

def extract_tar(file_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    with tarfile.open(file_path, 'r:*') as tar:
        total_size = sum(member.size for member in tar.getmembers() if member.isfile())
        with tqdm.tqdm(total=total_size, unit="B", unit_scale=True, desc="Extracting TAR") as pbar:
            for member in tar.getmembers():
                if member.isfile():
                    file_dest = os.path.join(output_path, member.name)
                    os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                    
                    with tar.extractfile(member) as src, open(file_dest, "wb") as dest:
                        while chunk := src.read(CHUNK_SIZE):
                            dest.write(chunk)
                            pbar.update(len(chunk))

def extract_zip(file_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        total_size = sum([zip_ref.getinfo(name).file_size for name in zip_ref.namelist()])
        with tqdm.tqdm(total=total_size, unit="B", unit_scale=True, desc="Extracting ZIP") as pbar:
            for name in zip_ref.namelist():
                file_dest = os.path.join(output_path, name)
                os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                
                with zip_ref.open(name) as src, open(file_dest, "wb") as dest:
                    while chunk := src.read(CHUNK_SIZE):
                        dest.write(chunk)
                        pbar.update(len(chunk))

# may need unrar.exe (https://www.rarlab.com/rar_add.htm)
def extract_rar(file_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    with rarfile.RarFile(file_path) as archive:
        total_size = sum([archive.getinfo(name).file_size for name in archive.namelist()])
        with tqdm.tqdm(total=total_size, unit="B", unit_scale=True, desc="Extracting RAR") as pbar:
            for name in archive.namelist():
                file_dest = os.path.join(output_path, name)
                os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                
                with archive.open(name) as src, open(file_dest, "wb") as dest:
                    while chunk := src.read(CHUNK_SIZE):
                        dest.write(chunk)
                        pbar.update(len(chunk))

def extract_7z(file_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    with py7zr.SevenZipFile(file_path, mode='r') as archive:
        file_list = archive.getnames()
        
        # Extract everything first while tracking progress manually
        total_size = os.path.getsize(file_path)

        with tqdm.tqdm(total=total_size, unit="B", unit_scale=True, desc="Extracting 7Z") as pbar:
            archive.extract(output_path)
            
            # Track extracted file sizes
            extracted_size = sum(os.path.getsize(os.path.join(output_path, f)) for f in file_list if os.path.exists(os.path.join(output_path, f)))
            pbar.update(extracted_size - pbar.n)

def unzip_file(file_path, output_path):
    if file_path.endswith('.zip'):
        extract_zip(file_path, output_path)
    elif file_path.endswith('.rar'):
        extract_rar(file_path, output_path)
    elif file_path.endswith('.7z'):
        extract_7z(file_path, output_path)
    elif file_path.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2')):
        extract_tar(file_path, output_path)
    else:
        print("Unsupported file format.")

def threaded_extraction(extraction_func, file, dest):
    thread=threading.Thread(target=extraction_func,args=(file,dest))
    thread.start()
    thread.join()
        
def main():
    parser=argparse.ArgumentParser(description="CLI Unzip Utility")
    parser.add_argument("file", help="Path to the compressed file")
    parser.add_argument("dest", help="Destination folder for extraction")
    args=parser.parse_args()

    if not os.path.exists(args.file):
        print("Error: File not found")
        return
    
    threaded_extraction(unzip_file, args.file, args.dest)
    print(f"Extraction complete: {args.dest}")

if __name__=="__main__":
    main()
    
