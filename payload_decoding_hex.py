# Written by D.Tholen, Ulmer Schokoladen GmbH & Co. KG, Wilhelmshaven
#

import base64

#base64_Str = 'y78KyAHAAQrQf/8='
#base64_Str = 'y8EKyAGoAQpHf/8='

#hexStr = base64.b64decode(base64_Str).hex()

# Status der Battery extrahieren
#
def getBatStatus(voltage):
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

    
# Spannung der Batterie extrahieren
#
def getBatSpannung(hex_str):
    voltage = hex_str[1:4]
    voltage = int(voltage,16)/1000
    status = getBatStatus(voltage)
    return voltage, status
    

# Temperatur des internen Temperatursensors Extrahieren
#
def getTempIntern(hex_str):
    temperature_internal_sensor = hex_str[5:8]
    temperature_internal_sensor = int(temperature_internal_sensor, 16)/100
    return temperature_internal_sensor

# Feuchtewert des internen Feuchtesensors Extrahieren
#
def getFeuchte(hex_str):
    #print(hex_str[8:12])
    humidity_internal_sensor = hex_str[8:12]
    humidity_internal_sensor = int(humidity_internal_sensor, 16)/10
    return humidity_internal_sensor
    return #Feuchte

def getTempExtern(hex_str):
    temperature_external_sensor = hex_str[10:14]
    temperature_external_sensor = int(temperature_external_sensor, 16)-65536
    temperature_external_sensor= temperature_external_sensor/100
    return temperature_external_sensor 
   



if __name__ == '__main__':
    #hex_str = '0e640106bc800163a16d45'
    hex_str = 'cba40abb025c017fff7fff' #Example from Dragino LHT65N
    #hex_str = 'DmQBBryAAWOhbUU'
    print(getBatSpannung(hex_str))
    print(getTempIntern(hex_str))
    print(getFeuchte(hex_str))
    #print(getTempExtern(hex_str))