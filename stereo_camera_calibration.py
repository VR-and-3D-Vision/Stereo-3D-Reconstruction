import sys
import os

sys.path.append(os.getcwd())
import numpy as np
import cv2
import glob
import argparse
from lib.utils import load_coefficients, save_stereo_coefficients


class Calibrator(object):
    """Apply camera calibrate operation for images in the given directory path."""

    def __init__(self):
        self.image_size = None  # （H, W）
        # Arrays to store object points and image points from all the images.
        self.points_world_xyz = []  # 3d point in real world space
        self.left_points_pixel_xy = []  # 2d points in image plane.
        self.right_points_pixel_xy = []  # 2d points in image plane.

    @staticmethod
    def get_image_list(image_dir, prefix="", image_format="jpg"):

        image_dir = os.path.join(image_dir, prefix + '*.' + image_format)
        image_list = glob.glob(image_dir)
        image_list.sort()
        assert len(image_list) > 0, Exception("Error:images is empty:{}".format(image_dir))
        return image_list

    def stereoCalibrate(self, objectPoints, imagePoints1, imagePoints2, cameraMatrix1, distCoeffs1, cameraMatrix2,
                        distCoeffs2, imageSize, R=None, T=None, E=None, F=None, flags=None,
                        criteria=None):
        """
        :param objectPoints: 
        :param imagePoints1: 
        :param imagePoints2: 
        :param cameraMatrix1: Input/output camera intrinsic matrix for the first camera
        :param distCoeffs1:  Input/output vector of distortion coefficients for the first camera 
        :param cameraMatrix2: Input/output second camera intrinsic matrix for the second camera
        :param distCoeffs2: Input/output vector of distortion coefficients for the second camera
        :param imageSize:(W,H)
        :param R: rotation matrix
        :param T: 
        :param E: essential matrix
        :param F: fundamental matrix
        :param flags:
        :param criteria:
        :return:
        """
        # K1=cameraMatrix1,D1=distCoeffs1
        # K2=cameraMatrix2,D2=distCoeffs2
        ret, K1, D1, K2, D2, R, T, E, F = cv2.stereoCalibrate(objectPoints, imagePoints1, imagePoints2, cameraMatrix1,
                                                              distCoeffs1, cameraMatrix2, distCoeffs2, imageSize,
                                                              R=R, T=T, E=E, F=F, flags=flags)
        # R=R, T=T, E=E, F=F, flags=flags,criteria=None)
        return ret, K1, D1, K2, D2, R, T, E, F

    def stereoRectify(self, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, imageSize, R, T, R1=None, R2=None,
                      P1=None, P2=None, Q=None, flags=None, alpha=None,
                      newImageSize=None):
        """
        :param cameraMatrix1: Input/output camera intrinsic matrix for the first camera第一个相机的相机内参
        :param distCoeffs1:  Input/output vector of distortion coefficients for the first camera 第一个相机的畸变系数
        :param cameraMatrix2: Input/output second camera intrinsic matrix for the second camera
        :param distCoeffs2: Input/output vector of distortion coefficients for the second camera
        :param imageSize:(W,H)
        :param R: Rotation matrix from the coordinate system of the first camera to the second camera
        :param T: Translation vector from the coordinate system of the first camera to the second camera
        :param R1:
        :param R2:
        :param P1: 
        :param P2: (
        :param Q: 4*4(disparity-to-depth mapping matrix )
        :param flags:
        :param alpha: 
        :param newImageSize: 
        :return:
        """
        R1, R2, P1, P2, Q, roi_left, roi_right = cv2.stereoRectify(cameraMatrix1, distCoeffs1,
                                                                   cameraMatrix2, distCoeffs2,
                                                                   imageSize, R, T,
                                                                   R1=R1, R2=R2, P1=P1, P2=P2, Q=Q,
                                                                   flags=flags, alpha=alpha, newImageSize=newImageSize)
        return R1, R2, P1, P2, Q, roi_left, roi_right

    def stereo_calibrate(self,
                         left_file,
                         left_dir,
                         left_prefix,
                         right_file,
                         right_dir,
                         right_prefix,
                         image_format,
                         save_dir,
                         square_size,
                         width=9,
                         height=6):
        """ Stereo calibration and rectification """
        self.load_image_points(left_dir, left_prefix, right_dir, right_prefix, image_format, square_size, width, height)
        # mtx：  dist: 
        mtx1, dist1, size = load_coefficients(left_file)
        print("left_camera_matrix:\n{}".format(mtx1))
        print("left_distortion:\n{}".format(dist1))
        print("--" * 30)
        # K2：  D2: 
        mtx2, dist2, size = load_coefficients(right_file)
        print("right_camera_matrix:\n{}".format(mtx2))
        print("right_distortion:\n{}".format(dist2))
        print("--" * 30)
        flag = 0
        # flag |= cv2.CALIB_FIX_INTRINSIC
        flag |= cv2.CALIB_USE_INTRINSIC_GUESS
        ret, K1, D1, K2, D2, R, T, E, F = self.stereoCalibrate(self.points_world_xyz,
                                                               self.left_points_pixel_xy,
                                                               self.right_points_pixel_xy,
                                                               mtx1, dist1, mtx2, dist2,
                                                               self.image_size)
        print("R=\n{}".format(R))
        print("T=\n{}".format(T))
        print("--" * 30)
        print("Stereo calibration rms={}".format(ret))
        print("PS:if over 0.1,redo calibration")

        R1, R2, P1, P2, Q, roi_left, roi_right = self.stereoRectify(K1, D1, K2, D2,
                                                                    self.image_size,
                                                                    R,
                                                                    T,
                                                                    flags=cv2.CALIB_ZERO_DISPARITY,
                                                                    alpha=0.9)
        save_file = os.path.join(save_dir, "stereo_cam.yml")
        save_stereo_coefficients(save_file, K1, D1, K2, D2, R, T, E, F, R1, R2, P1, P2, Q, self.image_size)
        print("save config in {}".format(save_file))

    def load_image_points(self,
                          left_dir,
                          left_prefix,
                          right_dir,
                          right_prefix,
                          image_format,
                          square_size,
                          width=9,
                          height=6):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 0.0001)
        pattern_size = (width, height)  # Chessboard size!
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
        point_world_xyz = np.zeros((height * width, 3), np.float32)
        point_world_xyz[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)
        point_world_xyz = point_world_xyz * square_size  # Create real world coords. Use your metric.

        # Get images for left and right directory. Since we use prefix and formats, both image set can be in the same dir.
        # Images should be perfect pairs. Otherwise all the calibration will be false.
        # Be sure that first cam and second cam images are correctly prefixed and numbers are ordered as pairs.
        left_images = self.get_image_list(left_dir, left_prefix, image_format)
        right_images = self.get_image_list(right_dir, right_prefix, image_format)
        # Pairs should be same size. Otherwise we have sync problem.
        if len(left_images) != len(right_images):
            print("Numbers of left and right images are not equal. They should be pairs.")
            print("Left images count: ", len(left_images))
            print("Right images count: ", len(right_images))
            sys.exit(-1)

        pair_images = list(zip(left_images, right_images))  # Pair the images for single loop handling
        # Iterate through the pairs and find chessboard corners. Add them to arrays
        # If openCV can't find the corners in one image, we discard the pair.
        for left_file, right_file in pair_images:
            l_image_id = os.path.basename(left_file)[len(left_prefix):]
            r_image_id = os.path.basename(right_file)[len(right_prefix):]
            assert l_image_id == r_image_id, Exception("Error:{},{}".format(left_file, right_file))
            right = cv2.imread(right_file)
            gray_right = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)
            left = cv2.imread(left_file)
            gray_left = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
            if self.image_size is None:
                self.image_size = gray_right.shape[::-1]  # (W,H)
                # self.image_size = gray_right.shape  # [H,W]
            # Find the chess board corners
            ret_right, corners_right = cv2.findChessboardCorners(gray_right, pattern_size,
                                                                 cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_FILTER_QUADS)
            ret_left, corners_left = cv2.findChessboardCorners(gray_left, pattern_size,
                                                               cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_FILTER_QUADS)

            if ret_left and ret_right:  # If both image is okay. Otherwise we explain which pair has a problem and continue
                # Object points
                self.points_world_xyz.append(point_world_xyz)
                # Right points
                winSize = (9, 9)
                corners2_right = cv2.cornerSubPix(gray_right, corners_right, winSize, (-1, -1), criteria)
                self.right_points_pixel_xy.append(corners2_right)
                # Left points
                corners2_left = cv2.cornerSubPix(gray_left, corners_left, winSize, (-1, -1), criteria)
                self.left_points_pixel_xy.append(corners2_left)
            else:
                print("Chessboard couldn't detected. Image pair: ", left_file, " and ", right_file)
                continue


