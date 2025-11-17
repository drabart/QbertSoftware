import pyrealsense2 as rs
import numpy as np
import cv2

cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)  # make it resizable
cv2.setWindowProperty('RealSense', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

pipeline = rs.pipeline()
config = rs.config()

# Depth stream at max resolution for D415
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 6)
# Color stream at max resolution for D415
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 6)

pipeline.start(config)

try:
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # depth_image is 16-bit in mm
        min_dist = 300  # 30 cm
        max_dist = 500  # 50 cm

        # Create a mask for the range
        mask = (depth_image >= min_dist) & (depth_image <= max_dist)

        # Scale only the masked area to 0-255
        scaled = np.zeros_like(depth_image, dtype=np.uint8)
        scaled[mask] = np.clip((depth_image[mask] - min_dist) * 255 / (max_dist - min_dist), 0, 255)

        # Apply colormap
        depth_colormap = cv2.applyColorMap(scaled, cv2.COLORMAP_HSV)

        # Make everything outside the range a single color (e.g., black)
        depth_colormap[~mask] = (0, 0, 0)  # BGR

        # Resize depth colormap to match color for display
        depth_colormap = cv2.resize(depth_colormap, (color_image.shape[1], color_image.shape[0]))

        images = np.hstack((color_image, depth_colormap))
        cv2.imshow('RealSense', images)

        if cv2.waitKey(1) == 27:
            break
finally:
    pipeline.stop()
    cv2.destroyAllWindows()
