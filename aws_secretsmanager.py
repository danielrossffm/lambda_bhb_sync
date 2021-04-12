import base64
import boto3
import json
class AwsSecretsManager:

    def __init__(self, secret_id, region="eu-central-1"):
        client = boto3.client('secretsmanager')
        secret = client.get_secret_value(SecretId=secret_id)
        print("Finished init of SecretsManager for secret: '" + str(secret_id) + "'")
        secret = secret["SecretString"]
        self.__secret = json.loads(secret)
        self.__secret["region"] = region

    def get(self, key):
        if key in self.__secret:
            sec = self.__secret[key]
            if key in ["username", "password", "client_id","refresh_token"]: 
                sec = base64.b64decode(sec)
                sec = sec.decode("utf-8")

            return sec



