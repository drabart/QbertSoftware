import pyrealsense2 as rs
import numpy as np
import cv2
import edge_detection

AUTO_EXPOSURE = False
RECORD_FULL = True
RECORD_RAW = False

def run_camera():
    cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('RealSense', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    fps = 6
    size = (640, 480)

    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.depth, size[0], size[1], rs.format.z16, fps)
    config.enable_stream(rs.stream.color, size[0], size[1], rs.format.bgr8, fps)

    profile = pipeline.start(config)
    color_sensor = profile.get_device().first_color_sensor()

    if AUTO_EXPOSURE:
        color_sensor.set_option(rs.option.enable_auto_exposure, 1)
        color_sensor.set_option(rs.option.enable_auto_white_balance, 1)
    else:
        color_sensor.set_option(rs.option.enable_auto_exposure, 0)
        color_sensor.set_option(rs.option.enable_auto_white_balance, 0)
        # color_sensor.set_option(rs.option.exposure, 50)
        color_sensor.set_option(rs.option.exposure, 100)
        color_sensor.set_option(rs.option.white_balance, 3000)

    color_sensor.set_option(rs.option.gain, 32)
    color_sensor.set_option(rs.option.brightness, 0)
    color_sensor.set_option(rs.option.contrast, 50)
    color_sensor.set_option(rs.option.sharpness, 50)
    color_sensor.set_option(rs.option.saturation, 50)
    color_sensor.set_option(rs.option.hue, 0)
    color_sensor.set_option(rs.option.gamma, 100)

    # optional
    color_sensor.set_option(rs.option.power_line_frequency, 1)  # 50=1, 60=2, Auto=3
    color_sensor.set_option(rs.option.auto_exposure_priority, 0)

    # Video writers (use any codec you like)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    if RECORD_FULL:
        video_writer = cv2.VideoWriter("full_recording.avi", fourcc, fps, (size[0]*2, size[1]*2))
    if RECORD_RAW:
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

            min_dist = 150
            max_dist = 300

            mask = (depth_image >= min_dist) & (depth_image <= max_dist)

            scaled = np.zeros_like(depth_image, dtype=np.uint8)
            scaled[mask] = np.clip((depth_image[mask] - min_dist) * 255 / (max_dist - min_dist), 0, 255)

            depth_colormap = cv2.applyColorMap(scaled, cv2.COLORMAP_HSV)
            depth_colormap[~mask] = (0, 0, 0)

            # Resize to match RGB size
            depth_colormap = cv2.resize(depth_colormap, (color_image.shape[1], color_image.shape[0]))

            # Write to video files
            if RECORD_RAW:
                rgb_writer.write(color_image)
                depth_writer.write(depth_colormap)

            data = edge_detection.find_lines(color_image.copy(), False)

            if data is not None:
                (threshold, edges, lines) = data
                edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

                # print(color_image.shape, edges.shape, lines.shape, depth_colormap.shape)

                top_row = np.hstack((color_image, edges))
                bottom_row = np.hstack((lines, depth_colormap))

                grid = np.vstack((top_row, bottom_row))

                if RECORD_FULL:
                    video_writer.write(grid)

                cv2.imshow("RealSense", grid)
            else:
                images = np.hstack((color_image, depth_colormap))
                cv2.imshow('RealSense', images)

            if cv2.waitKey(1) == 27:
                break

    finally:
        if RECORD_RAW:
            rgb_writer.release()
            depth_writer.release()
        if RECORD_FULL:
            video_writer.release()
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_camera()
