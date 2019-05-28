#coding=utf-8
import time
import RPi.GPIO as GPIO
import MFRC522
import signal

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

#BeepPin = 24
GPIO.setmode(GPIO.BOARD)
#GPIO.setup(BeepPin,GPIO.OUT)

# Import the TableService and Entity classes
table_service = TableService(account_name="aiiotedgeclassteama", account_key="E+fjw/Vw2OsaYYzSGbriFucx2z9Dx9zEBVL+Uc6UWHnUVuYWunA65O/nU5Qa/PVgARzq1QX2ogrp98o0ERIv3A==;EndpointSuffix=core.windows.net")

continue_reading = True

# 允許通行的卡號
# PassCardUID = ("117.243.55.187", "169.193.55.187")

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "\nCtrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        CardUID = str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])
        print "Card read UID: "+ CardUID

        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            # Beep
            #try:
            #    GPIO.output(BeepPin,GPIO.HIGH)
            #    time.sleep(0.5)
            #    GPIO.output(BeepPin,GPIO.LOW)
            #except KeyboardInterrupt:
            #    print "Exception:KeyboardInterrupt"
            #    GPIO.cleanup()

            # Add the card to RFID table
            card = Entity()
            card.PartitionKey = time.strftime("%Y-%m-%d", time.localtime())
            card.RowKey = time.strftime("%H:%M:%S", time.localtime())
            card.UID = CardUID
            card.Authenticate = status
            table_service.insert_or_replace_entity("RFID", card)

            # Update the Projects table
            projectlog = Entity()
            projectlog.PartitionKey = "CheckID"
            projectlog.RowKey = "001"
            projectlog.Value = CardUID
            table_service.insert_or_replace_entity("Projects", projectlog)
            
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            #time.sleep(0.5)
        else:
            print "Authentication error"
