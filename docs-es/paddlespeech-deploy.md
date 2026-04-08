# Integración de PaddleSpeechTTS con el servicio Xiaozhi

## Puntos clave
- Ventajas: despliegue local sin conexión y alta velocidad
- Desventajas: hasta el 25 de septiembre de 2025, el modelo predeterminado es un modelo en chino y no admite conversión de texto en inglés a voz. Si el texto incluye inglés, no se emitirá sonido. Si necesitas compatibilidad simultánea con chino e inglés, tendrás que entrenar tu propio modelo.

## 1. Requisitos básicos del entorno
Sistema operativo: Windows / Linux / WSL 2

Versión de Python: 3.9 o superior (ajusta esto según la guía oficial de Paddle)

Versión de Paddle: la versión oficial más reciente   ```https://www.paddlepaddle.org.cn/install```

Herramienta de gestión de dependencias: `conda` o `venv`

## 2. Iniciar el servicio de PaddleSpeech
### 1. Descargar el código fuente del repositorio oficial de PaddleSpeech
```bash 
git clone https://github.com/PaddlePaddle/PaddleSpeech.git
```
### 2. Crear un entorno virtual
```bash

conda create -n paddle_env python=3.10 -y
conda activate paddle_env
```
### 3. Instalar Paddle
Debido a las diferencias entre arquitecturas de CPU y GPU, crea el entorno siguiendo la versión de Python compatible según la guía oficial de Paddle.
```
https://www.paddlepaddle.org.cn/install
```

### 4. Entrar en el directorio de PaddleSpeech
```bash
cd PaddleSpeech
```
### 5. Instalar PaddleSpeech
```bash
pip install pytest-runner -i https://pypi.tuna.tsinghua.edu.cn/simple

# Usa cualquiera de los siguientes comandos
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install paddlespeech -i https://pypi.tuna.tsinghua.edu.cn/simple
```
### 6. Descargar automáticamente el modelo de voz usando un comando
```bash
paddlespeech tts --input "你好，这是一次测试"
```
Este paso descargará automáticamente la caché del modelo en el directorio local `.paddlespeech/models`.

### 7. Modificar la configuración de `tts_online_application.yaml`
Consulta la ruta ```"PaddleSpeech\demos\streaming_tts_server\conf\tts_online_application.yaml"```
Abre el archivo `tts_online_application.yaml` con un editor y establece `protocol` como `websocket`.

### 8. Iniciar el servicio
```yaml
paddlespeech_server start --config_file ./demos/streaming_tts_server/conf/tts_online_application.yaml
# Comando de arranque oficial por defecto:
paddlespeech_server start --config_file ./conf/tts_online_application.yaml
```
Inicia el servicio con la ruta real de tu archivo `tts_online_application.yaml`. Si ves logs como estos, significa que el arranque fue correcto:
```
Prefix dict has been built successfully.
[2025-08-07 10:03:11,312] [   DEBUG] __init__.py:166 - Prefix dict has been built successfully.
INFO:     Started server process [2298]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8092 (Press CTRL+C to quit)
```

## 3. Modificar el archivo de configuración de Xiaozhi
### 1.```main/xiaozhi-server/core/providers/tts/paddle_speech.py```

### 2.```main/xiaozhi-server/data/.config.yaml```
Usando un despliegue de un solo módulo:
```yaml
selected_module:
  TTS: PaddleSpeechTTS
TTS:
  PaddleSpeechTTS:
      type: paddle_speech
      protocol: websocket 
      url:  ws://127.0.0.1:8092/paddlespeech/tts/streaming  # URL del servicio TTS, apuntando al servidor local [por defecto en websocket: ws://127.0.0.1:8092/paddlespeech/tts/streaming]
      spk_id: 0  # ID del locutor; normalmente 0 representa la voz predeterminada
      sample_rate: 24000  # Frecuencia de muestreo [por defecto en websocket 24000; en http 0 para selección automática]
      speed: 1.0  # Velocidad de habla; 1.0 es la velocidad normal, >1 acelera y <1 desacelera
      volume: 1.0  # Volumen; 1.0 es el valor normal, >1 aumenta y <1 reduce
      save_path:   # Ruta de guardado
```
### 3. Iniciar el servicio Xiaozhi
```py
python app.py
```
Abre `test_page.html` dentro del directorio `test` y comprueba si el lado de PaddleSpeech genera logs cuando pruebas la conexión y envías mensajes.

Referencia de logs de salida:
```
INFO:     127.0.0.1:44312 - "WebSocket /paddlespeech/tts/streaming" [accepted]
INFO:     connection open
[2025-08-07 11:16:33,355] [    INFO] - sentence: 哈哈，怎么突然找我聊天啦？
[2025-08-07 11:16:33,356] [    INFO] - The durations of audio is: 2.4625 s
[2025-08-07 11:16:33,356] [    INFO] - first response time: 0.1143045425415039 s
[2025-08-07 11:16:33,356] [    INFO] - final response time: 0.4777836799621582 s
[2025-08-07 11:16:33,356] [    INFO] - RTF: 0.19402382942625715
[2025-08-07 11:16:33,356] [    INFO] - Other info: front time: 0.06514096260070801 s, first am infer time: 0.008037090301513672 s, first voc infer time: 0.04112648963928223 s,
[2025-08-07 11:16:33,356] [    INFO] - Complete the synthesis of the audio streams
INFO:     connection closed

```
