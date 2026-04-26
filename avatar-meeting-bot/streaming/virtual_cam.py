# streaming/virtual_cam.py
import cv2, sys, os
from config import cfg


class VirtualCamera:
    def __init__(self):
        # Create the window once — OBS captures this window as virtual webcam
        cv2.namedWindow("Avatar - Meeting", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Avatar - Meeting", 1280, 720)
        print("[CAM] Virtual camera window created ✓")
        print("[CAM] Make sure OBS is capturing 'Avatar - Meeting' window")

    def show_idle(self):
        """
        Show static face photo while bot is processing
        This replaces the idle_loop.mp4 — no extra file needed
        """
        if os.path.exists(cfg.FACE_PHOTO):
            img = cv2.imread(cfg.FACE_PHOTO)
            if img is not None:
                img = cv2.resize(img, (1280, 720))
                cv2.imshow("Avatar - Meeting", img)
                cv2.waitKey(1)   # update window without blocking
        else:
            print(f"[CAM WARNING] Face photo not found: {cfg.FACE_PHOTO}")

    def play_audio(self, audio_path):
        """Play audio through speakers (Windows only)"""
        if not audio_path or not os.path.exists(audio_path):
            print(f"[CAM WARNING] Audio not found: {audio_path}")
            return
        if sys.platform == "win32":
            import winsound
            # SND_ASYNC = plays in background so video can start too
            winsound.PlaySound(
                audio_path,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )

    def play_video(self, video_path):
        """
        Play video in the OpenCV window
        OBS captures this window → streams to Google Meet as webcam
        Press Q to skip current video
        """
        if not video_path or not os.path.exists(video_path):
            print(f"[CAM ERROR] Video not found: {video_path}")
            return

        print(f"[CAM] Streaming: {video_path}")
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"[CAM ERROR] Cannot open video: {video_path}")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Avatar - Meeting", frame)

            # waitKey(33) = ~30fps. Press Q to skip.
            if cv2.waitKey(33) & 0xFF == ord("q"):
                print("[CAM] Video skipped by user")
                break

        cap.release()

        # Go back to showing idle photo after video ends
        self.show_idle()
        print("[CAM] Playback complete ✓")
