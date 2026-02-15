from PIL import Image
import numpy as np


def readPILimg(image):
    img = Image.open(image)
    return img


def red_values(img):
    img = Image.open(img)
    red = list(img.getdata(0))
    return red


def green_values(img):
    img = Image.open(img)
    green = list(img.getdata(1))
    return green


def blue_values(img):
    img = Image.open(img)
    blue = list(img.getdata(2))
    return blue


def merge_image(r, g, b):
    return Image.merge("RGB", (r, g, b))


def color2gray(img):
    img_gray = img.convert('L')
    return img_gray


def PIL2np(img):
    # nrows = img.size[0]
    # ncols = img.size[1]
    # print("nrows, ncols : ", nrows, ncols)
    imgarray = np.array(img)
    return imgarray


def np2PIL(image):
    # print("size of arr: ", image.shape)
    img = Image.fromarray(np.uint8(image))
    return img


def arr_to_PIL(arr):
    return Image.fromarray(arr)
