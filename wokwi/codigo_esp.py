import network
import time
from umqtt_simple import MQTTClient
import urequests
import ujson
import urandom

#CONECTA NO WIFI
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASSWORD = ''


#TOKEN THINGSBOARD
ACCESS_TOKEN = "jQTgMycRWf774fcyvOfd" 

# Configurações MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPICO = "facial/kauan/resultado"
MQTT_CLIENT_ID = "esp32-kauan-{}".format(urandom.getrandbits(16))

#FUNÇÃO EXECUTADA QUANDO UMA MENSAGEM MQTT CHEGA
def on_mqtt_message(topic, msg):
    try:
        #RECEBE RESULTADO
        nome_reconhecido = msg.decode('utf-8')
        print(f"MQTT | Mensagem recebida: {nome_reconhecido}")

        #ENVIO DO RESULTADO
        url = 'https://thingsboard.cloud/api/v1/{}/telemetry'.format(ACCESS_TOKEN)
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            'face_detected': nome_reconhecido
        }
        
        print(f"HTTP | Enviando para {url}")
        print(f"HTTP | Payload: {ujson.dumps(payload)}")
        response = urequests.post(url, headers=headers, data=ujson.dumps(payload))
        
        #RESPOSTA DO SERVIDOR
        print('HTTP | Status:', response.status_code, '| Resposta:', response.text)
        response.close()

    except Exception as e:
        print(f"ERRO | Falha ao processar mensagem: {e}")

#INICIA WIFI E MQTT
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
print("WIFI | Conectando...")
while not wlan.isconnected(): time.sleep(1)
print("WIFI | Conectado!", wlan.ifconfig())

print("MQTT | Conectando ao broker...")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.set_callback(on_mqtt_message)
client.connect()
client.subscribe(MQTT_TOPICO)
print(f"MQTT | Conectado como '{MQTT_CLIENT_ID}' e inscrito no tópico: {MQTT_TOPICO}")
print("\n--- Aguardando mensagens ---")

#START
while True:
    try:
        client.check_msg()
        time.sleep(1)
    except OSError as e:
        print("ERRO | Conexão MQTT perdida. Reconectando...", e)
        client.connect()