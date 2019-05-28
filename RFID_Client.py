#coding=utf-8
import time
import RPi.GPIO as GPIO
import signal

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

LEDPin = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LEDPin,GPIO.OUT)

# Import the TableService and Entity classes
table_service = TableService(account_name="aiiotedgeclassteama", account_key="E+fjw/Vw2OsaYYzSGbriFucx2z9Dx9zEBVL+Uc6UWHnUVuYWunA65O/nU5Qa/PVgARzq1QX2ogrp98o0ERIv3A==;EndpointSuffix=core.windows.net")

continue_reading = True

# 要加這行才能順利執行
GPIO.setwarnings(False)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "\nCtrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Welcome message
print "Press Ctrl-C to stop."

# 不斷讀取具有是否要開門命令的實體值
while continue_reading:
    # 查詢實體
    task = table_service.get_entity("Projects", "Door", "002")
    # 偵測是否為可通行的卡，是的話，則value值應為1，亮燈
    if task.Value == "1":
        GPIO.output(LEDPin,GPIO.HIGH)
    else:
        GPIO.output(LEDPin,GPIO.LOW)
    
    time.sleep(0.5)
 
