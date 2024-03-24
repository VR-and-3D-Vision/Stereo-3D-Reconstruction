

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


