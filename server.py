#!/usr/bin/env python3
# coding=utf-8

# server.py
# The back end of Apertium TTS Web. See README for usage details, and see
# LICENSE for license details (GPLv3+).
# Copyright (C) 2018, Shardul Chiplunkar <shardul.chiplunkar@gmail.com>

from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps
from os import remove
from shlex import split
from subprocess import Popen
from tempfile import NamedTemporaryFile
from urllib.parse import parse_qs, urlparse


HOST = "0.0.0.0"
PORT = 2738

tts_models = {
    'chv': 'python2.7 ./Ossian/scripts/speak.py -l chv -s news -o {0} naive_01_nn {1}',
#    'zzz': 'cp ./chuvash_test3.wav {0}'  # uncomment for dummy audio testing
}

sanitizers = {
    'chv': {
        'ӑ': ['ă', 'ǎ'],
        'ӗ': ['ĕ', 'ě'],
        'ӳ': ['ÿ'],
        'ҫ': ['ç']
    },
    'zzz': {}
}


class TTSRequestHandler(BaseHTTPRequestHandler):

    # override https://github.com/python/cpython/blob/master/Lib/http/server.py#L492
    # because latin-1 --> utf-8 <sigh>
    def send_response_only(self, code, message=None):
        """Send the response header only."""
        if self.request_version != 'HTTP/0.9':
            if message is None:
                if code in self.responses:
                    message = self.responses[code][0]
                else:
                    message = ''
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(("%s %d %s\r\n" %
                    (self.protocol_version, code, message)).encode('utf-8'))

    def handle_tts(self, params):
        if 'lang' not in params:
            self.send_error(400, 'Missing lang parameter, e.g. lang=chv')
            return
        lang = params['lang'][0]
        if lang not in tts_models:
            self.send_error(501, 'That language is not supported')
            return

        if 'q' not in params:
            self.send_error(400, 'Missing q parameter, e.g. q=салам')
            return
        q = params['q'][0]
        for clean in sanitizers[lang]:
            for dirty in sanitizers[lang][clean]:
                q.replace(dirty, clean)

        synth_file = NamedTemporaryFile()
        input_file = NamedTemporaryFile(delete=False)
        input_file.write(q.encode('utf-8'))
        Popen(split(tts_models[lang].format(synth_file.name, input_file.name)))
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
        remove(input_file.name)

    def handle_list(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(dumps(list(tts_models.keys())).encode('utf-8'))

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
