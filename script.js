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

function loadAudio() {
    document.getElementById('loadingCircle').classList.remove('hidden');
    var xhr = new XMLHttpRequest();
    var audio = document.getElementById('audioElement');
    var url = apy + '/tts?lang=chv&q=' + document.getElementById('input').value;

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
