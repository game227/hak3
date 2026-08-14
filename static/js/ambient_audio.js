/**
 * QuietSpace Tashkent — Advanced Zen Nature & Focus Audio Synthesizer (Web Audio API)
 * Zero external MP3 files! 100% procedurally synthesized in real-time.
 * 
 * Available Soundscapes:
 * 1. 🌧 Zen Yomg‘ir (Soft Rain)
 * 2. 🍃 O‘rmon Shamoli (Forest Breeze)
 * 3. 🐦 Bahoriy Qushlar (Spring Forest Birds)
 * 4. 🌊 Tog‘ Soyi (Mountain Stream)
 * 5. 🌊 Okean To‘lqinlari (Ocean Waves - Tidal ebb & flow)
 * 6. 🪵 Tungi Gulxan (Cozy Fireplace / Campfire crackle)
 * 7. 🦗 Yozgi Tun & Chigirtkalar (Summer Night Crickets)
 * 8. ☕️ Sokin Qahvaxona (Quiet Cafe Warmth)
 * 9. 🧠 432 Hz Deep Focus (Alpha Waves Harmonic Resonance)
 */

class ZenNatureSynthesizer {
    constructor() {
        this.ctx = null;
        this.isPlaying = false;
        this.currentSound = null;
        this.masterGain = null;
        this.volume = 0.25;
        this.nodes = [];
        this.intervals = [];
    }

    initContext() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContext();
            this.masterGain = this.ctx.createGain();
            this.masterGain.gain.setValueAtTime(this.volume, this.ctx.currentTime);
            this.masterGain.connect(this.ctx.destination);
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    setVolume(val) {
        this.volume = parseFloat(val);
        if (this.masterGain && this.ctx) {
            this.masterGain.gain.setTargetAtTime(this.volume, this.ctx.currentTime, 0.05);
        }
    }

    togglePlay(soundType) {
        this.initContext();
        if (this.isPlaying && this.currentSound === soundType) {
            this.stop();
            return false;
        } else {
            this.stop();
            this.currentSound = soundType;
            this.play(soundType);
            return true;
        }
    }

    stop() {
        this.isPlaying = false;
        this.intervals.forEach(i => clearInterval(i));
        this.intervals = [];

        this.nodes.forEach(n => {
            try {
                if (n.stop) n.stop();
                if (n.disconnect) n.disconnect();
            } catch (e) {}
        });
        this.nodes = [];
    }

    play(type) {
        this.initContext();
        this.isPlaying = true;
        this.currentSound = type;

        switch (type) {
            case 'rain': this.createRain(); break;
            case 'wind': this.createWind(); break;
            case 'birds': this.createBirds(); break;
            case 'stream': this.createStream(); break;
            case 'ocean': this.createOceanWaves(); break;
            case 'campfire': this.createCampfire(); break;
            case 'crickets': this.createCrickets(); break;
            case 'cafe': this.createCafeAmbience(); break;
            case 'focus432': this.create432HzFocus(); break;
            default: this.createRain(); break;
        }
    }

    // Helper: Pink/Brownian noise buffer
    createPinkNoiseBuffer(duration = 2) {
        const bufferSize = this.ctx.sampleRate * duration;
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;

        for (let i = 0; i < bufferSize; i++) {
            const white = Math.random() * 2 - 1;
            b0 = 0.99886 * b0 + white * 0.0555179;
            b1 = 0.99332 * b1 + white * 0.0750759;
            b2 = 0.96900 * b2 + white * 0.1538520;
            b3 = 0.86650 * b3 + white * 0.3104856;
            b4 = 0.55000 * b4 + white * 0.5329522;
            b5 = -0.7616 * b5 - white * 0.0168980;
            output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.04;
            b6 = white * 0.115926;
        }
        return noiseBuffer;
    }

    // ── 1. 🌧 Soft Zen Rain ──────────────────────────────────────────────────
    createRain() {
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createPinkNoiseBuffer(3);
        noise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(1150, this.ctx.currentTime);

        const highpass = this.ctx.createBiquadFilter();
        highpass.type = 'highpass';
        highpass.frequency.setValueAtTime(340, this.ctx.currentTime);

        noise.connect(filter);
        filter.connect(highpass);
        highpass.connect(this.masterGain);

        noise.start();
        this.nodes.push(noise, filter, highpass);
    }

