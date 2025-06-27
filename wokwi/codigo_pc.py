import dlib
import cv2
import numpy as np
import os
import paho.mqtt.client as mqtt
import time

#CONFIGURAÇÕES MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPICO = "facial/kauan/resultado"

#SETUP MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT | Conectado ao Broker com sucesso!")
    else:
        print(f"MQTT | Falha ao conectar, código {rc}\n")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "pc-publicador-kauan-123")
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

#CARREGA OS MODELOS
SHAPE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FACE_REC_MODEL_PATH = "dlib_face_recognition_resnet_model_v1.dat"
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
face_rec_model = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)

def codificar_face(imagem_path):
    if not os.path.exists(imagem_path): return None
    img = cv2.imread(imagem_path)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = face_detector(rgb_img, 1)
    if len(faces) == 0: return None
    shape = shape_predictor(rgb_img, faces[0])
    return np.array(face_rec_model.compute_face_descriptor(rgb_img, shape))


#PROCESSAMENTO DAS IMAGENS
print("DLIB | Iniciando reconhecimento facial...")
IMG_CONHECIDA = "kauan.jpg"
IMG_DESCONHECIDA = "reconhecer.jpg"

encoding_conhecida = codificar_face(IMG_CONHECIDA)
encoding_desconhecida = codificar_face(IMG_DESCONHECIDA)

if encoding_conhecida is not None and encoding_desconhecida is not None:
    distancia = np.linalg.norm(encoding_conhecida - encoding_desconhecida)
    resultado = "Rosto desconhecido"
    if distancia < 0.6:
        resultado = "Rosto reconhecido: Kauan Vita"

    print(f"DLIB | Resultado do reconhecimento: {resultado}")

    #ENVIO DO RESULTADO VIA MQTT
    print(f"MQTT | Publicando resultado '{resultado}' no tópico...")
    mqtt_client.publish(MQTT_TOPICO, resultado)
else:
    print("DLIB | Não foi possível processar as imagens.")

time.sleep(2)
mqtt_client.loop_stop()
print("MQTT | Conexão encerrada.")