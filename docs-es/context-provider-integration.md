# Tutorial de uso de proveedores de contexto

## Resumen

Un `proveedor de contexto` añade una **fuente de datos** al contexto del prompt del sistema de Xiaozhi.

Cuando Xiaozhi se activa, el `proveedor de contexto` obtiene datos de sistemas externos y los inyecta dinámicamente en el prompt del sistema (System Prompt) del modelo grande.
Así, Xiaozhi puede “percibir” el estado de ciertos elementos del mundo justo en el momento del despertar.

Esto es esencialmente distinto de MCP y de la memoria: el `proveedor de contexto` obliga a Xiaozhi a percibir datos del mundo; la `memoria (Mem)` le permite saber de qué se habló antes; y `MCP (function_call)` se usa cuando necesita invocar una capacidad o conocimiento concreto.

Con esta función, en el instante mismo en que Xiaozhi se activa, puede “percibir”:
- El estado de sensores de salud humana (temperatura corporal, presión arterial, saturación de oxígeno, etc.)
- Datos en tiempo real de sistemas de negocio (carga del servidor, tareas pendientes, información bursátil, etc.)
- Cualquier información textual que pueda obtenerse a través de una API HTTP

**Nota**: esta función solo facilita que Xiaozhi perciba el estado de algo en el momento del despertar. Si quieres que Xiaozhi obtenga el estado de algo en tiempo real después de activarse, se recomienda combinar esta función con llamadas a herramientas MCP.

## Cómo funciona

1. **Configurar las fuentes**: el usuario configura una o varias direcciones HTTP API.
2. **Disparar la petición**: cuando el sistema construye el prompt, si detecta el marcador `{{ dynamic_context }}` en la plantilla, solicitará todas las APIs configuradas.
3. **Inyección automática**: el sistema convertirá automáticamente los datos devueltos por la API a una lista Markdown y sustituirá el marcador `{{ dynamic_context }}`.

## Especificación de la interfaz

Para que Xiaozhi pueda analizar correctamente los datos, tu API debe cumplir lo siguiente:

- **Método de petición**: `GET`
- **Cabeceras**: el sistema añadirá automáticamente el campo `device-id` al header de la petición
- **Formato de respuesta**: debe devolver JSON y contener los campos `code` y `data`

### Ejemplos de respuesta

**Caso 1: devolución de pares clave-valor**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "Temperatura del salón": "26℃",
    "Humedad del salón": "45%",
    "Estado de la puerta principal": "Cerrada"
  }
}
```
*Efecto de la inyección:*
```markdown
<context>
- **Temperatura del salón:** 26℃
- **Humedad del salón:** 45%
- **Estado de la puerta principal:** Cerrada
</context>
```

**Caso 2: devolución de una lista**
```json
{
  "code": 0,
  "data": [
    "Tienes 10 tareas pendientes",
    "La velocidad actual del coche es de 100 km/h"
  ]
}
```
*Efecto de la inyección:*
```markdown
<context>
- Tienes 10 tareas pendientes
- La velocidad actual del coche es de 100 km/h
</context>
```

## Guía de configuración

### Opción 1: configuración desde el panel de control (despliegue completo)

1. Inicia sesión en el panel de control y entra en la página **角色配置**
2. Localiza la opción **上下文源** (haz clic en el botón “编辑源”)
3. Haz clic en **添加** e introduce la dirección de tu API
4. Si tu API requiere autenticación, puedes añadir `Authorization` u otros headers en la sección **请求头**
5. Guarda la configuración

### Opción 2: configuración mediante archivo (despliegue de un solo módulo)

Edita el archivo `xiaozhi-server/data/.config.yaml` y añade el bloque `context_providers`:

```yaml
# Configuración de proveedores de contexto
context_providers:
  - url: "http://api.example.com/data"
    headers:
      Authorization: "Bearer your-token"
  - url: "http://another-api.com/data"
```

## Habilitar la función

De forma predeterminada, el archivo de plantilla del prompt del sistema (`data/.agent-base-prompt.txt`) ya incluye el marcador `{{ dynamic_context }}`, así que no necesitas añadirlo manualmente.

**Ejemplo:**

```markdown
<context>
【重要！以下信息已实时提供，无需调用工具查询，请直接使用：】
- **设备ID：** {{device_id}}
- **当前时间：** {{current_time}}
...
{{ dynamic_context }}
</context>
```

**Nota**: si no necesitas esta función, puedes optar por **no configurar ningún proveedor de contexto** o por **eliminar** el marcador `{{ dynamic_context }}` del archivo de plantilla del prompt.

## Apéndice: ejemplo de servicio Mock para pruebas

Para facilitar las pruebas y el desarrollo, proporcionamos un script sencillo de Python que actúa como Mock Server. Puedes ejecutarlo localmente para simular una API.

**mock_api_server.py**

```python
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

# 设置端口号
PORT = 8081

class MockRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析路径和参数
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        response_data = {}
        status_code = 200

        print(f"收到请求: {path}, 参数: {query}")

        # Case 1: 模拟健康数据 (返回字典 Dict)
        # 路径参数风格: /health
        # device_id 从 Header 获取
        if path == "/health":
            device_id = self.headers.get("device-id", "unknown_device")
            print(f"device_id: {device_id}")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "测试设备ID": device_id,
                    "心率": "80 bpm",
                    "血压": "120/80 mmHg",
                    "状态": "良好"
                }
            }

        # Case 2: 模拟新闻列表 (返回列表 List)
        # 无参数: /news/list
        elif path == "/news/list":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": [
                    "今日头条：Python 3.14 发布",
                    "科技新闻：AI 助手改变生活",
                    "本地新闻：明日有大雨，记得带伞"
                ]
            }

        # Case 3: 模拟天气简报 (返回字符串 String)
        # 无参数: /weather/simple
        elif path == "/weather/simple":
            response_data = {
                "code": 0,
                "msg": "success",
                "data": "今日晴转多云，气温 20-25 度，空气质量优，适合出行。"
            }

        # Case 4: 模拟设备详情 (Query参数风格)
        # 参数风格: /device/info
        # device_id 从 Header 获取
        elif path == "/device/info":
            device_id = self.headers.get("device-id", "unknown_device")
            response_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "查询方式": "Header参数",
                    "设备ID": device_id,
                    "电量": "85%",
                    "固件": "v2.0.1"
                }
            }
        
        # Case 5: 404 Not Found
        else:
            status_code = 404
            response_data = {"error": "接口不存在"}

        # 发送响应
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

# 启动服务
# 允许地址重用，防止快速重启报错
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), MockRequestHandler) as httpd:
    print(f"==================================================")
    print(f"Mock API Server 已启动: http://localhost:{PORT}")
    print(f"可用接口列表:")
    print(f"1. [字典] http://localhost:{PORT}/health")
    print(f"2. [列表] http://localhost:{PORT}/news/list")
    print(f"3. [文本] http://localhost:{PORT}/weather/simple")
    print(f"4. [参数] http://localhost:{PORT}/device/info")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
```
