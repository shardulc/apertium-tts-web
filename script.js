/**
 * script.js
 * JavaScript for the front end of Apertium TTS Web. See README for usage
 * details, and see LICENSE for license details (GPLv3+).
 * Copyright (C) 2018, Shardul Chiplunkar <shardul.chiplunkar@gmail.com>
 */

var apy = 'http://yukari.default.ftyers.uk0.bigv.io:2738';
var currentAudioUrl;
var loadables = document.getElementsByClassName('loadable');
var aboutModal = document.getElementById('aboutModalContainer');
var pageLang = 'eng';

var strings = {
    'eng': {
        'Apertium Text-to-Speech': 'Apertium Text-to-Speech',
        'Apertium': 'Apertium',
        'Text-to-Speech': 'Text-to-Speech',
        'chv': 'Chuvash',
        'eng': 'English',
        'Listen': 'Listen',
        'About': 'About',
        'AboutText':
            '<p><a href="http://wiki.apertium.org/wiki/Main_Page">Apertium</a> is a free/open-source language technology platform. This is Apertium TTS Web, a web server and interface providing a free/open-source text-to-speech service.</p>\
            <p>The code for <a href="https://github.com/shardulc/apertium-tts-web">Apertium TTS Web</a> is licensed under the GPLv3+. See the LICENSE file in the linked GitHub repository for more details. Note that the license does <i>not</i> include the program producing audio from text, but only this interface and the server that serves the audio.</p>\
            <p>Apertium TTS Web is written and maintained by Shardul Chiplunkar (email: firstname DOT lastname AT gmail DOT com).</p>'
    },
    'chv': {
        'chv': 'Чӑвашла',
        'Listen': 'Итле'
    }
}

window.onload = function() {
    getTextLangs();
}

function getTextLangs() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', encodeURI(apy + '/list'), true);
    xhr.onreadystatechange = function() {
        if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var textLangs = JSON.parse(xhr.responseText);
            var select = document.getElementById('textLangs');
            while(select.firstChild) {
                select.removeChild(select.lastChild);
            }
            for (var lang of textLangs) {
                var opt = document.createElement('option');
                opt.appendChild(document.createTextNode(strings[pageLang][lang]));
                opt.setAttribute('data-text', lang);
                opt.classList.add('localizable');
                select.appendChild(opt);
            }
        }
    }
    xhr.send();
}

function localize() {
    var pageLangs = document.getElementById('pageLangs');
    pageLang = pageLangs.options[pageLangs.selectedIndex].getAttribute('data-text');
    for (var elem of document.getElementsByClassName('localizable')) {
        var text = strings[pageLang][elem.getAttribute('data-text')];
        if (text !== undefined) {
            elem.innerHTML = text;
        } else {
            elem.innerHTML = strings['eng'][elem.getAttribute('data-text')];
        }
    }
}

function loadAudio() {
    document.getElementById('loadingCircle').classList.remove('hidden');
    var xhr = new XMLHttpRequest();
    var audio = document.getElementById('audioElement');
    var select = document.getElementById('textLangs');
    var lang = select.options[select.selectedIndex].getAttribute('data-text');
    var url = apy + '/tts?lang=' + lang + '&q=' + document.getElementById('input').value;

    xhr.open('GET', encodeURI(url), true);
    xhr.setRequestHeader('Content-Type', 'text/plain');
    xhr.responseType = 'blob';
    xhr.onreadystatechange = function(evt) {
        if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            document.getElementById('loadingCircle').classList.add('hidden');
            var blob = new Blob([xhr.response], {type: 'audio/wav'});
            if (currentAudioUrl !== undefined) {
                URL.revokeObjectURL(currentAudioUrl);
            }
            var currentAudioUrl = URL.createObjectURL(blob);
            audio.src = currentAudioUrl;
            document.getElementById('download').href = currentAudioUrl;
            enableAudio();
        }
    };
    xhr.send();
}

function disableAudio() {
    for (var elem of loadables) {
        elem.classList.add('hidden');
    }
}

function enableAudio() {
    for (var elem of loadables) {
        elem.classList.remove('hidden');
    }
}

function showAboutModal() {
    aboutModalContainer.classList.remove('hidden');
}

function hideAboutModal() {
    aboutModalContainer.classList.add('hidden');
}

window.onclick = function(event) {
    if(event.target == aboutModalContainer) {
        hideAboutModal();
    }
}
