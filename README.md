# LZW Compression Project (Python)

## 📌 Project Description
This project implements the **Lempel-Ziv-Welch (LZW)** compression algorithm in Python.  
It supports multiple compression levels and can handle both **text files and images**.

The project also includes a **Graphical User Interface (GUI)** that allows users to easily select files, choose compression levels, and perform compression/decompression operations.

---

## 🚀 Features
- LZW compression and decompression
- Multiple compression levels (Level 1 → Level 6)
- Image and text file support
- GUI-based user interaction
- Performance metrics (entropy, compression ratio, etc.)

---

## 🧠 Algorithm
The core of the system is based on the **dictionary-based LZW algorithm**:
- Repeated patterns are stored in a dictionary
- Each pattern is replaced with a shorter code
- This reduces file size without losing data

---

## 📁 Project Structure
LZW.py # Base LZW algorithm
LZW_Level2.py # Improved version
LZW_Level3.py
LZW_Level4.py
LZW_Level5.py
LZW_Level6_GUI.py # GUI application
image_tools.py # Image processing utilities
---

## 🖥️ GUI
The GUI allows the user to:
- Select a file
- Choose compression level
- Compress or decompress files
- View images

---

## ⚙️ Requirements
Install required libraries:

```bash
pip install numpy pillow pyqt5
