import numpy as np
import cv2
from matplotlib import pyplot as plt

import os

g = os.walk("./data/rectified")

for path, dir_list, file_list in g:
    for dir_name in dir_list:
        if dir_name == 'result':
            continue
        print('loading images...')
        left_np = cv2.imread(os.path.join(path, dir_name, 'im0.png'), 0)
        right_np = cv2.imread(os.path.join(path, dir_name, 'im1.png'), 0)

        window_size = 3
        left_matcher = cv2.StereoSGBM_create(
            blockSize=3,
            P1=8 * 3 * window_size ** 2,
            P2=32 * 3 * window_size ** 2,
            disp12MaxDiff=-1,
            uniquenessRatio=10,
            speckleWindowSize=100,
            speckleRange=2,
            mode=1
        )

        right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)

        left_disp = left_matcher.compute(left_np, right_np)
        right_disp = right_matcher.compute(right_np, left_np)

        wls_filter = cv2.ximgproc.createDisparityWLSFilter(left_matcher)
        wls_filter.setLambda(8000)
        wls_filter.setSigmaColor(1.2)
        wls_filter.setDepthDiscontinuityRadius(7)  # Normal value = 7
        wls_filter.setLRCthresh(24)
        disparity = np.zeros(left_disp.shape)
        disparity = wls_filter.filter(
            left_disp, left_np, disparity, right_disp)
        confidence_np = wls_filter.getConfidenceMap()

        # normalising disparities for saving/display
        disparity_norm = disparity.astype(np.float32) / 16
        left_disp_norm = left_disp.astype(np.float32) / 16

        plt.imshow(disparity_norm)
        plt.colorbar()
        plt.savefig(
            './data/rectified/result/' +
            dir_name +
            '.png')
        plt.show()

        print("saving disparity as disparity_image_sgbm_filt.txt")
        np.savetxt(
            os.path.join(
                path,
                dir_name,
                'disparity_image_sgbm_filt.txt'),
            disparity_norm,
            fmt='%3.2f',
            delimiter=' ',
            newline='\n')

print('done')
