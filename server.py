# coding=utf-8
from tempfile import NamedTemporaryFile
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
from shlex import split
from subprocess import Popen
from json import dump

HOST = "0.0.0.0"
PORT = 2738

tts_models = {
    'chv': 'python /home/ossian/Ossian/scripts/speak.py -l chv -s news -o %s naive_01_nn %s'
}

class TTSRequestHandler(BaseHTTPRequestHandler):

    def handle_tts(self, params):
        if 'lang' not in params:
            self.send_error(400, 'Missing lang parameter, e.g. lang=chv')
            return
        lang = params['lang'][0]
        if lang not in tts_models:
            self.send_error(501, 'That language is not supported')
            return

        if 'q' not in params:
            self.send_error(400, 'Missing q parameter, e.g. q=cалам')
            return
        q = params['q'][0]

        synth_file = NamedTemporaryFile()
        input_file = NamedTemporaryFile(delete=False)
        input_file.write(q)
        proc = Popen(split(tts_models[lang] % (synth_file.name, input_file.name)))

        input_file.close()

        self.send_response(200)
        self.send_header('Content-Type', 'audio/wav')
        self.send_header('Content-Disposition', 'attachment; filename=tts.wav')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        data = None
        while not data:
            data = synth_file.read(16384)
        while data:
            self.wfile.write(data)
            data = synth_file.read(16384)
        synth_file.close()

    def handle_list(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        dump({'langs': tts_models.keys()}, self.wfile)

    def do_GET(self):
        req = urlparse(self.path)
        if req.path == '/tts':
            self.handle_tts(parse_qs(req.query))
        elif req.path == '/list':
            self.handle_list()
        else:
            self.send_error(404, 'Endpoints are /tts and /list')

if __name__ == '__main__':
    httpd = HTTPServer((HOST, PORT), TTSRequestHandler)
    httpd.serve_forever()
