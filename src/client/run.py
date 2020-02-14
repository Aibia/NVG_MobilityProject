import os
import signal
import time
import subprocess
from multiprocessing import Process
from aiy.board import Board, Led
from client.db import database
from client.vision import recognizer
from client.sensor import servomotor, request
from client.voice import tts, stt
from client import logger, config



class Client:
    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super( Client, self).__new__(self)
        return self.instance


    def __init__(self):
        self.__web_server_proc = Process(target=(self.__webserver__))
        self.__nasa_proc = Process(target=self.__nasa__)


    def __webserver__(self):
        if self.__web_server_proc.is_alive():
            logger.log.info("Error Client is running")
            return False

        with Board() as board:
            proc = subprocess.Popen(['python3', config.APP_PATH])
            time.sleep(5)
            board.led.state = Led.ON
        return True 


    def __nasa__(self): 
        if self.__nasa_proc.is_alive():
            logger.log.info("Error Client is already running")
            return False

        logger.log.info("Start running client app")

        while True:
            try:
                # 환자 얼굴 찾기
                patient_id, confidence = recognizer.find_patient()
                if patient_id == -1:
                    continue
                logger.log.info("Patient found patient_id : {} confidence : {}".format(patient_id, confidence))
                # 주행 멈추기 
                logger.log.info(" Stop running ...")
                ret = request.gpio_pin_change_out()
                time.sleep(10)
                if ret["status"] == False:
                    logger.log.debug("Error Can't Stop Running")
                    request.gpio_pin_change_in()
                    continue
                # 환자 정보 갖고오기 
                patient_info = database.get_patient_info(patient_id)
                medicine_info = database.get_medicine_info(patient_id)
                if patient_info['name'] == "":
                    logger.log.debug("No Patient Found {}".format(patient_id))
                    time.sleep(3)
                    request.gpio_pin_change_in()
                    continue
                if config.CLOUD_TTS_ON:
                    tts.clova_tts("안녕하세요 {}님".format(patient_info["name"]))
                else:
                    tts.say("안녕하세요 {}님".format(patient_info["name"]))
                # 약 배출 
                servomotor.medicine_out(medicine_info)
                time.sleep(3)
                request.gpio_pin_change_in()
            except Exception as e:
                logger.log.debug("{}".format(e))


    def is_alive(self):
        return self.__nasa_proc.is_alive()

    
    def start(self):
        self.__web_server_proc.start()
        self.__nasa_proc.start()
        return True


    def stop(self, sig, frame):
        if self.__web_server_proc.is_alive():
            os.kill(self.__web_server_proc.pid, 9)
            logger.log.info("Web Server Stopped!")
            with Board() as board:
                board.led.state = Led.OFF
        if self.__nasa_proc.is_alive():
            self.__nasa_proc.terminate()
            logger.log.info("NASA App Stopped!")
        return True
        

signal.signal(signal.SIGINT, Client().stop)
client = Client()
client.start()