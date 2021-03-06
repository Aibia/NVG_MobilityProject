from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from servomotor import servomotor as sm
import RPi.GPIO as GPIO 


@dispatcher.add_method
def gpio_pin_change(pin_num, pin_opt): 
    try:
        GPIO.setmode(GPIO.BOARD)
        if pin_opt == "OUT":
            GPIO.setup(int(pin_num), GPIO.OUT)
        elif pin_opt == "IN":
            GPIO.setup(int(pin_num), GPIO.IN)
        else:
            return False
    except Exception as e:
        return False 
    else:
        return True 


@dispatcher.add_method
def medicine_out(medicine_info): 
    try:
        for motor_name in medicine_info.keys():
            if motor_name == "id":
                continue
            sm.medicine_out(motor_name, medicine_info[motor_name])           
    except Exception as e:
        return False 
    else:
        return True 


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)
