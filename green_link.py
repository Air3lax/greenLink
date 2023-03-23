# Library imports
import logging
import paho.mqtt.client as mqtt
import json
import time
import datetime
import os
import sys
import base64
from   _thread import start_new_thread

# Module imports
import config_parser as cp
import telegram_send
import payload_decoding_LHT65N as lht65n
import payload_decoding_LHT52  as lht52
import payload_decoding_LWL02  as lwl02
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
        MQTT_SERVER_IP      = self.config_data['mqtt_credentials']['ip']
        MQTT_SERVER_PORT    = self.config_data['mqtt_credentials']['port']
        MQTT_UPLINK_TOPIC   = self.config_data['mqtt_credentials']['uplink_topic']
        MQTT_USER           = self.config_data['mqtt_credentials']['user']
        MQTT_PASSWORD       = self.config_data['mqtt_credentials']['password']
        sensor_client = sensor_handler()
        sensor_list = []
        for i in self.config_data['lorawan_sensors']:
            sensor_list.append(i)
        self.mqtt_client = mqtt.Client()

        def on_connect_mqtt(client, userdata, flags, rc):
            if rc == 0:
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
                    time.sleep(1)
                    print('Server reconnected!')
                    self.logging('MQTT reconnected')
                    break
                except Exception as e:
                    print(e)
                    print('Trying to reconnect to mqtt-Server...')
                    time.sleep(1)
                    pass
        
        def on_message_mqtt(client, userdata, msg):
            m_decode = str(msg.payload.decode("utf-8", "ignore"))
            mqtt_message = json.loads(m_decode)  # decode json data
            if mqtt_message['name'] in sensor_list:
                try:
                    hex_payload = base64.b64decode(mqtt_message['payload']).hex()
                    fport = mqtt_message['port']
                    name = mqtt_message['name']
                    timestamp = mqtt_message['reported_at']
                    sensor_client.check_sensor_info(hex_payload, fport, name, timestamp)
                except Exception as e:
                    print(e)

        self.mqtt_client.on_connect = on_connect_mqtt
        self.mqtt_client.on_message = on_message_mqtt
        self.mqtt_client.on_disconnect = on_disconnect_mqtt
        self.mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.mqtt_client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 10)
        self.mqtt_client.loop_forever()
    
    def logging(self, entry):
        now                 = datetime.datetime.now()
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
        self.user_reporter = user_report()

    def decode_payload_lht52(self, payload, fport):
        if fport == '2':
            lht52_temperature = lht52.get_temperature(payload) # call only if fport is equal 2
            lht52_humidity = lht52.get_humidity(payload) # call only if fport is equal 2
            out= f"Temperature: {lht52_temperature} °C, Humidity: {lht52_humidity} %"
            telegram_send.send_telegram_message(out)
            print(out)
        if fport == '5':
            lht52_battery = lht52.get_bat_info(payload) # Call only if fport is equal 5
            out = f"LHT52 Battery : {lht52_battery}."
            print(lht52_battery)

    def decode_payload_lwl02(self, payload, timestamp):
        lwl02_total_events = lwl02.get_total_water_leak_events(payload)
        lwl02_event_duration = lwl02.get_last_water_leak_duration(payload)
        lwl02_battery = lwl02.get_bat_status(payload)
        out = f"Events: {lwl02_total_events}, last Event: {lwl02_event_duration} Minutes. Battery: {lwl02_battery} Volt."
        
        self.user_reporter.watchdog_LWL02(timestamp, lwl02_event_duration, lwl02_battery, lwl02_total_events)

    def check_sensor_info(self, payload, fport, name, timestamp):
        if name == 'LHT52':
            self.decode_payload_lht52(payload, fport)
        if name == 'LWL02' and fport == '10':
            self.decode_payload_lwl02(payload, timestamp)

