import time
import camera
import ujson
import urequests
import urandom
from umqtt.simple import MQTTClient
import gc
import network

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
THINGSBOARD_TOKEN = "xxx"

# Configurações MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_CLIENT_ID = f"esp32-cam-kauan-{urandom.getrandbits(16)}"
TOPIC_IMAGEM = "facial/kauan/imagem"
TOPIC_RESULTADO = "facial/kauan/resultado"

resultado_recebido = False


# Configuração do Wi-Fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
while not sta_if.isconnected():
    time.sleep(1)
print("Wi-Fi conectado. IP:", sta_if.ifconfig()[0])

def on_mqtt_message(topic, msg):
    global resultado_recebido
    try:
        nome_reconhecido = msg.decode('utf-8')
        print(f"\n[MQTT] Resultado recebido: '{nome_reconhecido}'")

        # Envia o resultado para o ThingsBoard via HTTP
        url = f'https://thingsboard.cloud/api/v1/{THINGSBOARD_TOKEN}/telemetry'
        headers = {'Content-Type': 'application/json'}
        payload = {'rosto_reconhecido': nome_reconhecido}
        
        print("[HTTP] Enviando para o ThingsBoard...")
        response = urequests.post(url, headers=headers, data=ujson.dumps(payload))
        
        print(f'[HTTP] Status: {response.status_code}, Resposta: {response.text}')
        response.close()

        resultado_recebido = True

    except Exception as e:
        print(f"ERRO ao processar mensagem MQTT ou enviar para o ThingsBoard: {e}")

def init_camera():
    print("Iniciando a câmera...")
    gc.collect()
    try:
        camera.framesize(5)    # QQVGA (160x120)
        camera.pixformat(1)    # JPEG
        camera.quality(10)     # Qualidade
        camera.init()
        time.sleep(1)
        print("Câmera pronta.")
    except Exception as e:
        print(f"Erro: {e}")

def connect_mqtt():

    print("Conectando ao Broker MQTT...")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    client.set_callback(on_mqtt_message)
    client.connect()
    client.subscribe(TOPIC_RESULTADO)
    print(f"Conectado como '{MQTT_CLIENT_ID}' e inscrito no tópico: '{TOPIC_RESULTADO}'")
    return client


client = connect_mqtt()
init_camera()
print("\n--- Sistema pronto. Iniciando ciclo de reconhecimento. ---\n")

while True:
    try:
        gc.collect()
        
        resultado_recebido = False
        
        print("Capturando imagem...")
        img_bytes = camera.capture()

        if img_bytes:
            print(f"Publicando imagem ({len(img_bytes)} bytes) no tópico '{TOPIC_IMAGEM}'...")
            client.publish(TOPIC_IMAGEM, img_bytes)
        else:
            print("Falha ao capturar imagem.")
            time.sleep(5)
            continue

        print("Aguardando resultado do servidor...")
        timeout_counter = 0
        while not resultado_recebido and timeout_counter < 15:
            client.check_msg()
            time.sleep(1)
            timeout_counter += 1
        
        if not resultado_recebido:
            print("Tempo de espera esgotado. Nenhum resultado recebido do servidor.")

        print("\n--- Ciclo concluído. Próxima captura em 60 segundos. ---\n")
        time.sleep(60)

    except OSError as e:
        print(f"ERRO de conexão MQTT: {e}. Tentando reconectar...")
        try:
            client.disconnect()
        except:
            pass
        client = connect_mqtt()
    except Exception as e:
        print(f"Ocorreu um erro inesperado no loop principal: {e}")
        time.sleep(10)