import cv2
import numpy as np
from matplotlib import pyplot as plt
from collections import Counter
import math

def line_to_general_form(x1, y1, x2, y2):
    a = y2 - y1
    b = x1 - x2
    c = x2*y1 - x1*y2
    return a, b, c

def point_to_segment(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return np.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    proj_x, proj_y = x1 + t * dx, y1 + t * dy
    return np.hypot(px - proj_x, py - proj_y)

def line_distance(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    return min(
        point_to_segment(x1, y1, x3, y3, x4, y4),
        point_to_segment(x2, y2, x3, y3, x4, y4),
        point_to_segment(x3, y3, x1, y1, x2, y2),
        point_to_segment(x4, y4, x1, y1, x2, y2)
    )

def are_lines_similar_general(line1, line2, tol=1e-6, max_dist=10):
    a1, b1, c1 = line_to_general_form(*line1)
    a2, b2, c2 = line_to_general_form(*line2)
    
    # normalize all coefficients
    norm1 = (a1**2 + b1**2 + c1**2)**0.5
    norm2 = (a2**2 + b2**2 + c2**2)**0.5

    a1, b1, c1 = a1/norm1, b1/norm1, c1/norm1
    a2, b2, c2 = a2/norm2, b2/norm2, c2/norm2

    # compare slope and position
    similar_orientation = abs(a1 - a2) < tol and abs(b1 - b2) < tol and abs(c1 - c2) < tol
    close_enough = line_distance(line1, line2) <= max_dist
    
    return similar_orientation and close_enough

def merge_lines(lines):
    merged = [False] * len(lines)
    final_lines = []

    for i, line1 in enumerate(lines[:, 0]):
        if merged[i]:
            continue

        x1_1, y1_1, x2_1, y2_1 = line1

        for j_offset, line2 in enumerate(lines[i+1:, 0]):
            j = i + 1 + j_offset  # actual index in the full array
            if merged[j]:
                continue

            if are_lines_similar_general(line1, line2, tol=0.01, max_dist=10):
                x1_2, y1_2, x2_2, y2_2 = line2
                line1 = (
                    min(x1_1, x2_1, x1_2, x2_2),
                    min(y1_1, y2_1, y1_2, y2_2),
                    max(x1_1, x2_1, x1_2, x2_2),
                    max(y1_1, y2_1, y1_2, y2_2)
                )
                merged[j] = True
                # update endpoints for further merges
                x1_1, y1_1, x2_1, y2_1 = line1

        final_lines.append([line1])

    return np.array(final_lines)

def find_lines(image, custom_processing = True):
    # Load image in grayscale
    # image = cv2.resize(image, (640, 480))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ret1, th1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    blur = cv2.GaussianBlur(gray, (5, 5), 1)
    thresholded_image = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 5)
    # ret2, thresholded_image = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    raw_edges = cv2.Canny(thresholded_image, 0, 255)

    slopes = []

    # --- Probabilistic Hough (segments) ---
    PIXEL_RESOLUTION = 1
    ANGULAR_RESOUTION = (np.pi * 2) / 200
    VOTE_THRESHOLD = 70
    geometric_lines = cv2.HoughLinesP(raw_edges, 
                                      PIXEL_RESOLUTION, 
                                      ANGULAR_RESOUTION, 
                                      VOTE_THRESHOLD, 
                                      minLineLength=30, 
                                      maxLineGap=15)
    if geometric_lines is not None:
        for line in geometric_lines:
            x1, y1, x2, y2 = line[0]

            if x2 != x1:
                slope = (y2 - y1) / (x2 - x1)
                angle = math.degrees(math.atan(slope))
            else:
                angle = 90.0  # vertical line

            slopes.append(angle)

    if geometric_lines is None:
        print("No geometric_lines found!")
        return (thresholded_image, raw_edges, image)
    
    if custom_processing:
        geometric_lines = geometric_lines.astype(float)
        geometric_lines = merge_lines(geometric_lines)
        geometric_lines = geometric_lines.astype(int)

    if geometric_lines is not None:
        for x, line in enumerate(geometric_lines):
            if not ((slopes[x] > 60 and slopes[x] < 85) or (slopes[x] < -60 and slopes[x] > -85)):
                continue
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255-slopes[x]*(255/90), slopes[x]*(255/90)), 2)
    
    return (thresholded_image, raw_edges, image)

if __name__ == "__main__":
    img = cv2.imread("train/long1.png")
    find_lines(img)
