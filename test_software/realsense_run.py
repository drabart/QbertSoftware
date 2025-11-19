import pyrealsense2 as rs
import numpy as np
import cv2

def run_camera():
    cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('RealSense', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    pipeline = rs.pipeline()
    config = rs.config()

    fps = 6
    size = (1280, 720)

    config.enable_stream(rs.stream.depth, size[0], size[1], rs.format.z16, fps)
    config.enable_stream(rs.stream.color, size[0], size[1], rs.format.bgr8, fps)

    pipeline.start(config)

    # Video writers (use any codec you like)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    rgb_writer = cv2.VideoWriter("rgb_output.avi", fourcc, fps, size)
    depth_writer = cv2.VideoWriter("depth_output.avi", fourcc, fps, size)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            min_dist = 300
            max_dist = 500

            mask = (depth_image >= min_dist) & (depth_image <= max_dist)

            scaled = np.zeros_like(depth_image, dtype=np.uint8)
            scaled[mask] = np.clip((depth_image[mask] - min_dist) * 255 / (max_dist - min_dist), 0, 255)

            depth_colormap = cv2.applyColorMap(scaled, cv2.COLORMAP_HSV)
            depth_colormap[~mask] = (0, 0, 0)

            # Resize to match RGB size
            depth_colormap = cv2.resize(depth_colormap, (color_image.shape[1], color_image.shape[0]))

            # Write to video files
            rgb_writer.write(color_image)
            depth_writer.write(depth_colormap)

            images = np.hstack((color_image, depth_colormap))
            cv2.imshow('RealSense', images)

            if cv2.waitKey(1) == 27:
                break

    finally:
        rgb_writer.release()
        depth_writer.release()
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_camera()
