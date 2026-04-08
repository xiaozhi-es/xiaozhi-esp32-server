# Guía de uso de la herramienta de pruebas de rendimiento para reconocimiento de voz, modelos de lenguaje, TTS no fluido, TTS en streaming y modelos visuales

1. Crea el directorio `data` dentro de `main/xiaozhi-server`
2. Crea el archivo `.config.yaml` dentro del directorio `data`
3. En `data/.config.yaml`, escribe los parámetros de tu reconocimiento de voz, modelo de lenguaje, TTS en streaming y modelo visual
Por ejemplo:
```
LLM:
  ChatGLMLLM:
    # 定义LLM API类型
    type: openai
    # glm-4-flash 是免费的，但是还是需要注册填写api_key的
    # 可在这里找到你的api key https://bigmodel.cn/usercenter/proj-mgmt/apikeys
    model_name: glm-4-flash
    url: https://open.bigmodel.cn/api/paas/v4/
    api_key: 你的chat-glm web key

TTS:

VLLM:

ASR:
```
4. Ejecuta `performance_tester.py` dentro de `main/xiaozhi-server`:
```
python performance_tester.py
```
