# Guía de uso de IndexStreamTTS

## Preparación del entorno
### 1. Clonar el proyecto
```bash 
git clone https://github.com/Ksuriuri/index-tts-vllm.git
```
Entra en el directorio descomprimido:
```bash
cd index-tts-vllm
```
Cambia a la versión especificada (una versión histórica que usa VLLM `0.10.2`):
```bash
git checkout 224e8d5e5c8f66801845c66b30fa765328fd0be3
```

### 2. Crear y activar el entorno `conda`
```bash 
conda create -n index-tts-vllm python=3.12
conda activate index-tts-vllm
```

### 3. Instalar PyTorch; se requiere la versión `2.8.0` (la más reciente)
#### Ver la versión máxima compatible con tu GPU y la versión realmente instalada
```bash
nvidia-smi
nvcc --version
``` 
#### Versión máxima de CUDA soportada por el driver
```bash
CUDA Version: 12.8
```
#### Versión real del compilador CUDA instalado
```bash
Cuda compilation tools, release 12.8, V12.8.89
```
#### El comando de instalación correspondiente (PyTorch ofrece por defecto la versión del driver `12.8`)
```bash
pip install torch torchvision
```
Se requiere PyTorch `2.8.0` (correspondiente a `vllm 0.10.2`). Para las instrucciones exactas de instalación, consulta la [web oficial de PyTorch](https://pytorch.org/get-started/locally/)

### 4. Instalar dependencias
```bash 
pip install -r requirements.txt
```

### 5. Descargar los pesos del modelo
### Opción 1: descargar los pesos oficiales y luego convertirlos
Estos son los pesos oficiales. Puedes descargarlos en cualquier ruta local. Soporta los pesos de `IndexTTS-1.5`
| HuggingFace                                                   | ModelScope                                                          |
|---------------------------------------------------------------|---------------------------------------------------------------------|
| [IndexTTS](https://huggingface.co/IndexTeam/Index-TTS)        | [IndexTTS](https://modelscope.cn/models/IndexTeam/Index-TTS)        |
| [IndexTTS-1.5](https://huggingface.co/IndexTeam/IndexTTS-1.5) | [IndexTTS-1.5](https://modelscope.cn/models/IndexTeam/IndexTTS-1.5) |

A continuación se toma como ejemplo el método de instalación con ModelScope
#### Atención: `git` necesita tener `lfs` instalado e inicializado (si ya lo tienes, puedes saltarte este paso)
```bash
sudo apt-get install git-lfs
git lfs install
```
Crea el directorio del modelo y descarga el modelo:
```bash 
mkdir model_dir
cd model_dir
git clone https://www.modelscope.cn/IndexTeam/IndexTTS-1.5.git
```

#### Conversión de los pesos del modelo
```bash 
bash convert_hf_format.sh /path/to/your/model_dir
```
Por ejemplo, si descargaste el modelo `IndexTTS-1.5` dentro del directorio `model_dir`, ejecuta:
```bash
bash convert_hf_format.sh model_dir/IndexTTS-1.5
```
Esta operación convertirá los pesos oficiales a una versión compatible con la librería `transformers` y los guardará en la carpeta `vllm` dentro de la ruta de pesos, para facilitar que la librería `vllm` cargue los pesos más adelante.

### 6. Modificar la interfaz para adaptarla al proyecto
Como los datos devueltos por la interfaz no son compatibles con este proyecto, hay que ajustarla para que devuelva directamente los datos de audio.
```bash
vi api_server.py
```
```bash 
@app.post("/tts", responses={
    200: {"content": {"application/octet-stream": {}}},
    500: {"content": {"application/json": {}}}
})
async def tts_api(request: Request):
    try:
        data = await request.json()
        text = data["text"]
        character = data["character"]

        global tts
        sr, wav = await tts.infer_with_ref_audio_embed(character, text)

        return Response(content=wav.tobytes(), media_type="application/octet-stream")
        
    except Exception as ex:
        tb_str = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        print(tb_str)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(tb_str)
            }
        )
```

### 7. Escribir el script `.sh` de arranque (debes ejecutarlo dentro del entorno `conda` correspondiente)
```bash 
vi start_api.sh
```
### Pega el siguiente contenido y luego pulsa `:` y escribe `wq` para guardar
#### Sustituye `/home/system/index-tts-vllm/model_dir/IndexTTS-1.5` por la ruta real en tu entorno
```bash
# Activar el entorno conda
conda activate index-tts-vllm 
echo "Entorno conda del proyecto activado"
sleep 2
# Buscar el PID que ocupa el puerto 11996
PID_VLLM=$(sudo netstat -tulnp | grep 11996 | awk '{print $7}' | cut -d'/' -f1)

# Comprobar si se encontró un PID
if [ -z "$PID_VLLM" ]; then
  echo "No se encontró ningún proceso usando el puerto 11996"
else
  echo "Se encontró un proceso usando el puerto 11996, PID: $PID_VLLM"
  # Intentar primero con un kill normal y esperar 2 segundos
  kill $PID_VLLM
  sleep 2
  # Comprobar si el proceso sigue vivo
  if ps -p $PID_VLLM > /dev/null; then
    echo "El proceso sigue en ejecución, forzando finalización..."
    kill -9 $PID_VLLM
  fi
  echo "Proceso $PID_VLLM finalizado"
fi

# Buscar procesos relacionados con VLLM::EngineCore
GPU_PIDS=$(ps aux | grep -E "VLLM|EngineCore" | grep -v grep | awk '{print $2}')

# Comprobar si se encontró algún PID
if [ -z "$GPU_PIDS" ]; then
  echo "No se encontraron procesos relacionados con VLLM"
else
  echo "Se encontraron procesos relacionados con VLLM, PID: $GPU_PIDS"
  # Intentar primero con un kill normal y esperar 2 segundos
  kill $GPU_PIDS
  sleep 2
  # Comprobar si el proceso sigue vivo
  if ps -p $GPU_PIDS > /dev/null; then
    echo "El proceso sigue en ejecución, forzando finalización..."
    kill -9 $GPU_PIDS
  fi
  echo "Procesos $GPU_PIDS finalizados"
fi

# Crear el directorio tmp si no existe
mkdir -p tmp

# Ejecutar api_server.py en segundo plano y redirigir los logs a tmp/server.log
nohup python api_server.py --model_dir /home/system/index-tts-vllm/model_dir/IndexTTS-1.5 --port 11996 > tmp/server.log 2>&1 &
echo "api_server.py se está ejecutando en segundo plano; revisa los logs en tmp/server.log"
```
Dale permisos de ejecución al script y ejecútalo:
```bash 
chmod +x start_api.sh
./start_api.sh
```
Los logs se escribirán en `tmp/server.log`; puedes verlos con este comando:
```bash
tail -f tmp/server.log
```
Si tu memoria de GPU es suficiente, puedes añadir el parámetro de arranque `--gpu_memory_utilization` al script para ajustar el porcentaje de uso de VRAM. El valor predeterminado es `0.25`.

## Configuración de voces
`index-tts-vllm` permite registrar voces personalizadas mediante un archivo de configuración, tanto para una sola voz como para combinaciones de voces.
Configura las voces personalizadas en el archivo `assets/speaker.json` de la raíz del proyecto.
### Formato de configuración
```bash
{
    "NombreDelLocutor1": [
        "ruta/del/audio1.wav",
        "ruta/del/audio2.wav"
    ],
    "NombreDelLocutor2": [
        "ruta/del/audio3.wav"
    ]
}
```
### Nota (después de configurar el rol, hay que reiniciar el servicio para registrar la voz)
Después de añadirlo, debes agregar el locutor correspondiente en el panel de control (en despliegue de un solo módulo, debes cambiar la `voice` correspondiente).
