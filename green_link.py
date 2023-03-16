# Library imports
import logging
import paho.mqtt.client as mqtt
import json
import time
import datetime
import os
import sys
import base64

# Module imports
import config_parser as cp
import telegram_send
import payload_decoding_LHT65N as lht65n
import payload_decoding_LHT52 as lht52
import payload_decoding_LWL02 as lwl02
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
        sensor_client = sensor_handler()
        
        sensor_list = []
        for i in self.config_data['lorawan_sensors']:
            sensor_list.append(i)
        print(sensor_list)
        #print(self.config_data['lorawan_sensors'][sensor_list[0]])
        # todo: maintain mqtt loop
        self.mqtt_client = mqtt.Client()
        #self.sensor_clinet = sensor_handler()
        

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
            #self.send_message("2301", 5)
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
                    self.logging('MQTT reconnected')
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
            #print(self.config_data['temperature_sensors']['greenhouse'])
            #telegram_send.send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, 'Testnachricht')
            #self.mqtt_client.publish(MQTT_TOPIC, 'OK')
            if mqtt_message['name'] in sensor_list:
                try:
                    #print(self.mqtt_message['payload'])
                    hex_payload = base64.b64decode(mqtt_message['payload']).hex()
                    fport = mqtt_message['port']
                    name = mqtt_message['name']
                    #sensor_handler.decode_payload_lwl02(self, hex_payload)
                    sensor_client.check_sensor_info(hex_payload, fport, name)
                    #pt.read_sensor(m_in, self.config_data)
                except Exception as e:
                    print(e)
            '''
            if mqtt_message['name'] == 'LHT52':
                try:
                    #print(mqtt_message['payload'])
                    fport = mqtt_message['port']
                    hex_payload = base64.b64decode(mqtt_message['payload']).hex()
                    sensor_handler.decode_payload_lht52(self, hex_payload, fport)
                    #pt.read_sensor(m_in, self.config_data)
                except Exception as e:
                    print(e)
                    '''

        
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
    
    def send_message(self, message, fport):
        print(self.config_data['lorawan_sensors']['LHT52'][1]['downlink_topic'])
        MQTT_DOWNLINK_TOPIC = self.config_data['lorawan_sensors']['LHT52'][1]['downlink_topic']
        message=json.dumps({"confirmed": 'true',"fPort": fport,"data": message})
        self.mqtt_client.publish(MQTT_DOWNLINK_TOPIC, message)
        print('Sending Downlink to IO-Controller: {}'.format(message))


class sensor_handler():

    def __init__(self) -> None:
        #telegram_send.send_telegram_message('Testnachricht')
        pass

        
    def decode_payload_lht52(self, payload, fport):
        if fport == '2':
            lht52_temperature = lht52.get_temperature(payload) # call only if fport is equal 2
            lht52_humidity = lht52.get_humidity(payload) # call only if fport is equal 2
            out= f"Temperature: {lht52_temperature} °C, Humidity: {lht52_humidity} %"
            print(out)
        if fport == '5':
            lht52_battery = lht52.get_bat_info(payload) # Call only if fport is equal 5
            out = f"LHT52 Battery : {lht52_battery}."
            print(lht52_battery)

    def decode_payload_lwl02(self, payload):
        lwl02_total_events = lwl02.get_total_water_leak_events(payload)
        lwl02_event_duration = lwl02.get_last_water_leak_duration(payload)
        lwl02_battery = lwl02.get_bat_status(payload)
        out = f"Events: {lwl02_total_events}, last Event: {lwl02_event_duration} Minutes. Battery: {lwl02_battery} Volt."
        telegram_send.send_telegram_message(out)
        print(out)

    def check_sensor_info(self, payload, fport, name):
        if name == 'LHT52':
            self.decode_payload_lht52(payload, fport)
        if name == 'LWL02':
            self.decode_payload_lwl02(payload)


if __name__ == '__main__':
    main_mqtt = mqtt_handler()
    #main_sensor = sensor_handler()
