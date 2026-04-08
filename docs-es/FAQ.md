# Preguntas frecuentes ❓

### 1、¿Por qué Xiaozhi reconoce muchas palabras en coreano, japonés o inglés cuando hablo? 🇰🇷

Sugerencia: comprueba si ya existe el archivo `model.pt` dentro de `models/SenseVoiceSmall`. Si no está, debes descargarlo. Consulta aquí: [Descargar el archivo del modelo de reconocimiento de voz](Deployment.md#模型文件)

### 2、¿Por qué aparece “TTS 任务出错 文件不存在”? 📁

Sugerencia: comprueba si instalaste correctamente las librerías `libopus` y `ffmpeg` con `conda`.

Si no las has instalado, ejecuta:

```
conda install conda-forge::libopus
conda install conda-forge::ffmpeg
```

### 3、TTS falla con frecuencia o agota el tiempo de espera ⏰

Sugerencia: si `EdgeTTS` falla con frecuencia, comprueba primero si estás usando un proxy o VPN. Si lo estás usando, prueba a desactivarlo y vuelve a intentarlo.
Si estás usando Doubao TTS de Huoshan Engine y falla a menudo, se recomienda usar la versión de pago, porque la versión de prueba solo admite 2 solicitudes concurrentes.

### 4、Puedo conectarme a mi servidor propio por Wi-Fi, pero no en modo 4G 🔐

Causa: el firmware de Xia Ge requiere una conexión segura en modo 4G.

Solución: actualmente hay dos formas de resolverlo. Puedes elegir cualquiera:

1、Modificar el código. Consulta este video: https://www.bilibili.com/video/BV18MfTYoE85

2、Configurar un certificado SSL con nginx. Consulta este tutorial: https://icnt94i5ctj4.feishu.cn/docx/GnYOdMNJOoRCljx1ctecsj9cnRe

### 5、¿Cómo mejorar la velocidad de respuesta de Xiaozhi? ⚡

La configuración predeterminada de este proyecto está pensada como una solución de bajo costo. Se recomienda que los principiantes empiecen con el modelo gratuito por defecto para resolver primero el problema de “que funcione”, y después optimicen “que vaya rápido”.
Si necesitas mejorar la velocidad de respuesta, puedes intentar sustituir distintos componentes. Desde la versión `0.5.2`, el proyecto admite configuración en streaming y, frente a las versiones anteriores, el tiempo de respuesta se ha reducido aproximadamente en `2.5 segundos`, mejorando notablemente la experiencia de uso.

| Nombre del módulo | Configuración inicial totalmente gratuita | Configuración en streaming |
|:---:|:---:|:---:|
| ASR (reconocimiento de voz) | FunASR (local) | 👍XunfeiStreamASR (streaming de Xunfei) |
| LLM (modelo grande) | glm-4-flash (Zhipu) | 👍qwen-flash (Alibaba Bailian) |
| VLLM (modelo visual grande) | glm-4v-flash (Zhipu) | 👍qwen2.5-vl-3b-instructh (Alibaba Bailian) |
| TTS (síntesis de voz) | ✅LinkeraiTTS (streaming de Lingxi) | 👍HuoshanDoubleStreamTTS (streaming de Huoshan) |
| Intent (reconocimiento de intención) | function_call (llamada a función) | function_call (llamada a función) |
| Memory (memoria) | mem_local_short (memoria local de corto plazo) | mem_local_short (memoria local de corto plazo) |

Si te interesa el tiempo consumido por cada componente, consulta el [informe de pruebas de rendimiento de los componentes de Xiaozhi](https://github.com/xinnan-tech/xiaozhi-performance-research). Puedes seguir el método de prueba del informe y medirlo en tu propio entorno.

### 6、Hablo despacio y Xiaozhi me interrumpe cuando hago pausas 🗣️

Sugerencia: busca esta sección en el archivo de configuración y aumenta el valor de `min_silence_duration_ms` (por ejemplo, a `1000`):

```yaml
VAD:
  SileroVAD:
    threshold: 0.5
    model_dir: models/snakers4_silero-vad
    min_silence_duration_ms: 700  # Si haces pausas largas al hablar, aumenta este valor
```

### 7、Tutoriales relacionados con el despliegue
1、[Cómo hacer el despliegue mínimo](./Deployment.md)<br/>
2、[Cómo hacer el despliegue completo de todos los módulos](./Deployment_all.md)<br/>
3、[Cómo desplegar la pasarela MQTT y habilitar el protocolo MQTT + UDP](./mqtt-gateway-integration.md)<br/>
4、[Cómo descargar automáticamente la última versión del proyecto, compilarla y arrancarla](./dev-ops-integration.md)<br/>
5、[Cómo integrar con Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>

### 9、Tutoriales relacionados con la compilación del firmware
1、[Cómo compilar tú mismo el firmware de Xiaozhi](./firmware-build.md)<br/>
2、[Cómo modificar la dirección OTA usando el firmware ya compilado por Xia Ge](./firmware-setting.md)<br/>
3、[Cómo configurar la actualización OTA automática del firmware en un despliegue de un solo módulo](./ota-upgrade-guide.md)<br/>

### 10、Tutoriales de ampliación
1、[Cómo habilitar el registro por número de teléfono en el panel de control](./ali-sms-integration.md)<br/>
2、[Cómo integrar Home Assistant para control domótico](./homeassistant-integration.md)<br/>
3、[Cómo habilitar el modelo visual para tomar fotos y reconocer objetos](./mcp-vision-integration.md)<br/>
4、[Cómo desplegar un punto de acceso MCP](./mcp-endpoint-enable.md)<br/>
5、[Cómo conectar un punto de acceso MCP](./mcp-endpoint-integration.md)<br/>
6、[Cómo obtener información del dispositivo con un método MCP](./mcp-get-device-info.md)<br/>
7、[Cómo habilitar el reconocimiento por huella de voz](./voiceprint-integration.md)<br/>
8、[Guía de configuración de fuentes para el plugin de noticias](./newsnow_plugin_config.md)<br/>
9、[Guía de integración de la base de conocimiento RAGFlow](./ragflow-integration.md)<br/>
10、[Cómo desplegar proveedores de contexto](./context-provider-integration.md)<br/>

### 11、Tutoriales relacionados con clonación de voz y despliegue local de voz
1、[Cómo clonar voces en el panel de control](./huoshan-streamTTS-voice-cloning.md)<br/>
2、[Cómo desplegar e integrar voz local con index-tts](./index-stream-integration.md)<br/>
3、[Cómo desplegar e integrar voz local con fish-speech](./fish-speech-integration.md)<br/>
4、[Cómo desplegar e integrar voz local con PaddleSpeech](./paddlespeech-deploy.md)<br/>

### 12、Tutoriales de pruebas de rendimiento
1、[Guía de pruebas de velocidad de cada componente](./performance_tester.md)<br/>
2、[Resultados de pruebas públicas periódicas](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>

### 13、Si tienes más preguntas, puedes contactarnos 💬

Puedes enviar tus preguntas en [issues](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues).
