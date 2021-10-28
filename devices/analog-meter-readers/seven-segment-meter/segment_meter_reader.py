import datetime
import json
import os
import time

import cv2
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from paddleocr import PaddleOCR, draw_ocr

load_dotenv()


def save_frame_camera(cap):
    _, frame = cap.read()
    return frame


def read_meter(frame):
    cv2.imwrite("./tmp/image.png", frame)
    img_path = "./tmp/image.png"

    ocr = PaddleOCR(lang="en", use_gpu=False)
    result = ocr.ocr(img_path)
    print(f"Result: {result}")
    return result[0][1][0] if len(result) else None


def post_sensing_value(sensing_value):
    body = json.dumps(
        {
            "sensor_id": "voltMeter001",
            "sensing_value": sensing_value,
            "timestamp": int(time.mktime(datetime.datetime.now().timetuple())),
        }
    )

    client = mqtt.Client()
    client.username_pw_set(os.getenv("MQTT_USER"), password=os.getenv("MQTT_PASSWORD"))
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLSv1_2, ciphers=None)
    client.tls_insecure_set(True)
    client.connect(os.getenv("MQTT_BROKER_HOST"), 8883)
    client.publish(os.getenv("MQTT_TOPIC"), body)
    client.disconnect()


cap = cv2.VideoCapture(0)
time.sleep(3)

while True:
    frame = save_frame_camera(cap)
    # If want to you use a sample image, please uncomment the following line:
    # frame = cv2.imread("./img/sample.jpg")

    sensing_value = read_meter(frame)
    print(f"Sensing value: {sensing_value}.")

    if sensing_value:
        post_sensing_value(sensing_value)

    time.sleep(30)
