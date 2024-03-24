

import os
import copy
import re
import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests
import matplotlib
import numbers
import base64
import PIL.Image as Image
from typing import List, Dict, Tuple
from PIL import ImageDraw, ImageFont
from math import cos, sin

import time
import shutil
import json
import glob
import random
import subprocess
import concurrent.futures
from datetime import datetime


def create_dir(parent_dir, dir1=None, filename=None):
    """
    create directory
    :param parent_dir:
    :param dir1:
    :param filename:
    :return:
    """
    out_path = parent_dir
    if dir1:
        out_path = os.path.join(parent_dir, dir1)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if filename:
        out_path = os.path.join(out_path, filename)
    return out_path


color_map = [(0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
             (0, 0, 128), (128, 0, 128), (0, 128, 128), (128, 128, 128),
             (64, 0, 0), (192, 0, 0), (64, 128, 0), (192, 128, 0),
             (64, 0, 128), (192, 0, 128), (64, 128, 128), (192, 128, 128),
             (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128)]






def get_video_capture(video_path, width=None, height=None, fps=None):
    """
     --   7W   Pix--> width=320,height=240
     --   30W  Pix--> width=640,height=480
     720P,100W Pix--> width=1280,height=720
     960P,130W Pix--> width=1280,height=1024
    1080P,200W Pix--> width=1920,height=1080
    :param video_path:
    :param width:
    :param height:
    :return:
    """
    video_cap = cv2.VideoCapture(video_path)
    # 设置分辨率
    if width:
        video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height:
        video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if fps:
        video_cap.set(cv2.CAP_PROP_FPS, 15)
    return video_cap



def get_video_info(video_cap):
    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    numFrames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    print("video:width:{},height:{},fps:{},numFrames:{}".format(width, height, fps, numFrames))
    return width, height, numFrames, fps




def create_dir(parent_dir, dir1=None, filename=None):
    """
    create directory
    :param parent_dir:
    :param dir1:
    :param filename:
    :return:
    """
    out_path = parent_dir
    if dir1:
        out_path = os.path.join(parent_dir, dir1)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    if filename:
        out_path = os.path.join(out_path, filename)
    return out_path




def save_coefficients(mtx, dist, path, image_size):
    """ Save the camera matrix and the distortion coefficients to given path/file. """
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    # mtx： 相机内参矩阵 dist: 畸变系数矩阵
    cv_file.write("size", image_size)  # (W,H)
    cv_file.write("K", mtx)
    cv_file.write("D", dist)
    # note you *release* you don't close() a FileStorage object
    cv_file.release()


def load_coefficients(path):
    """ Loads camera matrix and distortion coefficients. """
    # K： 相机内参矩阵 D: 畸变系数矩阵
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)
    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    image_size = tuple(cv_file.getNode("size").mat().reshape(-1).astype(np.int32))
    camera_matrix = cv_file.getNode("K").mat()
    dist_matrix = cv_file.getNode("D").mat()
    cv_file.release()
    return [camera_matrix, dist_matrix, image_size]



def save_stereo_coefficients(path, K1, D1, K2, D2, R, T, E, F, R1, R2, P1, P2, Q, image_size):
    """ Save the stereo coefficients to given path/file. """
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    cv_file.write("size", image_size)
    cv_file.write("K1", K1)
    cv_file.write("D1", D1)
    cv_file.write("K2", K2)
    cv_file.write("D2", D2)
    cv_file.write("R", R)
    cv_file.write("T", T)
    cv_file.write("E", E)
    cv_file.write("F", F)
    cv_file.write("R1", R1)
    cv_file.write("R2", R2)
    cv_file.write("P1", P1)
    cv_file.write("P2", P2)
    cv_file.write("Q", Q)
    cv_file.release()

