<h1 align="center">VibeDrop · Domande frequenti</h1>

<p align="center">
  🇮🇹 <b>Italiano</b> · 🇬🇧 <a href="FAQ.md">English</a> · 🇪🇸 <a href="FAQ.es.md">Español</a>
  <br>
  Prima installazione? Parti dalla <a href="GUIDA.md">guida passo passo</a>.
</p>

---

**Argomenti:**
[Installazione e avvio](#installazione-e-avvio) ·
[Download](#download) ·
[Telegram](#telegram) ·
[Impostazioni e dati](#impostazioni-e-dati)

---

## Installazione e avvio

### Windows dice "Windows ha protetto il PC". È un virus?

No. Windows mostra questo avviso per tutti i programmi nuovi che non hanno ancora
una "firma" conosciuta. Clicca su **Ulteriori informazioni** e poi su
**Esegui comunque**. Succede solo la prima volta.

### L'antivirus blocca o mette in quarantena VibeDrop.exe

Alcuni antivirus segnalano per errore i programmi creati con PyInstaller, lo
strumento usato per costruire VibeDrop. Scarica l'app **solo** dalla pagina
ufficiale *Releases* del progetto su GitHub e, se ti fidi, aggiungila alle
eccezioni dell'antivirus. In alternativa puoi avviare VibeDrop dal codice sorgente
(vedi il [README](../README.md)).

### Doppio clic su VibeDrop e non succede niente

Il primo avvio può richiedere **10-20 secondi**, perché il programma si "spacchetta"
da solo: aspetta senza cliccare di nuovo. Se dopo un minuto non è ancora comparso
nulla, riavvia il computer e riprova.

### L'app si apre nel browser invece che nella sua finestra

VibeDrop usa un componente di Windows chiamato **Microsoft Edge WebView2**. Se manca,
l'app apre la stessa schermata nel browser e funziona lo stesso. Per avere la
finestra, installa **WebView2 Runtime** dal sito Microsoft (cerca *"WebView2
Runtime download"*, scegli **Evergreen Bootstrapper**) e riapri VibeDrop.
Su Windows 11 è già presente.

### In alto c'è scritto "ffmpeg non trovato"

ffmpeg è il programma che converte l'audio in MP3. VibeDrop lo cerca, in quest'ordine:

1. nella **stessa cartella** di `VibeDrop.exe`;
2. in una cartella **`bin`** accanto a `VibeDrop.exe`;
3. tra i programmi installati nel computer (il cosiddetto *PATH*).

La soluzione più semplice è la prima: copia **ffmpeg.exe** accanto a
**VibeDrop.exe** (vedi il [passo 3 della guida](GUIDA.md#passo-3--scaricare-ffmpeg-il-convertitore))
e **riapri** l'app.

Se sei pratico del terminale, puoi anche installarlo per tutto il computer con
`winget install Gyan.FFmpeg`. Poi riavvia il computer.

### Funziona su Mac o Linux?

Il file `VibeDrop.exe` è solo per Windows. Su Mac e Linux puoi avviare VibeDrop dal
codice sorgente con Python 3.11 o più recente (istruzioni nel [README](../README.md)),
dopo aver installato ffmpeg (`brew install ffmpeg` su Mac, `sudo apt install ffmpeg`
su Ubuntu/Debian).

### L'icona sul Desktop è vuota o diversa da quella giusta

Windows conserva in memoria le icone già viste. Riavvia il computer: l'icona giusta
(un quadrato scuro arrotondato con cinque barrette azzurre) compare da sola.

---

## Download

### Quali link posso incollare?

Indirizzi di **singoli video** di YouTube:

- `https://www.youtube.com/watch?v=…`
- `https://youtu.be/…`
- `https://www.youtube.com/shorts/…`
- `https://www.youtube.com/live/…`
- `https://music.youtube.com/watch?v=…`

Puoi incollarne quanti ne vuoi, **uno per riga**.
Le **playlist intere** non sono supportate: se un link contiene sia un video sia una
playlist, VibeDrop scarica soltanto quel video.

### "Link non riconosciuto"

Quello che hai incollato non è l'indirizzo di un video. Apri il video su YouTube,
clicca sulla barra degli indirizzi, copia con **Ctrl + C** e incolla di nuovo.

### Dove finiscono le canzoni?

Nella cartella scritta **in basso a destra** nella finestra di VibeDrop. Di solito è
**Musica → VibeDrop** (`C:\Users\<tuo nome>\Music\VibeDrop`).
Per aprirla al volo, premi **Apri** accanto a una canzone finita.

### Come cambio la cartella delle canzoni?

Due modi:

- clicca sul percorso **in basso a destra**, scrivi quello nuovo e premi **Invio**
  (**Esc** annulla);
- oppure **Impostazioni → Cartella di destinazione** → **Salva**.

Se la cartella non esiste, VibeDrop la crea.

### Una canzone resta su "Errore". Che cosa significa il messaggio?

| Messaggio | Cosa fare |
|---|---|
| *Video non disponibile / Video privato* | Il video è stato rimosso, è privato o è bloccato nel tuo paese: non si può scaricare. |
| *Video con limiti di età* / *YouTube chiede un accesso* | Serve un file `cookies.txt`, vedi [sotto](#che-cosè-cookiestxt-e-come-lo-creo). |
| *Video riservato agli iscritti del canale* | Si può scaricare solo con un account iscritto al canale (`cookies.txt`). |
| *YouTube ha rifiutato il download (403)* | Aspetta qualche minuto e premi **Riprova**. Se si ripete, aggiorna yt-dlp. |
| *Troppe richieste a YouTube (429)* | Hai scaricato molto in poco tempo: aspetta 10-15 minuti. |
| *La connessione è andata in timeout* | Controlla Internet e premi **Riprova**. |
| *Il file MP3 non è stato creato* | ffmpeg non funziona: rimetti `ffmpeg.exe` accanto all'app e riaprila. |
| *Interrotto alla chiusura dell'app* | Hai chiuso VibeDrop mentre scaricava: premi **Riprova**. |

### I download funzionavano e all'improvviso hanno smesso tutti

YouTube cambia spesso il suo funzionamento e il componente che scarica,
**yt-dlp**, va aggiornato. Vai in **Impostazioni → Controlla aggiornamenti** (oppure
clicca **Aggiorna** nella striscia *"yt-dlp da aggiornare"* in alto), aspetta la
conferma, poi **chiudi e riapri** VibeDrop.

### Che cos'è cookies.txt e come lo creo?

Alcuni video (con limiti di età o riservati agli iscritti) si vedono solo da
account connessi. `cookies.txt` è un file che permette a VibeDrop di presentarsi
a YouTube **con il tuo account**.

1. Nel browser in cui hai già fatto l'accesso a YouTube, installa un'estensione che
   esporta i cookie in formato *Netscape*, per esempio **"Get cookies.txt LOCALLY"**.
2. Apri **youtube.com**, clicca sull'estensione ed esporta i cookie.
3. Rinomina il file in **`cookies.txt`**.
4. Premi **⊞ Windows + R**, scrivi `%APPDATA%\VibeDrop` e premi **Invio**:
   metti il file in quella cartella.

> [!CAUTION]
> `cookies.txt` dà accesso al tuo account YouTube/Google. Non condividerlo mai.
> Cancellalo quando non ti serve più.

### Posso scegliere la qualità?

Sì: **Impostazioni → Qualità MP3**, da **128** a **320 kbps**. 192 kbps è un ottimo
compromesso. Più alta è la qualità, più pesante è il file.

### Si possono scaricare più canzoni insieme?

Sì: incolla più link, uno per riga, e premi **Scarica**. VibeDrop le scarica **una
alla volta**, in ordine.

---

## Telegram

### Mi serve davvero Telegram?

No. Senza Telegram le canzoni restano sul computer. Telegram serve solo se vuoi
riceverle anche sul telefono.

### Dove trovo il token (la "chiave API") del mio bot?

Il token te lo dà **@BotFather** quando crei il bot. Se l'hai perso:

1. su Telegram apri la chat con **BotFather** (quello con la spunta blu);
2. scrivi `/mybots`;
3. tocca il nome del tuo bot → **API Token**.

Il token ha questo aspetto: `7012345678:AAHk3xQ-Zb9Lm2Pq8RsTuVwXyZ0aBcDeFgH`
(numeri, **due punti**, poi lettere e numeri).

### Trova chat id dice "Nessuna chat trovata"

Il bot vede solo i messaggi che **gli sono stati scritti**. Controlla questi punti:

1. Stai scrivendo nella chat del **tuo bot**, non in quella di **BotFather**?
   (Il tuo bot ha il nome utente che hai scelto, quello che finisce con *bot*.)
2. Hai premuto **AVVIA / START** e poi mandato un messaggio, per esempio *ciao*?
3. Il token in VibeDrop è proprio quello **di questo bot**? Se hai creato più bot,
   è facile confonderli.
4. Telegram conserva quei messaggi solo per **24 ore**: se è passato più tempo,
   scrivi di nuovo *ciao* al bot.

Poi premi di nuovo **Trova chat id**.

### Trova chat id proprio non funziona: come trovo il chat id a mano?

**Metodo 1, dal browser** (non serve installare niente):

1. Manda un messaggio qualsiasi al tuo bot.
2. Nella barra degli indirizzi del browser scrivi, sostituendo `IL_TUO_TOKEN` con
   il tuo token:
   ```
   https://api.telegram.org/botIL_TUO_TOKEN/getUpdates
   ```
   (attenzione: subito dopo `bot` viene il token, senza spazi né `/`).
3. Nella pagina cerca `"chat":{"id":` → il numero che segue è il tuo **chat id**,
   per esempio `"chat":{"id":123456789`.
4. Copialo nel campo **Chat id** di VibeDrop.

Se la pagina mostra solo `{"ok":true,"result":[]}`, il bot non ha ricevuto messaggi:
scrivigli di nuovo e ricarica la pagina.

**Metodo 2, con un bot:** cerca su Telegram **@userinfobot**, premi **AVVIA**: ti
risponde con il tuo **Id**, che è anche il chat id della tua chat privata con il
tuo bot. (È un bot esterno, non legato a VibeDrop: ti dice solo il tuo numero.)

### Verifica collegamento dà un errore. Che cosa significa?

| Messaggio | Causa e soluzione |
|---|---|
| *Token non valido* | Token copiato a metà, con uno spazio in più o di un altro bot. Ricopialo da BotFather (`/mybots` → bot → **API Token**). |
| *Chat id non valido* | Il chat id è sbagliato oppure non hai mai scritto al bot. Scrivi *ciao* al bot e usa **Trova chat id**. |
| *Hai bloccato il bot* | Apri la chat del bot su Telegram e premi **Sblocca** / **AVVIA**. |
| *Il bot non fa parte di quella chat* | Il chat id è di un gruppo in cui il bot non c'è: aggiungilo al gruppo, oppure usa la tua chat privata. |
| *Telegram non raggiungibile* | Niente Internet, oppure la rete (ufficio, scuola, hotel) blocca Telegram. Prova da un'altra rete. |
| *Troppe richieste a Telegram* | Aspetta un minuto e riprova. |
| *Servono il token del bot e la chat id* | Uno dei due campi è vuoto. |

### Il collegamento funziona ma le canzoni non arrivano sul telefono

- Dopo **Verifica collegamento** hai premuto **Salva**? Senza **Salva** le
  impostazioni non vengono ricordate.
- Guarda la riga della canzone in VibeDrop: se c'è scritto *"Telegram non
  riuscito"*, il messaggio accanto spiega il motivo. Puoi ritentare con
  **Invia di nuovo**.
- Controlla di guardare la chat del **tuo bot** su Telegram, non quella di BotFather.

### "Solo percorso inviato": perché non ho ricevuto la canzone?

Telegram non permette ai bot di inviare file oltre **50 MB** (circa 35 minuti a
192 kbps). Per i file più grandi il bot ti manda solo il percorso in cui il file è
salvato sul computer. Per audio molto lunghi, abbassa la **Qualità MP3**.

### Posso ricevere le canzoni in un gruppo?

Sì. Aggiungi il tuo bot al gruppo, scrivi un messaggio nel gruppo e premi
**Trova chat id**: scegli il nome del gruppo (il suo chat id è un numero negativo,
per esempio `-1001234567890`).

### Ho condiviso per sbaglio il token: cosa faccio?

Chi ha il token può usare il tuo bot. Cambialo subito:

1. apri **BotFather** → scrivi `/mybots` → scegli il bot → **API Token** →
   **Revoke current token**;
2. copia il **nuovo** token in **VibeDrop → Impostazioni** e premi **Salva**.

Il vecchio token smette subito di funzionare.

### Dove viene salvato il token? È al sicuro?

Resta **solo sul tuo computer**, nel file `settings.json` dentro `%APPDATA%\VibeDrop`.
VibeDrop lo usa unicamente per parlare con Telegram. Non mandare quel file a nessuno.

### Come smetto di ricevere le canzoni su Telegram?

**Impostazioni** → svuota i campi **Token del bot Telegram** e **Chat id** → **Salva**.

---

## Impostazioni e dati

### Come cambio lingua o tema?

**Impostazioni → Lingua** (Italiano, English, Español) e **Tema** (Chiaro, Scuro,
Sistema) → **Salva**.

### Le scritte sono troppo piccole o troppo grandi

Usa i pulsanti **−** e **+** in alto, oppure **Ctrl + rotellina del mouse**,
**Ctrl + +** e **Ctrl + −**. **Ctrl + 0** torna al 100%.

### Gli appunti restano salvati quando chiudo l'app?

Sì. Gli appunti del riquadro **Appunti** sono salvati sul tuo computer (in
`%APPDATA%\VibeDrop`) e li ritrovi alla prossima apertura. Puoi averne fino a 200;
cancellali con **Elimina**, oppure tutti insieme con **Pulisci**.

### Svuota completati cancella le mie canzoni?

No. Toglie solo le righe dall'elenco: i file MP3 restano nella cartella.
Anche **Elimina** su una canzone toglie solo la riga.

### Che cosa sono i "Dettagli sotto i download"?

È il testo che compare sotto ogni canzone finita e nella didascalia su Telegram.
Puoi personalizzarlo in **Impostazioni** usando `{title}` (titolo),
`{duration}` (durata) e `{size}` (dimensione).

### Dove sono salvati impostazioni, elenco e appunti?

In `%APPDATA%\VibeDrop` (premi **⊞ Windows + R**, scrivi `%APPDATA%\VibeDrop`,
**Invio**). Su Mac: `~/Library/Application Support/VibeDrop`; su Linux:
`~/.config/VibeDrop`.

### Voglio ripartire da zero

Chiudi VibeDrop e cancella la cartella `%APPDATA%\VibeDrop`. Al prossimo avvio l'app
riparte come appena installata. Le canzoni già scaricate non vengono toccate.

### È legale?

VibeDrop è uno strumento per **uso personale**. Scarica soltanto contenuti che hai
il diritto di usare e rispetta il diritto d'autore e le condizioni d'uso di YouTube.

---

<p align="center">
  Non hai trovato la risposta? Apri una segnalazione nella sezione <b>Issues</b> del progetto su GitHub.
</p>
