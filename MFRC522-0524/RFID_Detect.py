import time
import RPi.GPIO as GPIO
import MFRC522
import signal

from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

GPIO.setmode(GPIO.BOARD)

# Import the TableService and Entity classes
table_service = TableService(account_name="aiiotedgeclassteama", account_key="E+fjw/Vw2OsaYYzSGbriFucx2z9Dx9zEBVL+Uc6UWHnUVuYWunA65O/nU5Qa/PVgARzq1QX2ogrp98o0ERIv3A==;EndpointSuffix=core.windows.net")

continue_reading = True

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
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            # Add the card to RFID table
            card = Entity()
            card.PartitionKey = "2019"
            card.RowKey = time.time()
            card.UID = str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
            card.Authenticate = status
            table_service.insert_or_replace_entity("RFID", card)
            
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print "Authentication error"