def get_parser():
    save_dir = "configs/lenacv-camera"
    left_file = "configs/lenacv-camera/left_cam.yml"
    right_file = "configs/lenacv-camera/right_cam.yml"
    left_prefix = "left"
    right_prefix = "right"
    left_dir = "data/lenacv-camera"
    right_dir = "data/lenacv-camera"
    image_format = "png"
    width = 8
    height = 11
    square_size = 20
    parser = argparse.ArgumentParser(description='Camera calibration')
    parser.add_argument('--left_file', type=str, default=left_file, help='left matrix file')
    parser.add_argument('--right_file', type=str, default=right_file, help='right matrix file')
    parser.add_argument('--left_prefix', type=str, default=left_prefix, help='left image prefix')
    parser.add_argument('--right_prefix', type=str, default=right_prefix, help='right image prefix')
    parser.add_argument('--left_dir', type=str, default=left_dir, help='left images directory path')
    parser.add_argument('--right_dir', type=str, default=right_dir, help='right images directory path')
    parser.add_argument('--image_format', type=str, default=image_format, help='image format, png/jpg')
    parser.add_argument('--width', type=int, default=width, help='chessboard width size')
    parser.add_argument('--height', type=int, default=height, help='chessboard height size')
    parser.add_argument('--square_size', type=float, default=square_size, help='chessboard square size')
    parser.add_argument('--save_dir', type=str, default=save_dir, help='YML file to save stereo calibration matrices')
    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()
    print("args={}".format(args))
    calibrator = Calibrator()
    calibrator.stereo_calibrate(args.left_file,
                                args.left_dir,
                                args.left_prefix,
                                args.right_file,
                                args.right_dir,
                                args.right_prefix,
                                args.image_format,
                                args.save_dir,
                                args.square_size,
                                args.width,
                                args.height)
