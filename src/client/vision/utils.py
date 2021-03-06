import os
import numpy as np
from datetime import date

CURRENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__))
YML_DIR_PATH = os.path.join(CURRENT_DIR_PATH, 'ymls')
PATIENT_DATABASE_CSV_PATH = ""

def reshape(array, width):
    assert len(array) % width == 0
    height = len(array) // width
    return [array[i * width:(i+1) * width] for i in range(height)]


def get_latest_yml_path():
    dates = os.listdir(YML_DIR_PATH)
    dates.sort()
    return os.path.join(YML_DIR_PATH, "{}.yml".format(dates[-1]))





