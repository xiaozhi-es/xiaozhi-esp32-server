# Guía de uso del plugin del clima

## Resumen

El plugin del clima `get_weather` es una de las funciones principales del asistente de voz Xiaozhi ESP32. Permite consultar por voz la información meteorológica de distintas regiones del país. El plugin se basa en la API de QWeather y ofrece clima en tiempo real y pronóstico para 7 días.

## Guía para solicitar un API Key

### 1. Registrar una cuenta de QWeather

1. Visita la [consola de QWeather](https://console.qweather.com/)
2. Registra una cuenta y completa la verificación por correo electrónico
3. Inicia sesión en la consola

### 2. Crear una aplicación para obtener el API Key

1. Después de entrar en la consola, haz clic en [`项目管理`](https://console.qweather.com/project?lang=zh) → `创建项目`
2. Rellena la información del proyecto:
   - **Nombre del proyecto**: por ejemplo, "Asistente de voz Xiaozhi"
3. Haz clic en guardar
4. Una vez creado el proyecto, haz clic en `创建凭据` dentro de ese proyecto
5. Rellena la información de la credencial:
    - **Nombre de la credencial**: por ejemplo, "Asistente de voz Xiaozhi"
    - **Método de autenticación**: elige `API Key`
6. Haz clic en guardar
7. Copia el `API Key` de la credencial; este es el primer dato clave de configuración

### 3. Obtener el API Host

1. En la consola, haz clic en [`设置`](https://console.qweather.com/setting?lang=zh) → `API Host`
2. Consulta la dirección `API Host` exclusiva que se te haya asignado; este es el segundo dato clave de configuración

Después de completar estos pasos tendrás dos datos importantes de configuración: `API Key` y `API Host`.

## Formas de configuración (elige una)

### Opción 1. Si usas el despliegue con el panel de control (recomendado)

1. Inicia sesión en el panel de control
2. Entra en la página `角色配置`
3. Elige el agente que quieres configurar
4. Haz clic en `编辑功能`
5. Busca el plugin `天气查询` en el área de configuración de parámetros de la derecha
6. Marca `天气查询`
7. Pega el primer dato clave, `API Key`, en `天气插件 API 密钥`
8. Pega el segundo dato clave, `API Host`, en `开发者 API Host`
9. Guarda la configuración y luego guarda la configuración del agente

### Opción 2. Si solo usas un despliegue de un solo módulo de `xiaozhi-server`

Configúralo en `data/.config.yaml`:

1. Pega el primer dato clave, `API Key`, en `api_key`
2. Pega el segundo dato clave, `API Host`, en `api_host`
3. Escribe tu ciudad en `default_location`, por ejemplo `广州`

```yaml
plugins:
  get_weather:
    api_key: "你的和风天气API密钥"
    api_host: "你的和风天气API主机地址"
    default_location: "你的默认查询城市"
```
