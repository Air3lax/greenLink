### Decoding Payload from Dragino LWL02 Water Leak Sensor ###
### Uplink Payload length is 10 bytes                     ###


def get_bat_status(payload):
    voltage = int(payload[1:4], 16)/1000
    #voltage = int(voltage,16)/1000
    #status = generate_bat_status(voltage)
    return voltage

def get_total_water_leak_events(payload):
    # Number of events
    water_leak_events = int(payload[6:12], 16)
    #water_leak_events = int(water_leak_events, 16)
    return water_leak_events

def get_last_water_leak_duration(payload):
    # Duration in minutes
    last_water_leak_duration = int(payload[12:18], 16)
    return last_water_leak_duration




if __name__ == "__main__":
    print(get_bat_status("4be202000008000001"))
    print(get_total_water_leak_events("4be202000008000001"))
    print(get_last_water_leak_duration("4be202000008000001"))