import os
import sys
from PIL import Image
import imagehash
import cv2
import numpy as np
from multiprocessing import Pool
import time

def get_image_hash(image_path):
    return imagehash.average_hash(Image.open(image_path))

def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    
    # 比較圖片的哈希值
    hash1 = get_image_hash(img1_path)
    hash2 = get_image_hash(img2_path)
    
    if hash1 == hash2:
        # 如果哈希值相等，再進一步比較畫質
        quality1 = cv2.Laplacian(img1, cv2.CV_64F).var()
        quality2 = cv2.Laplacian(img2, cv2.CV_64F).var()
        
        if quality1 > quality2:
            return img1_path, quality1, img2_path, quality2
        else:
            return img2_path, quality2, img1_path, quality1
    return None

def find_image_files(folder_path):
    image_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('jpg', 'jpeg', 'png', 'bmp', 'tiff')):
                image_files.append(os.path.join(root, file))
    return image_files

def process_image_pair(pair):
    img1_path, img2_path = pair
    return compare_images(img1_path, img2_path)

def find_duplicate_images(folder_path):
    image_files = find_image_files(folder_path)
    duplicates = []
    image_pairs = [(image_files[i], image_files[j]) for i in range(len(image_files)) for j in range(i + 1, len(image_files))]

    with Pool() as pool:
        results = pool.map(process_image_pair, image_pairs)
    
    # 過濾掉None的結果
    duplicates = [result for result in results if result is not None]
    
    return duplicates

if __name__ == "__main__":
    # 指定資料夾路徑
    folder_path = sys.argv[1]
    t = time.time()
    print(f"開始時間： {t}")
    duplicates = find_duplicate_images(folder_path)

    # 顯示結果
    for img1, quality1, img2, quality2 in duplicates:
        print(f"重複的圖片: {img1} 和 {img2}\n")
        print(f"建議保留: {img1 if quality1 > quality2 else img2} (畫質: {max(quality1, quality2)})\n")
        print(f"建議刪除: {img2 if quality1 > quality2 else img1} (畫質: {min(quality1, quality2)})\n\n\n")

    print(f"結束時間： {time.time()}")
    print(f"總時間： {time.time() - t}")