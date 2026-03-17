import numpy as np
from PIL import Image
import math
import os
import pickle
from image_tools import red_values, green_values, blue_values, merge_image

def calculate_metrics(original_pixels, compressed_data):
    
    unique, counts = np.unique(original_pixels, return_counts=True)
    probabilities = counts / len(original_pixels)
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    
    max_val = max(compressed_data) if compressed_data else 1
    num_bits_per_code = math.ceil(math.log2(max_val + 1))
    avg_code_length = (len(compressed_data) * num_bits_per_code) / len(original_pixels)
    
    original_total_bits = len(original_pixels) * 8
    compressed_total_bits = len(compressed_data) * num_bits_per_code
    ratio = original_total_bits / compressed_total_bits
    
    return entropy, avg_code_length, ratio, compressed_total_bits

def lzw_compress(pixels):
    
    
    shifted_data = [x + 256 for x in pixels]
    dict_size = 512
    dictionary = {tuple([i]): i for i in range(dict_size)}
    w = []
    compressed_data = []

    for pixel in shifted_data:
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
    
    dict_size = 512
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
    return [x - 256 for x in result]

def main():
    # Image Loading and Path Setup
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_name = 'big_image.bmp'
    image_path = os.path.join(current_dir, input_file_name)

    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found!")
        return
    
    # Set up output filename based on input
    base_name, extension = os.path.splitext(input_file_name)
    output_file_name = f"{base_name}_restored{extension}"
    
    img = Image.open(image_path)
    width, height = img.size 
    
    # split color image into R, G, B components (Level 5)
    r_list = red_values(image_path)
    g_list = green_values(image_path)
    b_list = blue_values(image_path)

    channels = [r_list, g_list, b_list]
    channel_names = ["Red", "Green", "Blue"]
    processed_channels = []
    total_comp_size = 0
    total_entropy = 0

    print(f"Image Size: {width}x{height}")
    print("Level 4 Color Compression starting...")

    compressed_all_channels = []

    #Process each color channel individually
    for i, channel_pixels in enumerate(channels):
        
        compressed = lzw_compress(channel_pixels)
        compressed_all_channels.append(compressed)
        
        # Calculate performance metrics per channel
        ent, avg_l, ratio, c_size = calculate_metrics(channel_pixels, compressed)
        total_entropy += ent
        total_comp_size += c_size
        print(f"{channel_names[i]} Channel - Entropy: {ent:.4f}, Ratio: {ratio:.4f}")
        print(f"{channel_names[i]} Channel:")
        print(f"  - Entropy: {ent:.4f}")
        print(f"  - Avg Code Length: {avg_l:.4f} bits/pixel")
        print(f"  - Ratio: {ratio:.4f}")
        print(f"  - Size: {c_size / 8:.2f} bytes") # Bit'i Byte'a çevirdik
        print("-" * 15)

        # Restore channel pixels back to their original intensity
        decompressed = lzw_decompress(compressed)
        processed_channels.append(np.array(decompressed).reshape((height, width)))

    # SAVE COMPRESSED FILE (.bin)   
    bin_path = os.path.join(current_dir, "color_compressed.bin")

    with open(bin_path, "wb") as f:
        # Save dimensions first
        f.write(width.to_bytes(4, 'big'))
        f.write(height.to_bytes(4, 'big'))

        # Save each channel separately
        for compressed in compressed_all_channels:
            f.write(len(compressed).to_bytes(4, 'big'))  # length of channel
            for code in compressed:
                f.write(code.to_bytes(4, 'big'))

    print(f"Compressed color file saved: color_compressed.bin")
    
    #  Level 4: Recombine R, G, B channels
    final_r = processed_channels[0].astype(np.uint8)
    final_g = processed_channels[1].astype(np.uint8)
    final_b = processed_channels[2].astype(np.uint8)
    
    # Reconstruct the image
    restored_img = merge_image(Image.fromarray(final_r), Image.fromarray(final_g), Image.fromarray(final_b))

    #Calculate and display overall performance
    avg_entropy = total_entropy / 3
    overall_ratio = (len(r_list) * 8 * 3) / total_comp_size
    
    print("-" * 30)
    print(f"Overall Entropy (Intensity): {avg_entropy:.4f}")
    print(f"Overall Ratio (Intensity): {overall_ratio:.4f}")
    print("-" * 30)

    # Save and Final Verification
    save_path = os.path.join(current_dir, output_file_name)
    restored_img.save(save_path)
    
    print(f"Restored color image saved as: {output_file_name}")

    if np.array_equal(np.array(img), np.array(restored_img)):
        print("SUCCESSFUL: Color image restoration is perfect (Lossless).")
    else:
        print("ERROR: Differences detected in reconstructed image.")

if __name__ == "__main__":
    main()
