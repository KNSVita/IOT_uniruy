import network
import time

# Função para conectar ao Wi-Fi
def conecta_wifi(ssid, senha):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print('Conectando à rede Wi-Fi...')
        wlan.connect(ssid, senha)

        # Aguarda a conexão
        tentativas = 0
        while not wlan.isconnected() and tentativas < 10:
            print('.', end='')
            time.sleep(1)
            tentativas += 1

    if wlan.isconnected():
        print('\nConectado com sucesso!')
        print('IP:', wlan.ifconfig()[0])
        return wlan.ifconfig()[0]
    else:
        print('\nFalha ao conectar no Wi-Fi.')
        return None

# Executa a conexão ao iniciar
SSID = 'xxx'
SENHA = 'xxx'
conecta_wifi(SSID, SENHA)
