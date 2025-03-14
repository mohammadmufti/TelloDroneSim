from djitellopy import Tello
import cv2
import time

def run_video():
    tello = Tello()
    retries = 3
    delay = 2
    for attempt in range(retries):
        try:
            tello.connect()
            print("Video process: Connection established.")
            break
        except Exception as e:
            print(f"Video process: Connection attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print("Video process: Failed to connect to Tello. Exiting.")
                return

    tello.streamon()
    frame_read = tello.get_frame_read()

    cv2.namedWindow("Tello Video Feed", cv2.WINDOW_NORMAL)
    while True:
        frame = frame_read.frame
        if frame is not None:
            cv2.imshow("Tello Video Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    tello.streamoff()
    cv2.destroyAllWindows()
    frame_read.stop()
    print("Video process: Stopped.")

if __name__ == "__main__":
    run_video()