    // ── 2. 🍃 Forest Wind ────────────────────────────────────────────────────
    createWind() {
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createPinkNoiseBuffer(3);
        noise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(380, this.ctx.currentTime);
        filter.Q.setValueAtTime(3.2, this.ctx.currentTime);

        const lfo = this.ctx.createOscillator();
        lfo.frequency.setValueAtTime(0.1, this.ctx.currentTime);
        const lfoGain = this.ctx.createGain();
        lfoGain.gain.setValueAtTime(220, this.ctx.currentTime);

        lfo.connect(lfoGain);
        lfoGain.connect(filter.frequency);

        noise.connect(filter);
        filter.connect(this.masterGain);

        lfo.start();
        noise.start();
        this.nodes.push(noise, filter, lfo, lfoGain);
    }

    // ── 3. 🐦 Spring Forest Birds ────────────────────────────────────────────
    createBirds() {
        this.createWind();

        const triggerChirp = () => {
            if (!this.isPlaying || !this.ctx) return;
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            const baseFreq = 2300 + Math.random() * 800;
            osc.type = 'sine';
            osc.frequency.setValueAtTime(baseFreq, now);
            osc.frequency.exponentialRampToValueAtTime(baseFreq + 500, now + 0.07);
            osc.frequency.exponentialRampToValueAtTime(baseFreq - 250, now + 0.15);

            gain.gain.setValueAtTime(0.001, now);
            gain.gain.linearRampToValueAtTime(0.09, now + 0.03);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);

            osc.connect(gain);
            gain.connect(this.masterGain);

            osc.start(now);
            osc.stop(now + 0.2);
        };

        const interval = setInterval(() => {
            if (Math.random() > 0.35) {
                triggerChirp();
                setTimeout(triggerChirp, 160 + Math.random() * 100);
            }
        }, 2100);
        this.intervals.push(interval);
    }

    // ── 4. 🌊 Mountain Stream ────────────────────────────────────────────────
    createStream() {
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createPinkNoiseBuffer(2.5);
        noise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(700, this.ctx.currentTime);
        filter.Q.setValueAtTime(2.2, this.ctx.currentTime);

        const lfo = this.ctx.createOscillator();
        lfo.frequency.setValueAtTime(0.4, this.ctx.currentTime);
        const lfoGain = this.ctx.createGain();
        lfoGain.gain.setValueAtTime(140, this.ctx.currentTime);

        lfo.connect(lfoGain);
        lfoGain.connect(filter.frequency);

        noise.connect(filter);
        filter.connect(this.masterGain);

        lfo.start();
        noise.start();
        this.nodes.push(noise, filter, lfo, lfoGain);
    }

    // ── 5. 🌊 Ocean Waves (Tidal Ebb & Flow) ──────────────────────────────────
    createOceanWaves() {
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createPinkNoiseBuffer(4);
        noise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(450, this.ctx.currentTime);

        const lfo = this.ctx.createOscillator();
        lfo.frequency.setValueAtTime(0.12, this.ctx.currentTime); // ~8s wave period
        const lfoGain = this.ctx.createGain();
        lfoGain.gain.setValueAtTime(320, this.ctx.currentTime);

        const waveGain = this.ctx.createGain();
        const ampLfo = this.ctx.createOscillator();
        ampLfo.frequency.setValueAtTime(0.12, this.ctx.currentTime);
        const ampLfoGain = this.ctx.createGain();
        ampLfoGain.gain.setValueAtTime(0.4, this.ctx.currentTime);

        lfo.connect(lfoGain);
        lfoGain.connect(filter.frequency);

        ampLfo.connect(ampLfoGain);
        ampLfoGain.connect(waveGain.gain);

        noise.connect(filter);
        filter.connect(waveGain);
        waveGain.connect(this.masterGain);

        lfo.start();
        ampLfo.start();
        noise.start();
        this.nodes.push(noise, filter, lfo, lfoGain, waveGain, ampLfo, ampLfoGain);
    }

    // ── 6. 🪵 Cozy Campfire / Fireplace Crackle ──────────────────────────────
    createCampfire() {
        // Soft low roar base
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createPinkNoiseBuffer(2);
        noise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(280, this.ctx.currentTime);

        noise.connect(filter);
        filter.connect(this.masterGain);
        noise.start();
        this.nodes.push(noise, filter);

        // Crackling sparks
        const triggerPop = () => {
            if (!this.isPlaying || !this.ctx) return;
            const now = this.ctx.currentTime;
            const buffer = this.ctx.createBuffer(1, this.ctx.sampleRate * 0.03, this.ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < data.length; i++) {
                data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.005));
            }
            const spark = this.ctx.createBufferSource();
            spark.buffer = buffer;
            const sparkGain = this.ctx.createGain();
            sparkGain.gain.setValueAtTime(0.35 + Math.random() * 0.35, now);

            spark.connect(sparkGain);
            sparkGain.connect(this.masterGain);
            spark.start(now);
        };

        const interval = setInterval(() => {
            if (Math.random() > 0.4) {
                triggerPop();
                if (Math.random() > 0.6) setTimeout(triggerPop, 50 + Math.random() * 80);
            }
        }, 120);
        this.intervals.push(interval);
    }

    // ── 7. 🦗 Summer Night Crickets ──────────────────────────────────────────
    createCrickets() {
        // High pitched rhythmic cricket chirp
        const triggerCricket = () => {
            if (!this.isPlaying || !this.ctx) return;
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(4600 + Math.random() * 300, now);

            gain.gain.setValueAtTime(0.001, now);
            gain.gain.linearRampToValueAtTime(0.05, now + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.08);

            osc.connect(gain);
            gain.connect(this.masterGain);

            osc.start(now);
            osc.stop(now + 0.1);
        };

        const interval = setInterval(() => {
            triggerCricket();
            setTimeout(triggerCricket, 70);
            setTimeout(triggerCricket, 140);
        }, 1400);
        this.intervals.push(interval);
    }

    // ── 8. ☕️ Quiet Cafe Ambience ────────────────────────────────────────────
    createCafeAmbience() {
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createPinkNoiseBuffer(3);
        noise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(600, this.ctx.currentTime);

        const highpass = this.ctx.createBiquadFilter();
        highpass.type = 'highpass';
        highpass.frequency.setValueAtTime(200, this.ctx.currentTime);

        noise.connect(filter);
        filter.connect(highpass);
        highpass.connect(this.masterGain);

        noise.start();
        this.nodes.push(noise, filter, highpass);
    }

    // ── 9. 🧠 432 Hz Deep Focus (Alpha Binaural Harmonic Waves) ──────────────
    create432HzFocus() {
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        // 432 Hz base & 442 Hz (10 Hz Alpha Wave difference)
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(432, this.ctx.currentTime);

        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(442, this.ctx.currentTime);

        gain.gain.setValueAtTime(0.12, this.ctx.currentTime);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(this.masterGain);

        osc1.start();
        osc2.start();
        this.nodes.push(osc1, osc2, gain);
    }
}

