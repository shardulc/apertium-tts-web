#!/usr/bin/env python
# coding=utf-8

# server.py
# The back end of Apertium TTS Web. See README for usage details, and see
# LICENSE for license details (GPLv3+).
# Copyright (C) 2018, Shardul Chiplunkar <shardul.chiplunkar@gmail.com>

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from json import dump
from os import devnull, remove
from shlex import split
from subprocess import Popen
from tempfile import NamedTemporaryFile
from urlparse import parse_qs, urlparse


HOST = "0.0.0.0"
PORT = 2738

tts_models = {
    'chv': 'python /home/ossian/Ossian/scripts/speak.py -l chv -s news -o {0} naive_01_nn {1}',
    'zzz': 'cat /home/ossian/public_html/chuvash_test3.wav > {0}'
}

lang_names = {
    'eng': {
        'chv': 'Chuvash',
        'zzz': 'Dummy'
    }
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
            self.send_error(400, 'Missing q parameter, e.g. q=c\u0430\u043\u0430\u043c')
            return
        q = params['q'][0]

        synth_file = NamedTemporaryFile()
        input_file = NamedTemporaryFile(delete=False)
        null = open(devnull, 'w')
        input_file.write(q)
        Popen(split(tts_models[lang].format(synth_file.name, input_file.name)), stdout=null)
        input_file.close()
        null.close()

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

    def handle_list(self, params):
        if 'lang' not in params:
            self.send_error(400, 'Missing lang parameter, e.g. lang=eng')
            return
        lang = params['lang'][0]
        if lang not in lang_names:
            self.send_error(501, 'That language is not supported')
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        dump(lang_names[lang], self.wfile)

    def do_GET(self):
        req = urlparse(self.path)
        if req.path == '/tts':
            self.handle_tts(parse_qs(req.query))
        elif req.path == '/list':
            self.handle_list(parse_qs(req.query))
        else:
            self.send_error(404, 'Endpoints are /tts and /list')


if __name__ == '__main__':
    httpd = HTTPServer((HOST, PORT), TTSRequestHandler)
    httpd.serve_forever()
