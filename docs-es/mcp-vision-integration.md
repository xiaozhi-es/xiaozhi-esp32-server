# Guía de uso del modelo visual
Este tutorial se divide en dos partes:
- Primera parte: cómo habilitar el modelo visual cuando `xiaozhi-server` se ejecuta en modo de un solo módulo
- Segunda parte: cómo habilitar el modelo visual cuando se ejecuta en modo de despliegue completo

Antes de habilitar el modelo visual, debes preparar tres cosas:
- Necesitas un dispositivo con cámara y que ese dispositivo ya tenga implementada la llamada a la cámara en el repositorio de Xia Ge. Por ejemplo, la `立创·实战派ESP32-S3开发板`
- El firmware de tu dispositivo debe estar actualizado a la versión `1.6.6` o superior
- Ya debes haber conseguido que funcione correctamente el módulo básico de conversación

## Habilitar el modelo visual en `xiaozhi-server` con despliegue de un solo módulo

### Paso 1: confirmar la red
Como el modelo visual arrancará por defecto en el puerto `8003`,

si lo ejecutas con Docker, comprueba si tu `docker-compose.yml` ha expuesto el puerto `8003`. Si no es así, actualiza al archivo `docker-compose.yml` más reciente.

Si lo ejecutas desde código fuente, confirma que el firewall permite el puerto `8003`.

### Paso 2: elegir el modelo visual
Abre tu archivo `data/.config.yaml` y establece `selected_module.VLLM` a uno de los modelos visuales. Actualmente ya admitimos modelos visuales con interfaz de tipo `openai`. `ChatGLMVLLM` es uno de los modelos compatibles con `openai`.

```
selected_module:
  VAD: ..
  ASR: ..
  LLM: ..
  VLLM: ChatGLMVLLM
  TTS: ..
  Memory: ..
  Intent: ..
```

Supongamos que usamos `ChatGLMVLLM` como modelo visual. En ese caso primero debes entrar en [Zhipu AI](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) y solicitar una clave. Si ya la habías solicitado antes, puedes reutilizarla.

Añade esta configuración a tu archivo de configuración, o si ya existe, completa correctamente tu `api_key`.

```
VLLM:
  ChatGLMVLLM:
    api_key: 你的api_key
```

### Paso 3: iniciar el servicio `xiaozhi-server`
Si lo ejecutas desde el código fuente, usa este comando:
```
python app.py
```
Si lo ejecutas con Docker, reinicia el contenedor:
```
docker restart xiaozhi-esp32-server
```

Después del arranque se mostrarán logs como estos:

```
2025-06-01 **** - OTA接口是           http://192.168.4.7:8003/xiaozhi/ota/
2025-06-01 **** - 视觉分析接口是        http://192.168.4.7:8003/mcp/vision/explain
2025-06-01 **** - Websocket地址是       ws://192.168.4.7:8000/xiaozhi/v1/
2025-06-01 **** - =======上面的地址是websocket协议地址，请勿用浏览器访问=======
2025-06-01 **** - 如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
2025-06-01 **** - =============================================================
```

Después del arranque, abre en el navegador la dirección `视觉分析接口` que aparece en los logs y comprueba qué devuelve. Si estás en Linux y no tienes navegador, puedes ejecutar este comando:
```
curl -i 你的视觉分析接口
```

En condiciones normales debería mostrarse algo como esto:
```
MCP Vision 接口运行正常，视觉解释接口地址是：http://xxxx:8003/mcp/vision/explain
```

Ten en cuenta que, si tu despliegue es público o con Docker, debes modificar esta configuración en `data/.config.yaml`:
```
server:
  vision_explain: http://你的ip或者域名:端口号/mcp/vision/explain
```

¿Por qué? Porque la dirección de explicación visual necesita enviarse al dispositivo. Si usas una dirección de red local o una dirección interna de Docker, el dispositivo no podrá acceder a ella.

