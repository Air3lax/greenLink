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
import payload_decoding_LHT65N as lht65n
#import process_tempsensor as pt


class mqtt_handler():
    def __init__(self) -> None:
        self.scriptDir = os.path.dirname(os.path.realpath(__file__))
        print('INIT')
        self.logging('Started')
        try:
            self.config_data = cp.read_config()
            self.logging('Reading config-file _settings.json successfull')
        except Exception as error:
            self.logging('Error reading config-file: _settings.json, {}'.format(error))
        MQTT_SERVER_IP = self.config_data['mqtt_credentials']['ip']
        MQTT_SERVER_PORT = self.config_data['mqtt_credentials']['port']
        MQTT_UPLINK_TOPIC = self.config_data['mqtt_credentials']['uplink_topic']
        TELEGRAM_TOKEN = self.config_data['telegram_credentials']['token']
        TELEGRAM_CHAT_ID = self.config_data['telegram_credentials']['chat_id']
 
        # todo: maintain mqtt loop
        self.mqtt_client = mqtt.Client()

        def on_connect_mqtt(client, userdata, flags, rc):
            #self.connected = 0
            if rc == 0:
                #res = client.subscribe('v3/+/devices/+/up')
                ##res = client.subscribe('application/2/device/a840418431834bae/rx')
                res = client.subscribe(MQTT_UPLINK_TOPIC)
                if res[0] != mqtt.MQTT_ERR_SUCCESS:
                    raise RuntimeError("the client is not connected")
            print("Connected with result code:"+str(rc))
            self.logging('MQTT connected to {}, {} with result code {} on topic: {}'.format(MQTT_SERVER_IP, MQTT_SERVER_PORT, rc, MQTT_UPLINK_TOPIC))
            self.connected = True
            return rc
            
        def on_disconnect_mqtt(client, userdata, rc):
            print('Server Disonnected!')
            connected = False
            self.logging('MQTT disconnected, trying to re-connect to {}, {}, {}'.format(MQTT_SERVER_IP, MQTT_SERVER_PORT, MQTT_UPLINK_TOPIC))
            while connected == False:
                try:
                    self.mqtt_client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 10)
                    self.mqtt_client.connect()
                    time.sleep(1)
                    print('Server reconnected!')
                    self.logging('MQTT re-connected')
                    break
                except Exception as e:
                    print(e)
                    print('Trying to reconnect to mqtt-Server...')
                    #self.logging('MQTT trying to re-connect to {}, {}, {}'.format(MQTT_SERVER_IP, MQTT_SERVER_PORT, MQTT_UPLINK_TOPIC))
                    time.sleep(1)
                    pass
        
        def on_message_mqtt(client, userdata, msg):
            # Read Config on every mqtt-message.
            #self.get_config()
            m_decode = str(msg.payload.decode("utf-8", "ignore"))
            mqtt_message = json.loads(m_decode)  # decode json data
            # Get mqtt-data, check which Application has sent e.g. 'Temperaturen'
            print(self.config_data['temperature_sensors']['greenhouse'])
            #telegram_send.send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, 'Testnachricht')
            #self.mqtt_client.publish(MQTT_TOPIC, 'OK')
            try:
                print(mqtt_message['payload'])
                sensor_handler.decode_payload(self, mqtt_message['payload'])
                #pt.read_sensor(m_in, self.config_data)
            except Exception as e:
                print(e)
        
        self.mqtt_client.on_connect = on_connect_mqtt
        self.mqtt_client.on_message = on_message_mqtt
        self.mqtt_client.on_disconnect = on_disconnect_mqtt
        self.mqtt_client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 10)
        self.mqtt_client.loop_forever()
    
    def logging(self, entry):
        now                 = datetime.datetime.now()
        #print(now)
        time_now            = now.strftime("%H:%M:%S")
        date_now            = now.date()
        with open (self.scriptDir + '/_'+ 'log.txt', mode ='a+') as file:
            file.write(str(date_now)+' ' + time_now +', ' + str(entry) + '\n')


class sensor_handler():
    def decode_payload(self, payload):
        lht65_temperature = lht65n.get_temperature(payload)
        lht65_humidity = lht65n.get_humidity(payload)
        lht65_battery = lht65n.get_bat_info(payload)
        print(lht65_temperature, lht65_humidity, lht65_battery)


if __name__ == '__main__':
    main_mqtt = mqtt_handler()