// Global Synthesizer Instance
window.zenAudio = new ZenNatureSynthesizer();

const ZEN_SOUND_NAMES = {
    'rain': '🌧 Zen Yomg‘ir',
    'wind': '🍃 O‘rmon Shamoli',
    'birds': '🐦 Bahoriy Qushlar',
    'stream': '🌊 Tog‘ Soyi',
    'ocean': '🌊 Okean To‘lqinlari',
    'campfire': '🪵 Tungi Gulxan',
    'crickets': '🦗 Yozgi Chigirtkalar',
    'cafe': '☕️ Sokin Qahvaxona',
    'focus432': '🧠 432 Hz Deep Focus'
};

function selectZenSound(type) {
    const isPlaying = window.zenAudio.togglePlay(type);
    updateZenAudioUI(type, isPlaying);
}

function updateZenAudioUI(type, isPlaying) {
    const btn = document.getElementById('zen-audio-toggle');
    const eqBars = document.getElementById('zen-eq-bars');
    const title = document.getElementById('zen-audio-title');

    // Update active sound pill in drawer
    document.querySelectorAll('.zen-sound-card').forEach(c => {
        if (c.getAttribute('data-sound') === type && isPlaying) {
            c.classList.add('active');
        } else {
            c.classList.remove('active');
        }
    });

    if (isPlaying) {
        if (btn) btn.classList.add('playing');
        if (eqBars) eqBars.classList.remove('d-none');
        if (title) title.textContent = ZEN_SOUND_NAMES[type] || '🔊 Sokin Ambience';
    } else {
        if (btn) btn.classList.remove('playing');
        if (eqBars) eqBars.classList.add('d-none');
        if (title) title.textContent = '🔊 Sokin Ambience';
    }
}

function toggleZenSoundboardDrawer(e) {
    if (e) e.stopPropagation();
    const drawer = document.getElementById('zen-soundboard-modal');
    if (drawer) {
        drawer.classList.toggle('show');
    }
}
