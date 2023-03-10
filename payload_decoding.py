import base64

#base64_Str = 'y78KyAHAAQrQf/8='
#base64_Str = 'y8EKyAGoAQpHf/8='

#hexStr = base64.b64decode(base64_Str).hex()

# Status der Battery extrahieren
#
def getBatStatus(base64_Str):
    hexStr = base64.b64decode(base64_Str).hex()
    BatStr = hexStr[0] + hexStr[1] + hexStr[2] + hexStr[3]
    BatStatus = ((int(BatStr,16)>>14) & 0xff)
    return BatStatus

# Spannung der Batterie extrahieren
#
def getBatSpannung(base64_Str):
    hexStr = base64.b64decode(base64_Str).hex()
    BatStr = hexStr[0] + hexStr[1] + hexStr[2] + hexStr[3]
    Volt = (int(BatStr,16)& 0x03fff)/1000
    return Volt
    

# Temperatur des internen Temperatursensors Extrahieren
#
def getTempIntern(base64_Str):
    hexStr = base64.b64decode(base64_Str).hex()
    TempInternStr = hexStr[4] + hexStr[5] + hexStr[6] + hexStr[7]     
    TempIntern = int(TempInternStr,16)/100
    return TempIntern

# Feuchtewert des internen Feuchtesensors Extrahieren
#
def getFeuchte(base64_Str):
    hexStr = base64.b64decode(base64_Str).hex()
    FeuchteStr = hexStr[8] + hexStr[9] + hexStr[10] + hexStr[11]
    Feuchte = int(FeuchteStr,16)/10
    return Feuchte

def getTempExtern(base64_Str):
    # Wenn ext > 0 dann ist ein Externer Fühler angeschlossen
    #
    hexStr = base64.b64decode(base64_Str).hex()
    extStr = hexStr[12] + hexStr[13]
    ext = int(extStr,16)
    # ext == 1 dan ist es ein Externer Temperaturfühler
    #
    if ext == 1:
        TempExStr = hexStr[14] + hexStr[15] + hexStr[16] + hexStr[17]
        TempEx = int(TempExStr,16)/100
        return TempEx
    else:
        return 0
