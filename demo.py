
import os
import cv2
import argparse
import numpy as np
from lib import utils
from lib import camera_params, stereo_matcher


class StereoDepth(object):
    


    def __init__(self, stereo_file, width=640, height=480, filter=True):

        self.count = 0
        self.filter = filter
        self.camera_config = camera_params.get_stereo_coefficients(stereo_file)

        assert (width, height) == self.camera_config["size"], Exception("Error:{}".format(self.camera_config["size"]))

    def test_pair_image_file(self, left_file, right_file):

        frameR = cv2.imread(left_file)
        frameL = cv2.imread(right_file)
        self.task(frameR, frameL, waitKey=0)


    def capture2(self, left_video, right_video):

        capL = utils.get_video_capture(left_video)
        capR = utils.get_video_capture(right_video)
        width, height, numFrames, fps = utils.get_video_info(capL)
        width, height, numFrames, fps = utils.get_video_info(capR)
        self.count = 0
        while True:
            successL, frameL = capL.read()
            successR, frameR = capR.read()
            if not (successL and successR):
                print("No more frames")
                break
            self.count += 1
            self.task(frameL, frameR, waitKey=30)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Get key to stop stream. Press q for exit
                break
        capL.release()
        capR.release()
        cv2.destroyAllWindows()

    def get_3dpoints(self, disparity, Q, scale=1.0):

        
        # depth = stereo_matcher.get_depth(disparity, Q, scale=1.0)
        points_3d = cv2.reprojectImageTo3D(disparity, Q)
        # x, y, depth = cv2.split(points_3d)
        # baseline = abs(camera_config["T"][0])
        # baseline = 1 / Q[3, 2]  
        # fx = abs(Q[2, 3])
        # depth = (fx * baseline) / disparity
        points_3d = points_3d * scale
        points_3d = np.asarray(points_3d, dtype=np.float32)
        return points_3d

    def get_disparity(self, imgL, imgR, use_wls=True):

        dispL = stereo_matcher.get_filter_disparity(imgL, imgR, use_wls=use_wls)
        # dispL = disparity.get_simple_disparity(imgL, imgR)
        return dispL

    def get_rectify_image(self, imgL, imgR):

        # camera_params.get_rectify_transform(K1, D1, K2, D2, R, T, image_size)
        left_map_x, left_map_y = self.camera_config["left_map_x"], self.camera_config["left_map_y"]
        right_map_x, right_map_y = self.camera_config["right_map_x"], self.camera_config["right_map_y"]
        rectifiedL = cv2.remap(imgL, left_map_x, left_map_y, cv2.INTER_LINEAR, borderValue=cv2.BORDER_CONSTANT)
        rectifiedR = cv2.remap(imgR, right_map_x, right_map_y, cv2.INTER_LINEAR, borderValue=cv2.BORDER_CONSTANT)
        return rectifiedL, rectifiedR

    def task(self, frameL, frameR, waitKey=5):

        
        rectifiedL, rectifiedR = self.get_rectify_image(imgL=frameL, imgR=frameR)

        grayL = cv2.cvtColor(rectifiedL, cv2.COLOR_BGR2GRAY)
        grayR = cv2.cvtColor(rectifiedR, cv2.COLOR_BGR2GRAY)
        # Get the disparity map
        dispL = self.get_disparity(grayL, grayR, self.filter)
        points_3d = self.get_3dpoints(disparity=dispL, Q=self.camera_config["Q"])

        self.show_2dimage(grayL, grayR, points_3d, dispL, waitKey=waitKey)


    def show_2dimage(self, frameL, frameR, points_3d, dispL, waitKey=0):
        """
        :param frameL:
        :param frameR:
        :param dispL:
        :param points_3d:
        :return:
        """
        x, y, depth = cv2.split(points_3d)  # depth = points_3d[:, :, 2]
        xyz_coord = points_3d  # depth = points_3d[:, :, 2]
        depth_colormap = stereo_matcher.get_visual_depth(depth)
        dispL_colormap = stereo_matcher.get_visual_disparity(dispL)
        result = {"frameL": frameL, "frameR": frameR, "disparity": dispL_colormap, "depth": depth_colormap}
        # cv2.imshow('left', frameL)
        # cv2.imshow('right', frameR)
        cv2.imshow('disparity-color', dispL_colormap)
        cv2.imshow('depth-color', depth_colormap)
        key = cv2.waitKey(waitKey)
        self.save_images(result, self.count, key)
        if self.count <= 1:
            cv2.moveWindow("left", 700, 0)
            cv2.moveWindow("right", 1400, 0)
            cv2.moveWindow("disparity-color", 700, 700)
            cv2.moveWindow("depth-color", 1400, 700)
            cv2.waitKey(0)

    def save_images(self, result, count, key, save_dir="./data/temp"):
        """
        :param result:
        :param count:
        :param key:
        :param save_dir:
        :return:
        """
        if key == ord('q'):
            exit(0)
        elif key == ord('c') or key == ord('s'):
            file_utils.create_dir(save_dir)
            print("save image:{:0=4d}".format(count))
            cv2.imwrite(os.path.join(save_dir, "left_{:0=4d}.png".format(count)), result["frameL"])
            cv2.imwrite(os.path.join(save_dir, "right_{:0=4d}.png".format(count)), result["frameR"])
            cv2.imwrite(os.path.join(save_dir, "disparity_{:0=4d}.png".format(count)), result["disparity"])
            cv2.imwrite(os.path.join(save_dir, "depth_{:0=4d}.png".format(count)), result["depth"])


def str2bool(v):
    return v.lower() in ('yes', 'true', 't', 'y', '1')


def get_parser():
    stereo_file = "configs/lenacv-camera/stereo_cam.yml"
    # stereo_file = "configs/lenacv-camera/stereo_matlab.yml"
    left_video = None
    right_video = None
    left_video = "data/lenacv-video/left_video.avi"
    right_video = "data/lenacv-video/right_video.avi"
    left_file = "docs/left.png"
    right_file = "docs/right.png"
    parser = argparse.ArgumentParser(description='Camera calibration')
    parser.add_argument('--stereo_file', type=str, default=stereo_file, help='stereo calibration file')
    parser.add_argument('--left_video', default=left_video, help='left video file or camera ID')
    parser.add_argument('--right_video', default=right_video, help='right video file or camera ID')
    parser.add_argument('--left_file', type=str, default=left_file, help='left image file')
    parser.add_argument('--right_file', type=str, default=right_file, help='right image file')
    parser.add_argument('--filter', type=str2bool, nargs='?', default=True, help='use disparity filter')
    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()
    print("args={}".format(args))
    stereo = StereoDepth(args.stereo_file, filter=args.filter)

    if args.left_video is not None and args.right_video is not None:
        
        stereo.capture2(left_video=args.left_video, right_video=args.right_video)

    elif args.left_file and args.right_file:
        
        stereo.test_pair_image_file(args.left_file, args.right_file)
