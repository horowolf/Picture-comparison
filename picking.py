import os
import sys
from PIL import Image
import imagehash
import cv2
from multiprocessing import Pool
import time

def get_image_hash(image_path):
    return str(imagehash.average_hash(Image.open(image_path)))

def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    
    quality1 = cv2.Laplacian(img1, cv2.CV_64F).var()
    quality2 = cv2.Laplacian(img2, cv2.CV_64F).var()
    
    size1 = os.path.getsize(img1_path)
    size2 = os.path.getsize(img2_path)
    
    pixels1 = img1.shape[0] * img1.shape[1]
    pixels2 = img2.shape[0] * img2.shape[1]
    
    score1 = quality1 * (size1 / pixels1)
    score2 = quality2 * (size2 / pixels2)
    
    if score1 > score2:
        return img1_path, score1, img2_path, score2
    else:
        return img2_path, score2, img1_path, score1

def find_image_files(folder_path):
    image_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('jpg', 'jpeg', 'png', 'bmp', 'tiff')):
                image_files.append(os.path.join(root, file))
    return image_files

def find_duplicate_images(folder_path):
    image_files = find_image_files(folder_path)
    hash_dict = {}

    print("Getting hash")
    for image_file in image_files:
        img_hash = get_image_hash(image_file)
        if img_hash in hash_dict:
            hash_dict[img_hash].append(image_file)
        else:
            hash_dict[img_hash] = [image_file]

    print("Got hashes, start comparing")
    duplicates = []
    image_pairs = []

    for img_list in hash_dict.values():
        if len(img_list) > 1:
            for i in range(len(img_list)):
                for j in range(i + 1, len(img_list)):
                    image_pairs.append((img_list[i], img_list[j]))
    
    with Pool() as pool:
        results = pool.map(process_image_pair, image_pairs)
    
    duplicates = [result for result in results if result is not None]

    return duplicates

def process_image_pair(pair):
    img1_path, img2_path = pair
    return compare_images(img1_path, img2_path)

if __name__ == "__main__":
    folder_path = sys.argv[1]
    t = time.time()
    print(f"Start time: {t}")
    duplicates = find_duplicate_images(folder_path)

    # 顯示結果
    for img1, score1, img2, score2 in duplicates:
        print(f"Duplicate pictures:\n{img1}\n{img2}\n")
        print(f"Suggest to keep: {img1 if score1 > score2 else img2} (Score: {max(score1, score2)})\n")
        print(f"Suggest to delete: {img2 if score1 > score2 else img1} (Score: {min(score1, score2)})\n\n\n")

    print(f"Finish time: {time.time()}")
    print(f"Total time: {time.time() - t}")