import network
import time
import camera
import ubinascii
import ujson
import urequests

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
        print("PDF não localizado")

    payload = {
        "chip_id": chip_id,
        "img_b64": img_b64,
        "pdf_b64": pdf_b64
    }

    msg = ujson.dumps(payload)

    teste = msg.encode('utf-8')

    # ENVIA PARA THINGSBOARD
    TOKEN = 'xxx'
    URL = 'https://thingsboard.cloud/api/v1/{}/telemetry'.format(TOKEN)
    HEADERS = {'Content-Type': 'application/json'}

    try:
        response = urequests.post(URL,headers=HEADERS, data=teste)
        print('Enviado:', teste, '| Status', response.status_code)
        response.close()
    except Exception as e:
        print("Erro ao enviar dados:", e)
else:
    print("Falha ao capturar imagem.")
