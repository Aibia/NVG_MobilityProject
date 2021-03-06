from vision import recognizer
from vision.cascade import haar
from voice import tts, stt
from sensor import request
from db import database

SERVER_IP_ADDR = "192.168.0.12"

def main():
    while True:
        # 환자 얼굴 찾기
        patient_id = recognizer.get_id(haar.find_face())
        # 주행 멈추기 
        request.gpio_pin_change_out(SERVER_IP_ADDR)
        # 환자 정보 갖고오기 
        patient_info = database.get_patient_info(patient_id)
        medicine_info = database.get_medicine_info(patient_id)
        tts.say("Hello {}".format(patient_info["name"]))
        # 약 배출 
        request.medicine_out(SERVER_IP_ADDR, medicine_info)
        request.gpio_pin_change_in(SERVER_IP_ADDR)


if __name__ == "__main__":
    main()
