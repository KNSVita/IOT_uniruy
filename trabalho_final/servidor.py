import paho.mqtt.client as mqtt
import numpy as np
import dlib
import cv2
import os
import time

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = xxx
TOPIC_IMAGEM = "facial/kauan/imagem"
TOPIC_RESULTADO = "facial/kauan/resultado"

SHAPE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FACE_REC_MODEL_PATH = "dlib_face_recognition_resnet_model_v1.dat"

face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
face_rec_model = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)

def get_face_encoding(image_np):
    rgb_img = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    faces = face_detector(rgb_img, 1)
    if len(faces) == 0:
        return []
    encodings = []
    for face in faces:
        shape = shape_predictor(rgb_img, face)
        face_descriptor = face_rec_model.compute_face_descriptor(rgb_img, shape)
        encodings.append(np.array(face_descriptor))
    return encodings

KNOWN_FACES_DIR = "known_faces"
known_face_encodings = []
known_face_names = []

print("Carregando rostos conhecidos usando Dlib...")
for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        image_path = os.path.join(KNOWN_FACES_DIR, filename)
        known_image_np = cv2.imread(image_path)
        encodings = get_face_encoding(known_image_np)
        if encodings:
            known_face_encodings.append(encodings[0])
            person_name = os.path.splitext(filename)[0].replace("_", " ").title()
            known_face_names.append(person_name)
            print(f"Rosto de '{person_name}' codificado e carregado.")

print(f"\nSistema pronto com {len(known_face_names)} rosto(s) conhecido(s).")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao Broker MQTT com sucesso!")
        client.subscribe(TOPIC_IMAGEM)
        print(f"Inscrito no tópico de imagens: '{TOPIC_IMAGEM}'")
    else:
        print(f"Falha ao conectar, código de retorno: {rc}\n")

def on_message(client, userdata, msg):
    print(f"\nImagem recebida no tópico '{msg.topic}' ({len(msg.payload)} bytes)")

    np_arr = np.frombuffer(msg.payload, np.uint8)
    unknown_image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    unknown_encodings = get_face_encoding(unknown_image_np)
    
    recognized_name = "Nenhum_Rosto_Detectado"
    if unknown_encodings:
        unknown_encoding = unknown_encodings[0]
        distances = np.linalg.norm(known_face_encodings - unknown_encoding, axis=1)
        best_match_index = np.argmin(distances)
        min_distance = distances[best_match_index]
        
        if min_distance < 0.6:
            recognized_name = known_face_names[best_match_index]
        else:
            recognized_name = "Desconhecido"
    
    print(f"Reconhecimento concluído: '{recognized_name}'")
    
    client.publish(TOPIC_RESULTADO, payload=recognized_name, qos=1)
    print(f"Resultado publicado no tópico: '{TOPIC_RESULTADO}'")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Conectando ao broker {MQTT_BROKER}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.loop_forever()