Supongamos que tu dirección pública es `111.111.111.111`; entonces `vision_explain` debería configurarse así:

```
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

Si la interfaz MCP Vision funciona correctamente y también pudiste abrir desde el navegador la `视觉解释接口地址` enviada al dispositivo, continúa con el siguiente paso.

### Paso 4: activar la función despertando el dispositivo

Dile al dispositivo: “abre la cámara y dime qué ves”

Observa la salida de logs de `xiaozhi-server` para comprobar si aparece algún error.


## Cómo habilitar el modelo visual en un despliegue completo

### Paso 1: confirmar la red
Como el modelo visual arrancará por defecto en el puerto `8003`,

si lo ejecutas con Docker, comprueba si tu `docker-compose_all.yml` tiene mapeado el puerto `8003`. Si no es así, actualiza al archivo `docker-compose_all.yml` más reciente.

Si lo ejecutas desde código fuente, confirma que el firewall permite el puerto `8003`.

### Paso 2: comprobar tu archivo de configuración

Abre `data/.config.yaml` y verifica si la estructura del archivo coincide con la de `data/config_from_api.yaml`. Si es distinta o falta alguna opción, complétala.

### Paso 3: configurar la clave del modelo visual

Primero debes entrar en [Zhipu AI](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) y solicitar una clave. Si ya la habías solicitado antes, puedes reutilizarla.

Inicia sesión en el `智控台`, haz clic en `模型配置` en el menú superior y luego en `视觉打语言模型` en la barra lateral izquierda. Busca `VLLM_ChatGLMVLLM`, pulsa editar, escribe tu clave en `API密钥` y guarda.

Después de guardar correctamente, ve al agente que quieras probar, haz clic en `配置角色` y comprueba si en `视觉大语言模型(VLLM)` está seleccionado el modelo visual que acabas de configurar. Luego guarda.

### Paso 3: iniciar el módulo `xiaozhi-server`
Si lo ejecutas desde el código fuente, usa este comando:
```
python app.py
```
Si lo ejecutas con Docker, reinicia el contenedor:
```
docker restart xiaozhi-esp32-server
```

Después del arranque se mostrarán logs como estos:

```
2025-06-01 **** - 视觉分析接口是        http://192.168.4.7:8003/mcp/vision/explain
2025-06-01 **** - Websocket地址是       ws://192.168.4.7:8000/xiaozhi/v1/
2025-06-01 **** - =======上面的地址是websocket协议地址，请勿用浏览器访问=======
2025-06-01 **** - 如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
2025-06-01 **** - =============================================================
```

Después del arranque, abre en el navegador la dirección `视觉分析接口` que aparece en los logs y comprueba qué devuelve. Si estás en Linux y no tienes navegador, puedes ejecutar este comando:
```
curl -i 你的视觉分析接口
```

En condiciones normales debería mostrarse algo como esto:
```
MCP Vision 接口运行正常，视觉解释接口地址是：http://xxxx:8003/mcp/vision/explain
```

Ten en cuenta que, si tu despliegue es público o con Docker, debes modificar esta configuración en `data/.config.yaml`:
```
server:
  vision_explain: http://你的ip或者域名:端口号/mcp/vision/explain
```

¿Por qué? Porque la dirección de explicación visual necesita enviarse al dispositivo. Si usas una dirección de red local o una dirección interna de Docker, el dispositivo no podrá acceder a ella.

Supongamos que tu dirección pública es `111.111.111.111`; entonces `vision_explain` debería configurarse así:

```
server:
  vision_explain: http://111.111.111.111:8003/mcp/vision/explain
```

Si la interfaz MCP Vision funciona correctamente y también pudiste abrir desde el navegador la `视觉解释接口地址` enviada al dispositivo, continúa con el siguiente paso.

### Paso 4: activar la función despertando el dispositivo

Dile al dispositivo: “abre la cámara y dime qué ves”

Observa la salida de logs de `xiaozhi-server` para comprobar si aparece algún error.
