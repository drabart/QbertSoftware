import cv2
import edge_detection
import datetime

def run_detection(video):
    # make timestamp string
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # build file names
    thresholded_path = f"output/thresholded_{ts}.avi"
    edges_path       = f"output/edges_{ts}.avi"
    lines_path       = f"output/lines_{ts}.avi"

    # set your encoding and frame size
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    fps = 3
    size = (640, 480)

    thresholded_video = cv2.VideoWriter(thresholded_path, fourcc, fps, size, isColor=False)
    edges_video       = cv2.VideoWriter(edges_path, fourcc, fps, size, isColor=False)
    lines_video       = cv2.VideoWriter(lines_path, fourcc, fps, size)

    try:
        while True:
            ret, frame = video.read()
            if not ret:
                break  # end of file

            detected = edge_detection.find_lines(frame)
            if detected is None:
                continue

            (threshold, edges, geometric_lines) = detected

            thresholded_video.write(threshold)
            edges_video.write(edges)
            lines_video.write(geometric_lines)

            # process frame here
            # e.g. show it:
            # cv2.imshow("frame", frame)

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

    finally:
        thresholded_video.release()
        edges_video.release()
        lines_video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        cap = cv2.VideoCapture("cable_videos/rgb_output2.avi")

        if not cap.isOpened():
            print("Cannot open file")
            exit()

        run_detection(cap)
    finally:
        cap.release()
