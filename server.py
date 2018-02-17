# coding=utf-8
from tempfile import NamedTemporaryFile
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
from shlex import split
from subprocess import Popen

HOST = "localhost"
PORT = 2738

tts_models = {
    'chv': 'python /home/ossian/Ossian/scripts/speak.py -l chv -s news -o %s naive_01_nn %s'
}

class TTSRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path))
        
        if 'lang' not in params:
            self.send_error(400, 'Missing lang parameter, e.g. lang=chv')
            return
        lang = params['lang']
        if lang not in tts_models:
            self.send_error(501, 'That language is not supported')
            return

        if 'q' not in params:
            self.send_error(400, 'Missing q parameter, e.g. q=cалам')
            return
        q = params['q']

        synth_file = NamedTemporaryFile()
        input_file = NamedTemporaryFile()
        proc = Popen(split(tts_models[lang] % (synth_file.name, input_file.name)))
        
        input_file.write(q)
        input_file.close()

        self.send_response(200)
        self.send_header('Content-Type', 'audio/wav')
        self.send_header('Content-Disposition', 'attachment; filename=tts.wav')
        self.end_headers()
        while True:
            data = synth_file.read(16384)
            if not data:
                break
            self.wfile.write(data)
        synth_file.close()

if __name__ == '__main__':
    httpd = HTTPServer((HOST, PORT), TTSRequestHandler)
    httpd.serve_forever()