class logger():
    def __init__(self) -> None:
        self.scriptDir = os.path.dirname(os.path.realpath(__file__))

    
    def logging(self, entry):
        now                 = datetime.datetime.now()
        time_now            = now.strftime("%H:%M:%S")
        date_now            = now.date()
        with open (self.scriptDir + '/_'+ 'log.txt', mode ='a+') as file:
            file.write(str(date_now)+' ' + time_now +', ' + str(entry) + '\n')

class user_report(logger, mqtt_handler):

    def __init__(self) -> None:
        super().__init__()
        import time
        self.last_notification = 0
        
        #self.TIME_BETWEEN_NOTIFICATIONS = self.config_data['lorawan_sensors']['LWL02'][1]['prompt_timeout']
        self.number_of_events = 0
        self.initial_event = False
        self.water_is_flowing = False
        self.user_was_notified = False
        self.last_duration = 0

        start_new_thread(self.timer, ())
        self.log = logger()

    def notify_user(self):
        # Use this function to send Notification to User (Telegram only so far..)
        pass

    def watchdog_LWL02(self, timestamp, event_duration, battery_state, total_events):
        # Use this function to decide to send and manage Notifications.
        # According to the motto: as much as necessary, as little as possible
        # In our case, the LWL02-Sensor is used as a waterflow-Sensor, originally it is used to detect water leakage.
        #self.config_data_mqtt = self.config_data
        #self.TIME_BETWEEN_NOTIFICATIONS = self.config_data['lorawan_sensors']['LWL02'][1]['prompt_timeout']
        self.initial_event = True
        self.water_is_flowing = True
        #self.TIME_BETWEEN_NOTIFICATIONS = 60*60
        self.last_notification = timestamp
        
        self.battery_state = battery_state
        '''
        if total_events > self.number_of_events:
            print('Waterflow active!')
            self.water_is_flowing = True
            if self.user_was_notified == True:
                telegram_send.send_telegram_message(f'Wasserlauf ist wiederhergestellt, Batt: {self.battery_state} V')
                self.tick = 0
                self.user_was_notified = False
        if total_events == self.number_of_events and event_duration >0 and event_duration != self.last_duration:
            print('Waterflow stopped!')
            self.water_is_flowing = False
        else:
            print('Status Message from LWL02 (10 Minute in-event-update).')
            '''
        self.number_of_events = total_events
        print(self.last_notification, self.last_duration, self.battery_state, total_events)
        out = f"Events: {total_events}, last Event: {self.last_duration} Minutes. Battery: {self.battery_state} Volt."
        self.log.logging(out)
        self.last_duration = event_duration
        self.tick = 0


    def timer(self):
        self.tick = 0
        #self.TIME_BETWEEN_NOTIFICATIONS = self.config_data['lorawan_sensors']['LWL02'][1]['prompt_timeout']
        while (True):
            self.tick += 1
            print(self.tick)
            try:
                if self.tick >= 10:                    
                    telegram_send.send_telegram_message(f'Wasserlauf vor {self.tick/60} Minuten ausgefallen, bitte prüfen! Batt: {self.battery_state} V.')
                    self.initial_event = False
                    self.log.logging(f'Wasserlauf vor {self.tick/60} Minuten ausgefallen, bitte prüfen!, Batt: {self.battery_state} V.')
                    while self.initial_event == False:
                        pass # Wait here until next Message from LWL02
                    else:
                        telegram_send.send_telegram_message(f'Wasserlauf wiederhergestellt! Batt: {self.battery_state} V.')
                        self.log.logging(f'Wasserlauf wiederhergestellt! Batt: {self.battery_state} V.')
            except Exception as e:
                print(e)
            time.sleep(1)
            '''
            #if self.water_is_flowing == False and self.tick > 20 and self.user_was_notified == False and self.initial_event == True:
            if self.initial_event == True:
                telegram_send.send_telegram_message(f'Wasserlauf nach {self.last_duration} Minuten vor {self.tick} Sekunden ausgefallen, Batt: {self.battery_state} V.')
                self.user_was_notified = True
            '''


            

if __name__ == '__main__':
    main_mqtt = mqtt_handler()
    #main_sensor = sensor_handler()
