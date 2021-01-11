import cv2
import time

def compression(fourcc, image_file_list, output_video_path):
    start_time = time.time()

    # encoder
    # fourcc = "mp4v" or "h264"
    fourcc = cv2.VideoWriter_fourcc(*fourcc)
    img = cv2.imread(image_file_list[0])  # for get frame size
    fps = 25
    video = cv2.VideoWriter(output_video_path, fourcc, fps, (img.shape[1], img.shape[0]))

    if not video.isOpened():
        print("Error: Failed to open a video")
        return None

    # compress
    for i, f in enumerate(image_file_list):
        img = cv2.imread(f)
        video.write(img)

    video.release()
    elapsed_time = time.time() - start_time

    return elapsed_time


def decompression(video_file_path, output_dir, file_name):
    start_time = time.time()

    cap = cv2.VideoCapture(video_file_path)

    # decompression
    num = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:  # Extract final frame
            if num == 1:
                cv2.imwrite(output_dir + file_name, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
        else:
            break
        num += 1

    cap.release()

    elapsed_time = time.time() - start_time
    return elapsed_time