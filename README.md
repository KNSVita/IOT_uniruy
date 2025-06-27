# Sistema de Reconhecimento Facial com ESP32-CAM e MQTT

## 📜 Visão Geral do Projeto

Este é um projeto de Internet das Coisas (IoT) desenvolvido para a disciplina de "Aplicação de Cloud, IoT e Indústria 4.0 em Python" da faculdade Uniruy. O sistema demonstra uma solução de baixo custo para reconhecimento facial, superando a problemática de processar imagens em tempo real em microcontroladores com hardware limitado.

A solução utiliza um ESP32-CAM para capturar imagens, enquanto o processamento pesado de reconhecimento facial é delegado a um servidor. A comunicação entre os dispositivos é gerenciada pelo protocolo MQTT, e os resultados finais são enviados para a plataforma de nuvem ThingsBoard para visualização.

## 🏗️ Arquitetura do Sistema

O fluxo de operação do sistema é dividido nas seguintes etapas:

1.  **Captura de Imagem:** O `ESP32-CAM` é inicializado, conecta-se à rede Wi-Fi e captura uma imagem em formato JPEG.
2.  **Publicação MQTT (Imagem):** A imagem capturada é enviada como uma carga de bytes para o tópico MQTT `facial/kauan/imagem` no broker `broker.hivemq.com`.
3.  **Processamento no Servidor:** Um servidor Python (`servidor.py`) rodando em um computador está inscrito no tópico de imagens. Ao receber uma imagem, ele utiliza as bibliotecas `dlib` e `OpenCV` para:
    * Detectar faces na imagem.
    * Comparar a face detectada com um banco de dados de rostos conhecidos na pasta `known_faces`.
4.  **Publicação MQTT (Resultado):** O servidor publica o resultado (o nome da pessoa reconhecida ou "Desconhecido") no tópico MQTT `facial/kauan/resultado`.
5.  **Recebimento no ESP32:** O ESP32-CAM, que também está inscrito no tópico de resultados, recebe o nome da pessoa.
6.  **Envio para a Cloud:** Por fim, o ESP32-CAM envia o resultado recebido para um painel na plataforma **ThingsBoard** através de uma requisição HTTP POST.

## 🛠️ Tecnologias Utilizadas

* **Hardware:**
    * ESP32-CAM
    * Computador para rodar o servidor
* **Software e Bibliotecas:**
    * **Microcontrolador (MicroPython):** `umqtt.simple`, `urequests`, `camera`.
    * **Servidor (Python):** `paho-mqtt`, `dlib`, `opencv-python`, `numpy`.
* **Protocolos:**
    * MQTT
    * HTTP/HTTPS
* **Plataformas e Serviços:**
    * **Broker MQTT:** HiveMQ.
    * **Plataforma IoT:** ThingsBoard Cloud.
    * **Ambiente de Desenvolvimento:** Pycharm, Wokwi (para simulação).

---

### 📝 Nota sobre Segurança

Por questões de segurança e privacidade, dados sensíveis como senhas de Wi-Fi e tokens de acesso foram removidos dos arquivos de código (`xxx`) neste repositório. Lembre-se de preenchê-los com suas próprias credenciais durante a configuração.

---
**Autor:** Kauan Nunes Santos Vita
**Professor Orientador:** VITOR EMMANUEL ANDRADE
