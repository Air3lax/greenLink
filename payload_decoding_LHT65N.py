### Decoding Payload from Dragino LHT65N Water Leak Sensor ###
### Uplink Payload length is 10 bytes                     ###


def generate_bat_status(voltage):
    if voltage >= 3.275:
        bat_status = 'Very Good'
        return bat_status

    if voltage >= 2.85:
        bat_status = 'Good'
        return bat_status

    if voltage >= 2.425:
        bat_status = 'Low'
        return bat_status

    if voltage >= 2:
        bat_status = 'Very Low'
        return bat_status

def get_bat_info(hex_str):
    voltage = hex_str[1:4]
    voltage = int(voltage,16)/1000
    status = generate_bat_status(voltage)
    return voltage, status
    
def get_temperature(hex_str):
    temperature_internal_sensor = hex_str[5:8]
    temperature_internal_sensor = int(temperature_internal_sensor, 16)/100
    return temperature_internal_sensor

def get_humidity(hex_str):
    #print(hex_str[8:12])
    humidity_internal_sensor = hex_str[8:12]
    humidity_internal_sensor = int(humidity_internal_sensor, 16)/10
    return humidity_internal_sensor




if __name__ == '__main__':
    #hex_str = '0e640106bc800163a16d45'
    hex_str = 'cba40abb025c017fff7fff' #Example from Dragino LHT65N
    #hex_str = 'DmQBBryAAWOhbUU'
    print(get_bat_voltage(hex_str))
    print(get_temperature(hex_str))
    print(get_humidity(hex_str))
    #print(getTempExtern(hex_str))