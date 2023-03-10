# Library imports
import logging
import paho.mqtt.client as mqtt
import json
import time
import datetime
import os
import sys

# Module imports
#import payload_decoding as pd
#import maria_db_handler as mdb
import config_parser as cp
import telegram_send
#import process_tempsensor as pt


class worker():
    def __init__(self) -> None:
        print('INIT')
        self.config_data = cp.read_config()
        MQTT_SERVER_IP = self.config_data['mqtt_credentials']['ip']
        MQTT_SERVER_PORT = self.config_data['mqtt_credentials']['port']
        MQTT_TOPIC = self.config_data['mqtt_credentials']['topic']
        TELEGRAM_TOKEN = self.config_data['telegram_credentials']['token']
        TELEGRAM_CHAT_ID = self.config_data['telegram_credentials']['chat_id']
        # todo: maintain mqtt loop
        self.mqtt_client = mqtt.Client()

        def on_connect_mqtt(client, userdata, flags, rc):
            #self.connected = 0
            if rc == 0:
                #res = client.subscribe('v3/+/devices/+/up')
                ##res = client.subscribe('application/2/device/a840418431834bae/rx')
                res = client.subscribe(MQTT_TOPIC)
                if res[0] != mqtt.MQTT_ERR_SUCCESS:
                    raise RuntimeError("the client is not connected")
            print("Connected with result code:"+str(rc))
            self.connected = True
            return rc
            
        
        def on_disconnect_mqtt(client, userdata, rc):
            print('Server Disonnected!')
            connected = False
            while connected == False:
                try:
                    self.mqtt_client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 10)
                    self.mqtt_client.connect()
                    time.sleep(1)
                    print('Server reconnected!')
                    break
                except Exception as e:
                    print(e)
                    print('Trying to reconnect to mqtt-Server...')
                    time.sleep(1)
                    pass
        
        def on_message_mqtt(client, userdata, msg):
            # Read Config on every mqtt-message.
            #self.get_config()
            m_decode = str(msg.payload.decode("utf-8", "ignore"))
            m_in = json.loads(m_decode)  # decode json data
            # Get mqtt-data, check which Application has sent e.g. 'Temperaturen'
            print(m_in)
            telegram_send.send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, 'Testnachricht')
            #self.mqtt_client.publish(MQTT_TOPIC, 'OK')
            try:
                if m_in['applicationName'] == 'Temperaturen':
                    pt.read_sensor(m_in, self.config_data)
            except:
                pass
        
        
        self.mqtt_client.on_connect = on_connect_mqtt
        self.mqtt_client.on_message = on_message_mqtt
        self.mqtt_client.on_disconnect = on_disconnect_mqtt
        self.mqtt_client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 10)
        self.mqtt_client.loop_forever()
    
    #def get_config(self):
        #self.config_data = cp.read_config()
        






if __name__ == '__main__':
    worker = worker()
