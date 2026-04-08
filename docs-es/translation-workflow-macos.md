# Guía Reproducible Para Traducir Markdown En macOS

Esta guía describe el método real que usé para traducir todos los `.md` de este directorio al español sin romper el formato Markdown.

## Resumen del método

El flujo final fue este:

1. Inventariar todos los `.md`
2. Medir tamaño y revisar si había cambios locales
3. Traducir por lotes
4. Conservar intactos los elementos literales
5. Validar con `git diff --check`
6. Buscar restos de chino y revisar si eran intencionales

Importante: intenté opciones más automáticas en macOS, pero no fueron lo bastante fiables para dejar un resultado limpio de punta a punta. El método final no fue "traductor automático ciego", sino traducción asistida por lotes + validación terminal.

## Qué herramientas necesitas

En tu MacBook:

```bash
brew install ripgrep
```

Y además:

- `git`
- `python3`
- un editor (`vim`, `nvim`, `code`, etc.)
- opcionalmente un asistente LLM en terminal, si quieres replicar el paso de traducción asistida

## Reglas que seguí

Traducir:

- títulos
- texto explicativo
- listas
- notas
- tablas descriptivas

No traducir o revisar con cuidado:

- bloques de código
- comandos
- rutas
- nombres de archivo
- claves YAML/JSON
- variables de entorno
- URLs
- nombres exactos de menús o etiquetas si deben coincidir con la UI real
- logs y ejemplos literales

## Scripts incluidos

En este directorio quedaron dos scripts auxiliares:

- `md-translation-inventory.sh`
- `md-translation-validate.sh`

Hazlos ejecutables:

```bash
chmod +x md-translation-inventory.sh md-translation-validate.sh
```

## Paso a paso

### 1. Entra al directorio

```bash
cd /Users/jorge/ESP-IDF/xiaozhi-esp32-server/docs
```

### 2. Crea una rama de trabajo

```bash
git checkout -b translate/docs-es
```

### 3. Haz inventario

```bash
./md-translation-inventory.sh .
```

Esto te mostrará:

- lista de `.md`
- conteo de líneas
- estado de git

### 4. Agrupa archivos por lotes

Yo los traduje por lotes para reducir errores y mantener contexto. Un patrón útil:

- lote corto: archivos de menos de 80-100 líneas
- lote medio: 100-220 líneas
- lote grande: archivos de despliegue o integración largos

Puedes ver tamaños así:

```bash
wc -l *.md | sort -n
```

### 5. Lee un lote antes de traducirlo

Ejemplo:

```bash
for f in FAQ.md docker-build.md ali-sms-integration.md; do
  printf '\n===== %s =====\n' "$f"
  sed -n '1,220p' "$f"
done
```

La idea es revisar primero el tipo de contenido:

- si hay más prosa que código: traducir casi todo
- si hay mucha configuración: traducir solo comentarios y explicación
- si hay texto literal del sistema: conservarlo

### 6. Traduce por lotes

El prompt base que seguí fue este:

```text
Traduce estos archivos Markdown al español sin perder el formato Markdown.
Mantén intactos:
- fences de código
- comandos
- rutas
- nombres de archivo
- claves YAML/JSON
- variables de entorno
- URLs
- logs literales
- etiquetas exactas de UI cuando deban coincidir con el sistema

Traduce:
- títulos
- texto descriptivo
- listas
- notas
- tablas descriptivas

No reestructures el documento.
No elimines enlaces ni imágenes.
No cambies bloques de configuración salvo comentarios humanos o texto descriptivo.
```

Si lo haces con un asistente LLM desde terminal, mi recomendación es:

- pasarle pocos archivos por tanda
- validar cada tanda antes de seguir
- no intentar hacer 26 archivos de una sola vez

### 7. Edita en sitio

Yo apliqué los cambios directamente sobre los `.md`.

Si lo haces manualmente con editor:

```bash
vim FAQ.md
```

Si lo haces con ayuda de un asistente:

- pídele que edite los archivos en sitio
- luego revisa el diff local

### 8. Valida después de cada lote

```bash
./md-translation-validate.sh .
```

Este script revisa:

- errores formales de diff
- restos de caracteres CJK
- resumen de diff

### 9. Revisa restos de chino

No todo resto de chino es un error. Yo dejé chino en estos casos:

- nombres exactos de pantallas del panel
- logs de ejemplo
- textos que el usuario debe buscar tal cual en la UI
- ejemplos de payload o configuración literal

La búsqueda rápida:

```bash
rg -n --glob '*.md' '[一-龥]'
```

Después revisa cada coincidencia una por una.

## Flujo completo recomendado

```bash
cd /Users/jorge/ESP-IDF/xiaozhi-esp32-server/docs
chmod +x md-translation-inventory.sh md-translation-validate.sh
git checkout -b translate/docs-es
./md-translation-inventory.sh .
wc -l *.md | sort -n
./md-translation-validate.sh .
git diff --stat -- *.md
git diff --check -- *.md
```

## Criterio práctico para no romper Markdown

Antes de guardar cambios, comprueba esto:

- los encabezados siguen empezando con `#`
- las listas mantienen `-` o numeración
- las tablas siguen con `|`
- las imágenes siguen con `![...]()`
- los enlaces siguen con `[...]()`
- los fences siguen con triple backtick
- el YAML/JSON sigue con indentación correcta

## Qué no recomendaría

No recomendaría:

- traducir todo con reemplazos masivos
- tocar claves de configuración
- traducir nombres de campos de API
- cambiar ejemplos de logs reales
- hacer un solo parche enorme sin validación intermedia

## Método exacto que terminó funcionando mejor

En términos prácticos, el método más robusto fue:

1. `rg` para listar
2. `wc -l` para dimensionar
3. `git status` para asegurar que no había cambios previos en los `.md`
4. lectura por lotes con `sed`
5. traducción por lotes conservando literales
6. validación con `git diff --check`
7. búsqueda de CJK residual con `rg`
8. revisión final de `git diff --stat`

## Si quieres automatizar más

Puedes automatizar el inventario y la validación con los scripts incluidos, pero la parte de traducción sigue necesitando revisión humana o un asistente LLM con criterio, porque:

- mezclar texto humano con YAML/JSON y logs rompe fácilmente documentos
- muchas cadenas deben quedarse literales
- hay menús y labels que conviene no "españolizar" si el producto sigue mostrándolos en chino

## Archivos auxiliares de este método

- [translation-workflow-macos.md](/Users/jorge/ESP-IDF/xiaozhi-esp32-server/docs/translation-workflow-macos.md)
- [md-translation-inventory.sh](/Users/jorge/ESP-IDF/xiaozhi-esp32-server/docs/md-translation-inventory.sh)
- [md-translation-validate.sh](/Users/jorge/ESP-IDF/xiaozhi-esp32-server/docs/md-translation-validate.sh)
