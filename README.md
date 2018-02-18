## Apertium TTS Web

Apertium TTS Web is made up of two components: a web interface and a
server. To function, Apertium TTS Web also requires a third component not
included in this repository, which is the TTS (Text-To-Speech) engine itself
that produces audio from text. <insert link when available>

### Web Interface

The files `index.html`, `style.css`, and `script.js` form the web interface.
These can be served by any web server with no further steps. For example, if
Python is installed, the command `python -m http.server 80` run from this
directory will serve the web interface on port 80.

If the user is willing to change the [default server][2] to a local instance and
forfeit the Google web font "Ubuntu", then the web interface can function
without Internet access as long as it can access the server on an internal
network.

The interface is fully internationalized. It is fully localized in US English
and partially localized in Chuvash and Marathi. All resources required to
change the page language are loaded in the JavaScript on first load.

### Server

The file `server.py` comprises the server, written in Python 3. The command
`./server.py` starts the server and a Ctrl-C interrupt stops it. By default, the
server runs on [port 2738][3]. The server exposes two endpoints to HTTP `GET`
requests:
1. `/list` returns the [ISO 639-3 language codes][1] of all the languages for
which the server provides the text-to-speech service. The endpoint requires no
parameters and the response is a JSON object of the form `['lang1', 'lang2',
...]`.
1. `/tts` returns the synthesized audio for a given language and input text. The
endpoint requires the parameters `lang`, which is the [ISO 693-3 code][1] of the
input text language, and `q`, which is the input text itself. The response
(which may take some time) is a WAV audio file served as binary data with the
headers:
  * `Content-Type: audio/wav`
  * `Content-Disposition: attachment; filename=tts.wav`

The server tries to include appropriate error messages when it responds with a
4xx or 5xx status code.


  [1]: https://en.wikipedia.org/wiki/ISO_639-3
  [2]: https://github.com/shardulc/apertium-tts-web/blob/master/script.js#L8
  [3]: https://github.com/shardulc/apertium-tts-web/blob/master/server.py#L19
