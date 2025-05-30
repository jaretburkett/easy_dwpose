import math

import cv2
import numpy as np

eps = 0.01


def draw_bodypose(canvas, candidate, subset):
    H, W, C = canvas.shape
    candidate = np.array(candidate)
    subset = np.array(subset)

    stickwidth = 4

    limbSeq = [
        [2, 3],
        [2, 6],
        [3, 4],
        [4, 5],
        [6, 7],
        [7, 8],
        [2, 9],
        [9, 10],
        [10, 11],
        [2, 12],
        [12, 13],
        [13, 14],
        [2, 1],
        [1, 15],
        [15, 17],
        [1, 16],
        [16, 18],
        [3, 17],
        [6, 18],
    ]

    colors = [
        [255, 0, 0],
        [255, 85, 0],
        [255, 170, 0],
        [255, 255, 0],
        [170, 255, 0],
        [85, 255, 0],
        [0, 255, 0],
        [0, 255, 85],
        [0, 255, 170],
        [0, 255, 255],
        [0, 170, 255],
        [0, 85, 255],
        [0, 0, 255],
        [85, 0, 255],
        [170, 0, 255],
        [255, 0, 255],
        [255, 0, 170],
        [255, 0, 85],
    ]

    for i in range(17):
        for n in range(len(subset)):
            index = subset[n][np.array(limbSeq[i]) - 1]
            if -1 in index:
                continue
            Y = candidate[index.astype(int), 0] * float(W)
            X = candidate[index.astype(int), 1] * float(H)
            
            # Check if any point is outside the image boundaries
            if (Y[0] < 0 or Y[0] >= W or X[0] < 0 or X[0] >= H or 
                Y[1] < 0 or Y[1] >= W or X[1] < 0 or X[1] >= H):
                continue
                
            mX = np.mean(X)
            mY = np.mean(Y)
            length = ((X[0] - X[1]) ** 2 + (Y[0] - Y[1]) ** 2) ** 0.5
            angle = math.degrees(math.atan2(X[0] - X[1], Y[0] - Y[1]))
            polygon = cv2.ellipse2Poly((int(mY), int(mX)), (int(length / 2), stickwidth), int(angle), 0, 360, 1)
            cv2.fillConvexPoly(canvas, polygon, colors[i])

    canvas = (canvas * 0.6).astype(np.uint8)

    for i in range(18):
        for n in range(len(subset)):
            index = int(subset[n][i])
            if index == -1:
                continue
            x, y = candidate[index][0:2]
            x = int(x * W)
            y = int(y * H)
            # Check if point is within image boundaries
            if x > eps and y > eps and x < W and y < H:
                cv2.circle(canvas, (int(x), int(y)), 4, colors[i], thickness=-1)

    return canvas


def draw_handpose(canvas, all_hand_peaks):
    import matplotlib

    H, W, C = canvas.shape
    
    # Higher threshold for hands to reduce false positives
    hand_threshold = 0.3  # Much higher than the default eps = 0.01

    edges = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 4],
        [0, 5],
        [5, 6],
        [6, 7],
        [7, 8],
        [0, 9],
        [9, 10],
        [10, 11],
        [11, 12],
        [0, 13],
        [13, 14],
        [14, 15],
        [15, 16],
        [0, 17],
        [17, 18],
        [18, 19],
        [19, 20],
    ]

    # (person_number*2, 21, 2)
    for i in range(len(all_hand_peaks)):
        peaks = all_hand_peaks[i]
        peaks = np.array(peaks)

        for ie, e in enumerate(edges):
            x1, y1 = peaks[e[0]]
            x2, y2 = peaks[e[1]]

            x1 = int(x1 * W)
            y1 = int(y1 * H)
            x2 = int(x2 * W)
            y2 = int(y2 * H)
            # Check if any point is outside the image boundaries or below threshold
            if (x1 > hand_threshold and y1 > hand_threshold and x2 > hand_threshold and y2 > hand_threshold and
                x1 < W and y1 < H and x2 < W and y2 < H):
                cv2.line(
                    canvas,
                    (x1, y1),
                    (x2, y2),
                    matplotlib.colors.hsv_to_rgb([ie / float(len(edges)), 1.0, 1.0]) * 255,
                    thickness=2,
                )

        for _, keyponit in enumerate(peaks):
            x, y = keyponit

            x = int(x * W)
            y = int(y * H)
            if x > hand_threshold and y > hand_threshold and x < W and y < H:
                cv2.circle(canvas, (x, y), 4, (0, 0, 255), thickness=-1)
    return canvas


def draw_facepose(canvas, all_lmks):
    H, W, C = canvas.shape
    for lmks in all_lmks:
        lmks = np.array(lmks)
        for lmk in lmks:
            x, y = lmk
            x = int(x * W)
            y = int(y * H)
            if x > eps and y > eps and x < W and y < H:
                cv2.circle(canvas, (x, y), 3, (255, 255, 255), thickness=-1)
    return canvas


def draw_pose(pose, height: int, width: int, include_face: bool = True, include_hands: bool = True) -> np.ndarray:
    canvas = np.zeros(shape=(height, width, 3), dtype=np.uint8)

    candidate = pose["bodies"]
    subset = pose["body_scores"]
    canvas = draw_bodypose(canvas, candidate, subset)

    if include_face:
        faces = pose["faces"]
        canvas = draw_facepose(canvas, faces)

    if include_hands:
        hands = pose["hands"]
        canvas = draw_handpose(canvas, hands)

    return canvas
