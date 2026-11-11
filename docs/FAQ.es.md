<h1 align="center">VibeDrop · Preguntas frecuentes</h1>

<p align="center">
  🇪🇸 <b>Español</b> · 🇬🇧 <a href="FAQ.md">English</a> · 🇮🇹 <a href="FAQ.it.md">Italiano</a>
  <br>
  ¿Primera instalación? El <a href="../README.md#-quick-start">Quick start</a> lo explica en cinco pasos
  (guía detallada para principiantes disponible <a href="GUIDA.md">en italiano</a>).
</p>

---

**Temas:**
[Instalación y arranque](#instalación-y-arranque) ·
[Descargas](#descargas) ·
[Telegram](#telegram) ·
[Ajustes y datos](#ajustes-y-datos)

---

## Instalación y arranque

### Windows dice "Windows protegió su PC". ¿Es un virus?

No. Windows muestra este aviso con todos los programas nuevos que todavía no tienen
una firma conocida. Haz clic en **Más información** y luego en
**Ejecutar de todas formas**. Solo pasa la primera vez.

### El antivirus bloquea o pone en cuarentena VibeDrop.exe

Algunos antivirus marcan por error los programas creados con PyInstaller, la
herramienta con la que se construye VibeDrop. Descarga la app **solo** desde la
página oficial **Releases** del proyecto en GitHub y, si confías en ella, añádela a
las excepciones del antivirus. También puedes ejecutar VibeDrop desde el código
fuente (consulta el [README](../README.md)).

### Hago doble clic en VibeDrop y no pasa nada

El primer arranque puede tardar **10-20 segundos** porque el programa se
descomprime solo. Espera sin volver a hacer clic. Si después de un minuto no ha
aparecido nada, reinicia el ordenador y vuelve a intentarlo.

### La app se abre en el navegador en lugar de en su ventana

VibeDrop usa un componente de Windows llamado **Microsoft Edge WebView2**. Si falta,
la app abre la misma pantalla en el navegador y funciona igual. Para tener la
ventana, instala **WebView2 Runtime** desde la web de Microsoft (busca
*"WebView2 Runtime download"*, elige **Evergreen Bootstrapper**) y vuelve a abrir
VibeDrop. Windows 11 ya lo incluye.

### Arriba pone "ffmpeg no encontrado"

ffmpeg es el programa que convierte el audio a MP3. VibeDrop lo busca, en este orden:

1. en la **misma carpeta** que `VibeDrop.exe`;
2. en una carpeta **`bin`** junto a `VibeDrop.exe`;
3. entre los programas instalados en el ordenador (el *PATH*).

La solución más sencilla es la primera: copia **ffmpeg.exe** junto a
**VibeDrop.exe** y **vuelve a abrir** la app. Puedes conseguir `ffmpeg.exe` en
[gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip): abre el
`.zip`, entra en la carpeta y luego en `bin`.

Si te manejas con la terminal, `winget install Gyan.FFmpeg` lo instala para todo el
sistema; después reinicia el ordenador.

### ¿Funciona en Mac o Linux?

`VibeDrop.exe` es solo para Windows. En Mac y Linux puedes ejecutar VibeDrop desde
el código fuente con Python 3.11 o superior (consulta el [README](../README.md)),
después de instalar ffmpeg (`brew install ffmpeg` en Mac,
`sudo apt install ffmpeg` en Ubuntu/Debian).

### El icono del escritorio está vacío o no es el correcto

Windows guarda en memoria los iconos que ya ha visto. Reinicia el ordenador y
aparecerá el icono correcto (un cuadrado oscuro redondeado con cinco barritas
azules).

---

## Descargas

### ¿Qué enlaces puedo pegar?

Direcciones de **vídeos sueltos** de YouTube:

- `https://www.youtube.com/watch?v=…`
- `https://youtu.be/…`
- `https://www.youtube.com/shorts/…`
- `https://www.youtube.com/live/…`
- `https://music.youtube.com/watch?v=…`

Puedes pegar tantos como quieras, **uno por línea**.
Las **listas de reproducción completas** no son compatibles: si un enlace contiene
un vídeo y una lista, VibeDrop descarga solo ese vídeo.

### "Enlace no reconocido"

Lo que has pegado no es la dirección de un vídeo. Abre el vídeo en YouTube, haz
clic en la barra de direcciones, copia con **Ctrl + C** y vuelve a pegar.

### ¿Dónde se guardan las canciones?

En la carpeta que aparece **abajo a la derecha** en la ventana de VibeDrop,
normalmente **Música → VibeDrop** (`C:\Users\<tu nombre>\Music\VibeDrop`).
Pulsa **Abrir** junto a una canción terminada para ir directamente a ella.

### ¿Cómo cambio la carpeta de las canciones?

Dos formas:

- haz clic en la ruta **abajo a la derecha**, escribe la nueva y pulsa **Intro**
  (**Esc** cancela);
- o ve a **Ajustes → Carpeta de destino** → **Guardar**.

Si la carpeta no existe, VibeDrop la crea.

### Una canción se queda en "Error". ¿Qué significa el mensaje?

| Mensaje | Qué hacer |
|---|---|
| *Vídeo no disponible / Vídeo privado* | El vídeo se eliminó, es privado o está bloqueado en tu país: no se puede descargar. |
| *Vídeo con límite de edad* / *YouTube pide iniciar sesión* | Hace falta un archivo `cookies.txt`, mira [más abajo](#qué-es-cookiestxt-y-cómo-lo-creo). |
| *Vídeo reservado a los miembros del canal* | Solo se puede con una cuenta que sea miembro del canal (`cookies.txt`). |
| *YouTube rechazó la descarga (403)* | Espera unos minutos y pulsa **Reintentar**. Si se repite, actualiza yt-dlp. |
| *Demasiadas solicitudes a YouTube (429)* | Has descargado mucho en poco tiempo: espera 10-15 minutos. |
| *La conexión ha caducado* | Comprueba Internet y pulsa **Reintentar**. |
| *No se creó el archivo MP3* | ffmpeg no funciona: vuelve a poner `ffmpeg.exe` junto a la app y ábrela de nuevo. |
| *Interrumpido al cerrar la app* | Cerraste VibeDrop mientras descargaba: pulsa **Reintentar**. |

### Las descargas funcionaban y de repente fallan todas

YouTube cambia a menudo y el componente que descarga, **yt-dlp**, necesita
actualizarse. Ve a **Ajustes → Buscar actualizaciones** (o pulsa **Actualizar** en
la franja *"yt-dlp necesita una actualización"* de arriba), espera la confirmación
y luego **cierra y vuelve a abrir** VibeDrop.

### ¿Qué es cookies.txt y cómo lo creo?

Algunos vídeos (con límite de edad o solo para miembros) solo se ven con una cuenta
conectada. `cookies.txt` permite que VibeDrop hable con YouTube **como tu cuenta**.

1. En el navegador donde ya has iniciado sesión en YouTube, instala una extensión
   que exporte las cookies en formato *Netscape*, por ejemplo
   **"Get cookies.txt LOCALLY"**.
2. Abre **youtube.com**, pulsa la extensión y exporta las cookies.
3. Cambia el nombre del archivo a **`cookies.txt`**.
4. Pulsa **⊞ Windows + R**, escribe `%APPDATA%\VibeDrop`, pulsa **Intro** y pon el
   archivo en esa carpeta.

> [!CAUTION]
> `cookies.txt` da acceso a tu cuenta de YouTube/Google. No lo compartas nunca y
> bórralo cuando ya no lo necesites.

### ¿Puedo elegir la calidad?

Sí: **Ajustes → Calidad MP3**, de **128** a **320 kbps**. 192 kbps es un buen
equilibrio; cuanta más calidad, más pesa el archivo.

### ¿Puedo descargar varias canciones a la vez?

Sí: pega varios enlaces, uno por línea, y pulsa **Descargar**. VibeDrop los descarga
**de uno en uno**, en orden.

---

## Telegram

### ¿Necesito Telegram?

No. Sin Telegram las canciones se quedan en el ordenador. Telegram solo sirve para
recibirlas también en el móvil.

### ¿Dónde encuentro el token (la "clave API") de mi bot?

Te lo da **@BotFather** al crear el bot. Si lo has perdido:

1. abre el chat con **BotFather** (el que tiene la marca azul de verificación);
2. envía `/mybots`;
3. toca tu bot → **API Token**.

Un token tiene este aspecto: `7012345678:AAHk3xQ-Zb9Lm2Pq8RsTuVwXyZ0aBcDeFgH`
(números, **dos puntos** y luego letras y números).

### Buscar chat id dice "No se encontró ninguna chat"

Tu bot solo ve los mensajes que **le envían a él**. Comprueba que:

1. escribes a **tu bot**, no a **BotFather** (tu bot tiene el nombre de usuario que
   elegiste, el que termina en *bot*);
2. has pulsado **INICIAR / START** y después has enviado un mensaje, por ejemplo
   *hola*;
3. el token de VibeDrop es el de **ese** bot (es fácil confundirlos si creaste más
   de uno);
4. Telegram solo guarda esos mensajes **24 horas**: si ha pasado más tiempo, vuelve
   a escribir *hola*.

Después pulsa otra vez **Buscar chat id**.

### Buscar chat id sigue fallando: ¿cómo obtengo el chat id a mano?

**Opción 1, en el navegador** (sin instalar nada):

1. Envía cualquier mensaje a tu bot.
2. Abre esta dirección, sustituyendo `TU_TOKEN` por tu token:
   ```
   https://api.telegram.org/botTU_TOKEN/getUpdates
   ```
   (el token va justo después de `bot`, sin espacios ni `/`).
3. Busca `"chat":{"id":`: el número que sigue es tu **chat id**, por ejemplo
   `"chat":{"id":123456789`.
4. Pégalo en el campo **Chat id** de VibeDrop.

Si la página solo muestra `{"ok":true,"result":[]}`, el bot no ha recibido
mensajes: vuelve a escribirle y recarga la página.

**Opción 2, con un bot:** busca en Telegram **@userinfobot** y pulsa **INICIAR**.
Te responde con tu **Id**, que también es el chat id de tu chat privado con tu bot.
(Es un bot externo, sin relación con VibeDrop: solo te dice tu número.)

### Verificar conexión da un error. ¿Qué significa?

| Mensaje | Causa y solución |
|---|---|
| *Token no válido* | Token copiado a medias, con un espacio de más o de otro bot. Cópialo de nuevo desde BotFather (`/mybots` → bot → **API Token**). |
| *Chat id no válido* | El chat id es incorrecto o nunca escribiste al bot. Envía *hola* al bot y usa **Buscar chat id**. |
| *Has bloqueado el bot* | Abre el chat del bot en Telegram y pulsa **Desbloquear** / **INICIAR**. |
| *El bot no forma parte de esa chat* | El chat id es de un grupo donde el bot no está: añádelo al grupo o usa tu chat privado. |
| *Telegram no está disponible* | No hay Internet o la red (oficina, escuela, hotel) bloquea Telegram. Prueba con otra red. |
| *Demasiadas solicitudes a Telegram* | Espera un minuto y vuelve a intentarlo. |
| *Hacen falta el token del bot y la chat id* | Uno de los dos campos está vacío. |

### La conexión funciona pero las canciones no llegan al móvil

- ¿Pulsaste **Guardar** después de **Verificar conexión**? Sin **Guardar** no se
  conserva nada.
- Mira la fila de la canción en VibeDrop: si pone *"Telegram falló"*, el mensaje de
  al lado explica el motivo. Puedes reintentarlo con **Enviar de nuevo**.
- Comprueba que miras el chat de **tu bot** en Telegram, no el de BotFather.

### "Solo se envió la ruta": ¿por qué no recibí la canción?

Telegram no permite a los bots enviar archivos de más de **50 MB** (unos 35 minutos
a 192 kbps). Para archivos más grandes, el bot te envía solo la ruta donde está
guardado en el ordenador. Para audios muy largos, baja la **Calidad MP3**.

### ¿Puedo recibir las canciones en un grupo?

Sí. Añade tu bot al grupo, escribe un mensaje en el grupo y pulsa
**Buscar chat id**; elige el grupo (su chat id es un número negativo, como
`-1001234567890`).

### He compartido el token por error: ¿qué hago?

Quien tenga el token puede usar tu bot. Cámbialo enseguida:

1. abre **BotFather** → envía `/mybots` → elige el bot → **API Token** →
   **Revoke current token**;
2. pega el token **nuevo** en **VibeDrop → Ajustes** y pulsa **Guardar**.

El token anterior deja de funcionar al instante.

### ¿Dónde se guarda el token? ¿Está seguro?

Se queda **solo en tu ordenador**, en el archivo `settings.json` dentro de
`%APPDATA%\VibeDrop`. VibeDrop lo usa únicamente para hablar con Telegram. No envíes
ese archivo a nadie.

### ¿Cómo dejo de recibir las canciones en Telegram?

**Ajustes** → vacía **Token del bot de Telegram** y **Chat id** → **Guardar**.

---

## Ajustes y datos

### ¿Cómo cambio el idioma o el tema?

**Ajustes → Idioma** (Español, English, Italiano) y **Tema** (Claro, Oscuro,
Sistema) → **Guardar**.

### El texto es demasiado pequeño o grande

Usa los botones **−** y **+** de arriba, o **Ctrl + rueda del ratón**,
**Ctrl + +** y **Ctrl + −**. **Ctrl + 0** vuelve al 100 %.

### ¿Se guardan las notas al cerrar la app?

Sí. Las notas del panel **Notas** se guardan en tu ordenador (en
`%APPDATA%\VibeDrop`) y siguen ahí la próxima vez. Puedes tener hasta 200; bórralas
con **Borrar** o todas juntas con **Limpiar**.

### ¿"Vaciar terminados" borra mis canciones?

No. Solo quita las filas de la lista; los archivos MP3 se quedan en la carpeta.
**Borrar** en una canción también quita solo la fila.

### ¿Qué son los "Detalles bajo las descargas"?

Es el texto que aparece debajo de cada canción terminada y como pie del mensaje en
Telegram. Personalízalo en **Ajustes** con `{title}` (título), `{duration}`
(duración) y `{size}` (tamaño).

### ¿Dónde se guardan los ajustes, el historial y las notas?

En `%APPDATA%\VibeDrop` en Windows (pulsa **⊞ Windows + R**, escribe
`%APPDATA%\VibeDrop`, **Intro**), `~/Library/Application Support/VibeDrop` en Mac y
`~/.config/VibeDrop` en Linux.

### Quiero empezar de cero

Cierra VibeDrop y borra la carpeta `%APPDATA%\VibeDrop`. El siguiente arranque será
como una instalación nueva. Las canciones ya descargadas no se tocan.

### ¿Es legal?

VibeDrop es una herramienta para **uso personal**. Descarga solo contenido que
tengas derecho a usar y respeta los derechos de autor y las condiciones de uso de
YouTube.

---

<p align="center">
  ¿No encuentras la respuesta? Abre una <b>Issue</b> en la página del proyecto en GitHub.
</p>
