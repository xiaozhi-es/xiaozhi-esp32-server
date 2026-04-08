# Guía de uso de puntos de acceso MCP

Este tutorial usa como ejemplo la función de calculadora MCP de código abierto publicada por Xia Ge y explica cómo conectar tu propio servicio MCP personalizado a tu punto de acceso.

El requisito previo de este tutorial es que tu `xiaozhi-server` ya tenga habilitada la función de punto de acceso MCP. Si todavía no la has activado, puedes hacerlo primero siguiendo [este tutorial](./mcp-endpoint-enable.md).

# Cómo añadir a un agente una función MCP sencilla, por ejemplo una calculadora

### Si usas un despliegue completo
Si usas un despliegue completo, entra en el panel de control, ve a `智能体管理`, haz clic en `配置角色` y, a la derecha de `意图识别`, verás un botón `编辑功能`.

Haz clic en ese botón. En la ventana emergente, en la parte inferior, verás `MCP接入点`. Normalmente aparecerá la `MCP接入点地址` de ese agente. A continuación vamos a ampliar ese agente con una función de calculadora basada en tecnología MCP.

Esta `MCP接入点地址` es muy importante; la vas a necesitar enseguida.

### Si usas un despliegue de un solo módulo
Si usas un despliegue de un solo módulo y ya configuraste la dirección del punto de acceso MCP en el archivo de configuración, normalmente al arrancar se mostrarán logs similares a estos:
```
250705[__main__]-INFO-初始化组件: vad成功 SileroVAD
250705[__main__]-INFO-初始化组件: asr成功 FunASRServer
250705[__main__]-INFO-OTA接口是          http://192.168.1.25:8002/xiaozhi/ota/
250705[__main__]-INFO-视觉分析接口是     http://192.168.1.25:8002/mcp/vision/explain
250705[__main__]-INFO-mcp接入点是        ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket地址是    ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-=======上面的地址是websocket协议地址，请勿用浏览器访问=======
250705[__main__]-INFO-如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
250705[__main__]-INFO-=============================================================
```

Como se ve arriba, el valor `ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc` que aparece tras `mcp接入点是` es tu `MCP接入点地址`.

Esta `MCP接入点地址` es muy importante; la vas a necesitar enseguida.

## Paso 1: descargar el código del proyecto de calculadora MCP de Xia Ge

Abre en el navegador el [proyecto de calculadora](https://github.com/78/mcp-calculator) escrito por Xia Ge.

En la página, busca el botón verde `Code`, ábrelo y verás el botón `Download ZIP`.

Haz clic para descargar el código fuente comprimido. Después de descargarlo y descomprimirlo, es posible que el directorio se llame `mcp-calculatorr-main`.
Debes renombrarlo a `mcp-calculator`. A continuación entraremos en el directorio del proyecto desde la línea de comandos e instalaremos sus dependencias.


```bash
# Entrar en el directorio del proyecto
cd mcp-calculator

conda remove -n mcp-calculator --all -y
conda create -n mcp-calculator python=3.10 -y
conda activate mcp-calculator

pip install -r requirements.txt
```

## Paso 2: arrancar el servicio

Antes de arrancar, copia primero la dirección del punto de acceso MCP desde el agente de tu panel de control.

Por ejemplo, la dirección MCP de mi agente es:
```
ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Ahora introduce este comando:

```bash
export MCP_ENDPOINT=ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
```

Cuando lo hayas hecho, inicia el programa:

```bash
python mcp_pipe.py calculator.py
```

### Si usas despliegue con panel de control
Después de arrancarlo, vuelve al panel de control y pulsa para refrescar el estado de conexión MCP. Entonces verás la lista de funciones ampliadas.

### Si usas un despliegue de un solo módulo
Si usas un despliegue de un solo módulo, cuando el dispositivo se conecte aparecerán logs como estos, lo que indica que se ha hecho correctamente:

```
250705 -INFO-正在初始化MCP接入点: wss://2662r3426b.vicp.fun/mcp_e 
250705 -INFO-发送MCP接入点初始化消息
250705 -INFO-MCP接入点连接成功
250705 -INFO-MCP接入点初始化成功
250705 -INFO-统一工具处理器初始化完成
250705 -INFO-MCP接入点服务器信息: name=Calculator, version=1.9.4
250705 -INFO-MCP接入点支持的工具数量: 1
250705 -INFO-所有MCP接入点工具已获取，客户端准备就绪
250705 -INFO-工具缓存已刷新
250705 -INFO-当前支持的函数列表: [ 'get_time', 'get_lunar', 'play_music', 'get_weather', 'handle_exit_intent', 'calculator']
```
Si incluye `'calculator'`, significa que el dispositivo podrá invocar la herramienta de calculadora a través del reconocimiento de intención.
