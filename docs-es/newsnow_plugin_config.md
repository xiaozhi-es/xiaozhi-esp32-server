# Guía de configuración de fuentes de noticias para el plugin `get_news_from_newsnow`

## Resumen

El plugin `get_news_from_newsnow` ahora admite la configuración dinámica de fuentes de noticias desde la interfaz web de administración, por lo que ya no es necesario modificar el código. Los usuarios pueden configurar distintas fuentes para cada agente desde el panel de control.

## Formas de configuración

### 1. Configuración desde la interfaz web de administración (recomendada)

1. Inicia sesión en el panel de control
2. Entra en la página `角色配置`
3. Elige el agente que quieres configurar
4. Haz clic en `编辑功能`
5. Busca el plugin `newsnow新闻聚合` en el área de configuración de parámetros de la derecha
6. En el campo `新闻源配置`, introduce nombres en chino separados por punto y coma

### 2. Configuración mediante archivo

Configúralo en `config.yaml`:

```yaml
plugins:
  get_news_from_newsnow:
    url: "https://newsnow.busiyi.world/api/s?id="
    news_sources: "澎湃新闻;百度热搜;财联社;微博;抖音"
```

## Formato de configuración de las fuentes

La configuración de las fuentes usa nombres en chino separados por punto y coma, con el siguiente formato:

```
中文名称1;中文名称2;中文名称3
```

### Ejemplo de configuración

```
澎湃新闻;百度热搜;财联社;微博;抖音;知乎;36氪
```

## Fuentes compatibles

El plugin admite los siguientes nombres de fuentes en chino:

- 澎湃新闻
- 百度热搜
- 财联社
- 微博
- 抖音
- 知乎
- 36氪
- 华尔街见闻
- IT之家
- 今日头条
- 虎扑
- 哔哩哔哩
- 快手
- 雪球
- 格隆汇
- 法布财经
- 金十数据
- 牛客
- 少数派
- 稀土掘金
- 凤凰网
- 虫部落
- 联合早报
- 酷安
- 远景论坛
- 参考消息
- 卫星通讯社
- 百度贴吧
- 靠谱新闻
- Y más...

## Configuración predeterminada

Si no configuras ninguna fuente, el plugin usará la siguiente configuración predeterminada:

```
澎湃新闻;百度热搜;财联社
```

## Instrucciones de uso

1. **Configurar las fuentes**: establece los nombres de las fuentes en chino desde la interfaz web o el archivo de configuración, separados por punto y coma
2. **Invocar el plugin**: el usuario puede decir "播报新闻" o "获取新闻"
3. **Especificar una fuente**: el usuario puede decir "播报澎湃新闻" o "获取百度热搜"
4. **Obtener detalles**: el usuario puede decir "详细介绍这条新闻"

## Cómo funciona

1. El plugin recibe un nombre en chino como parámetro (por ejemplo, "澎湃新闻")
2. Según la lista de fuentes configuradas, convierte el nombre en chino al ID equivalente en inglés (por ejemplo, "thepaper")
3. Usa ese ID en inglés para llamar a la API y obtener los datos
4. Devuelve el contenido de la noticia al usuario

## Notas

1. Los nombres en chino configurados deben coincidir exactamente con los definidos en `CHANNEL_MAP`
2. Después de cambiar la configuración, debes reiniciar el servicio o volver a cargar la configuración
3. Si la fuente configurada no es válida, el plugin usará automáticamente la fuente predeterminada
4. Debes separar varias fuentes con punto y coma inglés (`;`), no con punto y coma chino (`；`)
