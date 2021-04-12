import boto3
from aws_secretsmanager import AwsSecretsManager
from aws_aurora_mysql import AuroraMySqlDataBase
import requests
import json
from BHB import BHB

def printDecator(func):
    import copy; printCopy = copy.deepcopy(print)
    def internal(text): 
        printCopy(str(text))
        resp = func(str(text))        
    return internal



def lambda_handler(event, context):

    if "resource" in event: resource = event["resource"]
    else: return {"statusCode" : 400, "body" : json.dumps("Missing resource")}

    if resource == "syncBookingTable":
        bhb_secret = AwsSecretsManager("bhb-dtr-gmbh-prod")
        BHBInstance = BHB(bhb_secret)
        date_from = "2020-01-01"
        date_to = "2025-12-31"
        bookings = BHBInstance.get_bookings(date_from, date_to)

        print("\nReceived " + str(len(bookings)) + " entries from BHB.")
        print("Starting DB Import..")

        timecard_db_secret = AwsSecretsManager("timecards_database")    
        AuroraDB = AuroraMySqlDataBase(timecard_db_secret, "accounting")

        AuroraDB.beginTransaction()
        AuroraDB.deleteCompleteTable("booking")
        AuroraDB.insertDictToDB("booking",bookings)
        AuroraDB.endTransaction()