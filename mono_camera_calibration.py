# -*-coding: utf-8 -*-

import os
import numpy as np
import cv2
import argparse
import glob
import matplotlib.pylab as plt
from tqdm import tqdm
from lib import utils


class Calibrator(object):
    """Apply camera calibrate operation for images in the given directory path."""

    def __init__(self):
        self.image_size = None  # W, H）
        # Arrays to store object points and image points from all the images.
        self.points_world_xyz = []  # 3d point in real world space,
        self.points_pixel_xy = []  # 2d points in image plane,

    @staticmethod
    def get_image_list(image_dir, prefix="", image_format="jpg"):
        
        image_dir = os.path.join(image_dir, prefix + '*.' + image_format)
        image_list = glob.glob(image_dir)
        image_list.sort()
        assert len(image_list) > 0, Exception("Error:images is empty:{}".format(image_dir))
        return image_list

    def calibrate_camera(self, image_dir, width, height, square_size, prefix="", image_format="jpg", show=False):
        """
        :param image_dir: chessboard image directory path
        :param width: chessboard width size
        :param height: chessboard height size
        :param square_size: chessboard square size(mm)
        :param prefix: image prefix
        :param image_format: image format, png/jpg
        :param show: show_2dimage result
        :return: mtx： 
                 dist: 
        """
        image_list = self.get_image_list(image_dir, prefix, image_format)
        assert len(image_list) > 0, Exception("Error:images is empty:{}".format(image_dir))
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 0.0001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
        point_world_xyz = np.zeros((height * width, 3), np.float32)
        point_world_xyz[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)
        point_world_xyz = point_world_xyz * square_size  # Create real world coords. Use your metric.

        # Iterate through the pairs and find chessboard corners. Add them to arrays
        # If openCV can't find the corners in an image, we discard the image.
        for filename in tqdm(image_list):
            print(filename)
            img = cv2.imread(filename)
            if len(img.shape) == 2:
                gray = img
            else:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if self.image_size is None:
                self.image_size = gray.shape[::-1]  # (W,H)
            else:
                assert gray.shape[::-1] == self.image_size
            # Find the chess board corners
            # patternSize = (columns(width), rows(height))
            ret, corners = cv2.findChessboardCorners(gray, (width, height), None)
            # If found, add object points, image points (after refining them)
            if ret:
                # 
                winSize = (9, 9)
                corners2 = cv2.cornerSubPix(gray, corners, winSize, (-1, -1), criteria)
                self.points_world_xyz.append(point_world_xyz)
                self.points_pixel_xy.append(corners2)
                # Draw and display the corners
                # Show the image to see if pattern is found ! imshow function.
                if show:
                    img = cv2.drawChessboardCorners(img, (width, height), corners2, ret)
                    cv2.namedWindow("Chessboard", flags=cv2.WINDOW_NORMAL)
                    cv2.imshow("Chessboard", img)
                    cv2.waitKey(0)
            else:
                raise Exception("no Chessboard:{}".format(filename))
        ret, mtx, dist, rvecs, tvecs = calibrator.calibrate()
        return mtx, dist

    def calibrate(self):
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.points_world_xyz,
                                                           self.points_pixel_xy,
                                                           self.image_size,
                                                           None, None)
        # 
        print("mtx=\n", mtx)
        print("dist=\n", dist)
        # print("rvecs=\n", rvecs)
        # print("tvecs=\n", tvecs)
        print("ret=\n", ret)
        print("PS:if over 0.1,redo calibration")
        return ret, mtx, dist, rvecs, tvecs

    def rectify_test(self, filename, mtx, dist):
        """
        :param filename:
        :param mtx:
        :param dist: 
        :return:
        """
        img = cv2.imread(filename)
        dst1 = self.rectify(img, mtx, dist)
        plt.imshow(img, cmap='gray'), plt.title("Orig"), plt.show()  
        plt.imshow(dst1, cmap='gray'), plt.title("rectify"), plt.show()  
        plt.imshow(dst1 - img, cmap='gray'), plt.title("Diff"), plt.show() 

    def rectify(self, img, mtx, dist):

        return cv2.undistort(img, mtx, dist)

    def save_result(self, save_dir, prefix, mtx, dist):

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        filename = [str(prefix), "cam.yml"]
        filename = "_".join(filename)
        save_file = os.path.join(save_dir, filename)
        utils.save_coefficients(mtx, dist, save_file, self.image_size)
        print("save config in {}".format(save_file))


def str2bool(v):
    return v.lower() in ('yes', 'true', 't', 'y', '1')


def get_parser():
    image_dir = "data/lenacv-camera"
    save_dir = "configs/lenacv-camera"
    prefix = "left"
    # prefix = "right"
    width = 8
    height = 11
    image_format = "png"
    square_size = 20  # mm
    parser = argparse.ArgumentParser(description='Camera calibrate')
    parser.add_argument('--image_dir', type=str, default=image_dir, help='image directory path')
    parser.add_argument('--prefix', type=str, default=prefix, help='image prefix')
    parser.add_argument('--image_format', type=str, default=image_format, help='image format, png/jpg')
    parser.add_argument('--square_size', type=float, default=square_size, help='chessboard square size(mm)')
    parser.add_argument('--width', type=int, default=width, help='chessboard width size')
    parser.add_argument('--height', type=int, default=height, help='chessboard height size')
    parser.add_argument('--save_dir', type=str, default=save_dir, help='YML file to save calibrate matrices')
    parser.add_argument('--show', type=str2bool, nargs='?', const=True, default=True, help='Turn on or turn off flag')
    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()
    print("args={}".format(args))
    calibrator = Calibrator()
    mtx, dist = calibrator.calibrate_camera(image_dir=args.image_dir,
                                            width=args.width,
                                            height=args.height,
                                            square_size=args.square_size,
                                            prefix=args.prefix,
                                            image_format=args.image_format,
                                            show=args.show)
    calibrator.save_result(args.save_dir, args.prefix, mtx, dist)
