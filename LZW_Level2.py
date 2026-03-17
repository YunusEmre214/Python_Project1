import numpy as np
from PIL import Image
import math
import os

def calculate_metrics(original_pixels, compressed_data):
    #Calculates Entropy, Average Code Length and Compression Ratio
    unique, counts = np.unique(original_pixels, return_counts=True)
    probabilities = counts / len(original_pixels)
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    
    
    num_bits_per_code = math.ceil(math.log2(max(compressed_data) + 1))
    avg_code_length = (len(compressed_data) * num_bits_per_code) / len(original_pixels)
    
    
    original_total_bits = len(original_pixels) * 8
    compressed_total_bits = len(compressed_data) * num_bits_per_code
    compression_ratio = original_total_bits / compressed_total_bits
    
    return entropy, avg_code_length, compression_ratio, compressed_total_bits

def lzw_compress(pixels):
   
    dict_size = 256
    dictionary = {tuple([i]): i for i in range(dict_size)}
    
    w = []
    compressed_data = []
    
    for pixel in pixels:
        wc = w + [pixel]
        if tuple(wc) in dictionary:
            w = wc
        else:
            compressed_data.append(dictionary[tuple(w)])
            dictionary[tuple(wc)] = dict_size
            dict_size += 1
            w = [pixel]
    
    if w:
        compressed_data.append(dictionary[tuple(w)])
    
    return compressed_data

def lzw_decompress(compressed_data):
    
    dict_size = 256
    dictionary = {i: [i] for i in range(dict_size)}
    
    
    k = compressed_data[0]
    w = [k]
    result = [k]
    
    for k in compressed_data[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + [w[0]]
        else:
            raise ValueError("Incorrect compression code!")
            
        result.extend(entry)
        dictionary[dict_size] = w + [entry[0]]
        dict_size += 1
        w = entry
        
    return result

def main():
    # 1. Image Reading and Setup
    base_path = os.path.dirname(os.path.abspath(__file__))
    image_name = 'big_image.bmp' 
    image_path = os.path.join(base_path, image_name)

    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found!")
        return

    
    base_name, extension = os.path.splitext(image_name)
    output_file_name = f"{base_name}_restored{extension}"
    bin_name = f"{base_name}.bin"

    img = Image.open(image_path).convert('L') # Convert to Grayscale
    width, height = img.size
    original_pixels = list(img.getdata()) # Get raw pixel values
    
    print(f"Image Size: {width}x{height}")
    print("Compression is starting (Level 2)...")

    # 2. Direct LZW Compression (No Difference Imaging)
    compressed_data = lzw_compress(original_pixels)

    # Save compressed data to .bin file
    bin_path = os.path.join(base_path, bin_name)
    with open(bin_path, "wb") as f:
        for code in compressed_data:
            f.write(code.to_bytes(4, byteorder="big"))  # 4 bytes per code

    print(f"Compressed file saved as: {bin_name}")
    
    # 3. Performance Metrics
    entropy, avg_len, ratio, comp_size = calculate_metrics(original_pixels, compressed_data)
    
    print("-" * 30)
    print(f"Entropy: {entropy:.4f}")
    print(f"Average Code Length: {avg_len:.4f} bits/pixel")
    print(f"Compression Ratio: {ratio:.4f}")
    print(f"Compressed File Size (est): {comp_size / 8:.2f} bytes")
    print("-" * 30)

    # 4. Decompression Process
    print("Decompressing...")
    restored_pixels = lzw_decompress(compressed_data)
    
    # 5. Saving and Final Verification
    restored_img = Image.new('L', (width, height))
    restored_img.putdata(restored_pixels)
    
    # Save with the dynamic name
    restored_img.save(os.path.join(base_path, output_file_name))
    print(f"Restored image saved as: {output_file_name}")
    
    if original_pixels == restored_pixels:
        print("SUCCESSFUL: Original and restored images are identical.")
    else:
        print("ERROR: Differences found between images!")

if __name__ == "__main__":
    main()
