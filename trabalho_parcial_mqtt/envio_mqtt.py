import network
import time
import camera
import ubinascii
import ujson
from umqtt.simple import MQTTClient

# Configuração do Wi-Fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
while not sta_if.isconnected():
    time.sleep(1)
print("Wi-Fi conectado. IP:", sta_if.ifconfig()[0])

#CHIP ID
chip_id = ubinascii.hexlify(network.WLAN().config('mac')[-3:]).decode().upper()

# Inicia câmera

camera.framesize(5)   # QQVGA (160x120) — menor imagem
camera.pixformat(1)   # JPEG
camera.quality(10)
camera.init()

# Captura imagem
img = camera.capture_jpg()

if img:
    # Converte para base64
    img_b64 = ubinascii.b2a_base64(img).replace(b'\n', b'').decode()

    print("Tamanho da imagem base64:", len(img_b64))

    try:
        with open("ROTEIRO DE EXTEN-IOT.pdf","rb") as f:
            pdf_bin = f.read()
            pdf_b64 = ubinascii.b2a_base64(pdf_bin).replace(b'\n', b'').decode()

    except:
        pdf_b64 = ""

    payload = {
        "chip_id": chip_id,
        "img_b64": img_b64,
        "pdf_b64": pdf_b64
    }

    msg = ujson.dumps(payload)

    teste = msg.encode('utf-8')

    # Envia via MQTT
    BROKER = "28a6f2cda33d4edd968db56415df18b6.s1.eu.hivemq.cloud"
    PORTA = 8883
    USERNAME = "grupos"
    PASSWORD = "gruposUNIRUY25.1"
    TOPICO = b"iot/entregaparcial/grupo04"
    CLIENTE_ID = b"ESP32CAM"

    try:
        cliente = MQTTClient(CLIENTE_ID, BROKER, port=PORTA, user=USERNAME, password=PASSWORD, ssl = True)
        cliente.connect()
        cliente.publish(TOPICO, teste)
        print("Dados enviados via MQTT!")
        cliente.disconnect()
    except Exception as e:
        print("Erro ao enviar dados:", e)
else:
    print("Falha ao capturar imagem.")
