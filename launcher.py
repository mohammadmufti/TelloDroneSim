import multiprocessing
import os

def run_main():
    os.system("python main.py")

def run_video():
    os.system("python video.py")

if __name__ == "__main__":
    main_process = multiprocessing.Process(target=run_main)
    video_process = multiprocessing.Process(target=run_video)

    main_process.start()
    video_process.start()

    main_process.join()  # Wait for main to finish
    video_process.terminate()  # Stop video when main ends