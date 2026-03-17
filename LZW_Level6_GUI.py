import sys
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QComboBox, QApplication, QMainWindow, QPushButton, QLabel, QFileDialog
import os
from PyQt5.QtGui import QPixmap
from image_tools import merge_image

import LZW,LZW_Level2,LZW_Level3,LZW_Level4,LZW_Level5

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LZW GUI")
        self.setGeometry(700, 100, 550, 800) 

        # 1. Image Labels
        self.label_image = QLabel("Original Preview", self)
        self.label_image.setGeometry(30, 30, 240, 240)
        self.label_image.setStyleSheet("border: 2px solid #ccc; background: #f9f9f9; color: grey;")
        self.label_image.setScaledContents(True)

        self.label_image2 = QLabel("Restored Preview", self)
        self.label_image2.setGeometry(280, 30, 240, 240)
        self.label_image2.setStyleSheet("border: 2px solid #ccc; background: #f9f9f9; color: grey;")
        self.label_image2.setScaledContents(True)

        # 2. Statistics Panel
        self.label_info = QLabel(self)
        self.label_info.setGeometry(30, 290, 490, 200)
        self.label_info.setStyleSheet("""
            background-color: blue; 
            color: white; 
            font-family: 'Segoe UI', Arial;
            font-size: 14px;
            padding: 15px;
            border-radius: 8px;
        """)
        self.reset_stats_text()

        # 3. File compress and decompress buttons
        self.method_box = QComboBox(self)
        self.method_box.setGeometry(175, 510, 200, 35)
        for i in range(1, 6): self.method_box.addItem(f"Level {i}")

        self.button_select = QPushButton("Select File", self)
        self.button_select.setGeometry(175, 555, 200, 45)
        self.button_select.clicked.connect(self.select_file)

        self.button_compress = QPushButton("Compress", self)
        self.button_compress.setGeometry(115, 620, 150, 55)
        self.button_compress.setStyleSheet("background-color: #e1e1e1; font-weight: bold;")
        self.button_compress.clicked.connect(self.compress_file)

        self.button_decompress = QPushButton("Decompress", self)
        self.button_decompress.setGeometry(285, 620, 150, 55)
        self.button_decompress.setStyleSheet("background-color: #e1e1e1; font-weight: bold;")
        self.button_decompress.clicked.connect(self.decompress_file)

    def reset_stats_text(self):
        self.label_info.setText(
            "Entropy:\n"
            "Average Code Length:\n"
            "Compression Ratio:\n"
            "Input Image size:\n"
            "Compressed Image size:\n"
            "Difference:"
        )

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_path:
            self.selected_file = file_path
            self.label_image.setPixmap(QPixmap(file_path))
            self.label_image2.clear()
            self.reset_stats_text()
            self.label_info.setText(self.label_info.text() + f"\n\nSelected: {os.path.basename(file_path)}")

    def compress_file(self):
        if not hasattr(self, "selected_file"): return
        
        method = self.method_box.currentText()
        file_ext = os.path.splitext(self.selected_file)[1].lower()
        base_name = os.path.splitext(self.selected_file)[0]
        output_bin = f"{base_name}_compressed.bin"

        #  LEVEL 1 (TEXT)
        if method == "Level 1" and file_ext == ".txt":
            lzw = LZW.LZWCoding(self.selected_file, "text")
            output_path = lzw.compress_text_file()
            self.compressed_data_path = output_path
            
            # Read the file contents and calculate character probabilities.
            with open(self.selected_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # A simple entropy and average length calculation.
            from collections import Counter
            import math
            counts = Counter(text)
            total = len(text)
            ent = -sum((c/total) * math.log2(c/total) for c in counts.values())
            
            # Average bit length after compression
            orig_s = os.path.getsize(self.selected_file)
            comp_s = os.path.getsize(output_path)
            avg = (comp_s * 8) / total if total > 0 else 0

            self.update_stats(ent, avg, orig_s/comp_s, orig_s, comp_s)
            return

        #  IMAGE PROCESSING 
        if file_ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            img = Image.open(self.selected_file).convert('L')
            width, height = img.size
            self.width, self.height = width, height
            pixels = list(img.getdata())
            
            final_data_to_save = [] 

            if method == "Level 2":
                compressed = LZW_Level2.lzw_compress(pixels)
                ent, avg, rat, _ = LZW_Level2.calculate_metrics(pixels, compressed)
                final_data_to_save = [compressed]
            
            elif method == "Level 3":
                img_array = np.array(img)
                diff = LZW_Level3.get_difference_image(img_array)
                self.diff_shape = diff.shape
                compressed = LZW_Level3.lzw_compress(diff.flatten().tolist())
                ent, avg, rat, _ = LZW_Level3.calculate_metrics(diff.flatten().tolist(), compressed)
                final_data_to_save = [compressed]

            elif method == "Level 4":
                r = LZW_Level4.red_values(self.selected_file)
                g = LZW_Level4.green_values(self.selected_file)
                b = LZW_Level4.blue_values(self.selected_file)
                r_c, g_c, b_c = LZW_Level4.lzw_compress(r), LZW_Level4.lzw_compress(g), LZW_Level4.lzw_compress(b)
                ent, avg, rat, size = LZW_Level4.calculate_metrics(r, r_c)
                final_data_to_save = [r_c, g_c, b_c]

            elif method == "Level 5":
                r = LZW_Level5.red_values(self.selected_file)
                g = LZW_Level5.green_values(self.selected_file)
                b = LZW_Level5.blue_values(self.selected_file)
                res_comp = []; t_ent, t_avg, t_size = 0, 0, 0
                for ch in [r, g, b]:
                    diff_img = LZW_Level5.get_difference_image(np.array(ch).reshape(height, width))
                    c = LZW_Level5.lzw_compress(diff_img.flatten().tolist())
                    res_comp.append(c)
                    e, a, ra, s = LZW_Level5.calculate_metrics(diff_img.flatten().tolist(), c)
                    t_ent += e; t_avg += a; t_size += s
                ent, avg, rat, size = t_ent/3, t_avg/3, (len(r)*8*3)/t_size, t_size
                final_data_to_save = res_comp

            # BINARY SAVE (3-byte per code + Header) 
            with open(output_bin, "wb") as f:
                f.write(len(final_data_to_save).to_bytes(4, 'big'))
                for ch in final_data_to_save:
                    f.write(len(ch).to_bytes(4, 'big')) 
                for ch in final_data_to_save:
                    for val in ch:
                        f.write(val.to_bytes(3, 'big')) # 24-bit kod

            self.compressed_data_path = output_bin
            orig_size = os.path.getsize(self.selected_file)
            comp_size = os.path.getsize(output_bin)
            self.update_stats(ent, avg, rat, orig_size, comp_size)

    def update_stats(self, ent, avg, rat, orig, comp):
        diff = orig - comp
        status = "Reduced" if diff >= 0 else "Increased"
        self.label_info.setText(
            f"Entropy: {ent:.4f}\n"
            f"Average Code Length: {avg:.4f} bits/pixel\n"
            f"Compression Ratio: {rat:.4f}\n"
            f"Input Image size: {orig} bytes\n"
            f"Compressed Image size: {comp} bytes\n"
            f"Difference: {abs(diff)} bytes ({status})"
        )

    def decompress_file(self):
        if not hasattr(self, "compressed_data_path"): return
        
        method = self.method_box.currentText()
        base_name = self.compressed_data_path.replace("_compressed.bin", "")
        file_ext = ".txt" if method == "Level 1" else os.path.splitext(self.selected_file)[1]
        output_restored = f"{base_name}_decompressed{file_ext}"

        if method == "Level 1":
            lzw = LZW.LZWCoding(self.selected_file, "text")
            res_path = lzw.decompress_text_file()
            self.label_info.setText(self.label_info.text() + f"\n\nRestored: {os.path.basename(res_path)}")
            self.label_image2.setText("Text Decompressed Successfully")
            return

        #  BINARY READ
        with open(self.compressed_data_path, "rb") as f:
            num_channels = int.from_bytes(f.read(4), 'big')
            ch_sizes = [int.from_bytes(f.read(4), 'big') for _ in range(num_channels)]
            all_channels = []
            for sz in ch_sizes:
                all_channels.append([int.from_bytes(f.read(3), 'big') for _ in range(sz)])

        # DECOMPRESS LOGIC 
        if method == "Level 2":
            pix = LZW_Level2.lzw_decompress(all_channels[0])
            restored_img = Image.new("L", (self.width, self.height))
            restored_img.putdata(pix)
        
        elif method == "Level 3":
            pix = LZW_Level3.lzw_decompress(all_channels[0])
            final = LZW_Level3.restore_from_difference(np.array(pix).reshape(self.diff_shape))
            restored_img = Image.new("L", (self.width, self.height))
            restored_img.putdata(final.flatten().tolist())

        elif method == "Level 4":
            r_d, g_d, b_d = [LZW_Level4.lzw_decompress(c) for c in all_channels]
            restored_img = merge_image(
                Image.fromarray(np.array(r_d).reshape((self.height, self.width)).astype(np.uint8)),
                Image.fromarray(np.array(g_d).reshape((self.height, self.width)).astype(np.uint8)),
                Image.fromarray(np.array(b_d).reshape((self.height, self.width)).astype(np.uint8))
            )

        elif method == "Level 5":
            restored_rgb = []
            for c in all_channels:
                dec = LZW_Level5.lzw_decompress(c)
                restored_rgb.append(LZW_Level5.restore_from_difference(np.array(dec).reshape((self.height, self.width))))
            restored_img = merge_image(
                Image.fromarray(restored_rgb[0].astype(np.uint8)),
                Image.fromarray(restored_rgb[1].astype(np.uint8)),
                Image.fromarray(restored_rgb[2].astype(np.uint8))
            )
        restored_img.save(output_restored)
        self.label_image2.setPixmap(QPixmap(output_restored))
        self.label_info.setText(self.label_info.text() + f"\n\nRestored: {os.path.basename(output_restored)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
