import requests
from requests.auth import HTTPDigestAuth
import cv2
import mediapipe as mp
import time
import datetime

showCameraFeedInWindow = True
useThumbsUp = True
useMotionDetect = True

timeout = 1 # last time triggered within that time. To prevent double trigger at a time
motion_threshold = 5000

ipCamIPv4 = "192.168.1.250"
ipCamUsername = "admin"
ipCamPassword = "redacted_PW"

class DahuaClient:
    def __init__(self, username, password, address, port=80, timeout=10, motion_threshold=500, useThumbsUp=False, useMotionDetect=False):
        self.username = username
        self.password = password
        self.address = address
        self.port = port
        self.timeout = timeout
        self.motion_threshold = motion_threshold
        self.base_url = f"http://{address}:{port}"
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
        self.mp_drawing = mp.solutions.drawing_utils
        self.last_motion_time = 0
        self.last_thumbs_up_time = 0
        self.useThumbsUp = useThumbsUp
        self.useMotionDetect = useMotionDetect
        self.password = "SB212356"

    def _request(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, auth=HTTPDigestAuth(self.username, self.password))
        response.raise_for_status()
        return response.text

    def get_rtsp_url(self, channel, subtype):
        return f"rtsp://{self.username}:{self.password}@{self.address}:554/cam/realmonitor?channel={channel}&subtype={subtype}"

    def is_thumbs_up(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
        thumb_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_MCP]
        thumb_cmc = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_CMC]

        if (thumb_tip.y < thumb_ip.y < thumb_mcp.y < thumb_cmc.y and
                thumb_tip.y < thumb_mcp.y and thumb_tip.y < thumb_cmc.y):
            return True
        return False

    def view_rtsp_stream(self, channel, subtype):
        rtsp_url = self.get_rtsp_url(channel, subtype)
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            print("Error: Unable to open video stream.")
            return

        if self.useMotionDetect:
            _, first_frame = cap.read()
            first_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
            first_gray = cv2.GaussianBlur(first_gray, (21, 21), 0)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to retrieve frame. Exiting...")
                break

            if self.useMotionDetect:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                frame_delta = cv2.absdiff(first_gray, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=3)
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                current_time = time.time()
                motion_detected = False

                for contour in contours:
                    if cv2.contourArea(contour) < self.motion_threshold:
                        continue
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    motion_detected = True

                if motion_detected and current_time - self.last_motion_time > self.timeout:
                    print(f"Motion detected!. Time: {datetime.datetime.now()}")
                    self.last_motion_time = current_time

            if self.useThumbsUp:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(frame_rgb)

                current_time = time.time()
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                        if self.is_thumbs_up(hand_landmarks):
                            if current_time - self.last_thumbs_up_time > self.timeout:
                                print(f"Thumbs up detected!. Time: {datetime.datetime.now()}")
                                self.last_thumbs_up_time = current_time

            if showCameraFeedInWindow:
                cv2.imshow('RTSP Stream', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

client = DahuaClient(ipCamUsername, ipCamPassword, ipCamIPv4, timeout = timeout, useThumbsUp=useThumbsUp, useMotionDetect=useMotionDetect, motion_threshold = motion_threshold)
client.view_rtsp_stream(5, 1)
