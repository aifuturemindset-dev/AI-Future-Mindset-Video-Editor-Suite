#!/usr/bin/env python3
"""Synthesise a sound-effect bed from a cue list.

Storyboards specify sound design - a pattern-interrupt drone, a ticking
clock, a whoosh, a success chime - and in a sandbox every sample library is
unreachable: freesound, pixabay and archive.org all fail here. These effects
are simple enough to generate, which also makes them royalty-free and tunable
to the cut rather than trimmed to fit it.

Nothing here is a substitute for a real library if one is available. It is a
substitute for having no sound design at all.

Each generator returns a stereo float array at 48 kHz, peak-normalised; the
caller sets the level. Filtering is done in the frequency domain because the
effects are short and it keeps the code readable.

Usage as a library:
    from soundbed import render_bed
    render_bed(cues, total_seconds, "bed.wav")

where cues is [{"at": 12.5, "fx": "whoosh", "gain_db": -20}, ...]
"""

import numpy as np

SR = 48000


# ---------------------------------------------------------------- helpers

def _t(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)


def _env(n, attack, decay, hold=0.0):
    """Attack / hold / exponential decay, in seconds."""
    a = max(1, int(attack * SR))
    h = int(hold * SR)
    d = max(1, n - a - h)
    return np.concatenate([
        np.linspace(0, 1, a),
        np.ones(h),
        np.exp(-np.linspace(0, 5, d)),
    ])[:n]


def _band(x, low=None, high=None):
    """Zero-phase band limit via FFT. Fine for short, non-critical effects."""
    spec = np.fft.rfft(x)
    freq = np.fft.rfftfreq(len(x), 1 / SR)
    if low is not None:
        spec *= 1 / (1 + (low / np.maximum(freq, 1e-6)) ** 4)
    if high is not None:
        spec *= 1 / (1 + (freq / high) ** 4)
    return np.fft.irfft(spec, n=len(x))


def _noise(dur):
    return np.random.default_rng(7).standard_normal(int(SR * dur))


def _bell(freq, dur, ratio=3.5, index=6.0):
    """FM bell - the cheapest convincing glass/chime timbre."""
    t = _t(dur)
    mod = np.sin(2 * np.pi * freq * ratio * t) * index * np.exp(-t * 6)
    return np.sin(2 * np.pi * freq * t + mod) * np.exp(-t * 4.5)


def _stereo(x, spread=0.0):
    """Mono to stereo, optionally with a small haas-style spread."""
    if spread <= 0:
        return np.stack([x, x], axis=1)
    d = int(spread * SR)
    left = np.concatenate([x, np.zeros(d)])
    right = np.concatenate([np.zeros(d), x])
    return np.stack([left, right], axis=1)


def _norm(x):
    peak = np.max(np.abs(x))
    return x / peak if peak > 1e-9 else x


# ------------------------------------------------------------ generators

def digital_pulse():
    """Sharp digital pulse over a low drone. Slide 1 pattern interrupt."""
    dur = 3.2
    t = _t(dur)
    ping = np.sin(2 * np.pi * 1320 * t) * _env(len(t), 0.001, 0.2)
    drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.5 * t))
    drone *= np.minimum(1, t / 0.6) * np.exp(-t * 0.5)
    return _stereo(_norm(ping * 0.7 + drone * 0.5), 0.012)


def paper_shuffle():
    """Paper handling with a glass resonance underneath. Slide 2."""
    dur = 1.6
    n = int(SR * dur)
    x = np.zeros(n)
    rng = np.random.default_rng(3)
    for start in (0.0, 0.22, 0.46, 0.72):
        seg = _band(rng.standard_normal(int(SR * 0.28)), low=1800, high=9000)
        seg *= _env(len(seg), 0.004, 0.2)
        i = int(start * SR)
        x[i:i + len(seg)] += seg[:max(0, n - i)]
    chime = _bell(1568, dur, ratio=2.4, index=3.0) * 0.28
    return _stereo(_norm(x * 0.9 + chime), 0.01)


def ticking_clock():
    """Ticks accelerating, cut off by a soft bass drop. Slide 3."""
    dur = 4.0
    n = int(SR * dur)
    x = np.zeros(n)
    rng = np.random.default_rng(11)
    pos, gap = 0.0, 0.52
    while pos < 2.9:
        click = _band(rng.standard_normal(int(SR * 0.04)), low=1200, high=6000)
        click *= _env(len(click), 0.0005, 0.03)
        i = int(pos * SR)
        x[i:i + len(click)] += click[:max(0, n - i)]
        pos += gap
        gap *= 0.86                      # winding up
    t = _t(dur)
    drop = np.sin(2 * np.pi * np.cumsum(np.linspace(120, 38, n)) / SR)
    mask = np.clip((t - 2.95) * 3, 0, 1) * np.exp(-np.maximum(0, t - 2.95) * 1.6)
    return _stereo(_norm(x * 0.8 + drop * mask * 0.9), 0.008)


def synth_pad():
    """Warm swelling pad for the reframe. Slide 4."""
    dur = 4.5
    t = _t(dur)
    voices = sum(np.sin(2 * np.pi * f * t) for f in (196, 246.9, 293.7, 392))
    swell = np.minimum(1, t / 1.8) * np.exp(-np.maximum(0, t - 2.2) * 0.9)
    return _stereo(_norm(_band(voices, high=3200) * swell), 0.02)


def metallic_click():
    """Heavy glass/metal click. Slide 5."""
    dur = 1.4
    body = _band(_noise(dur), low=300, high=5200) * _env(int(SR * dur), 0.002, 0.12)
    ring = _bell(523, dur, ratio=5.1, index=4.0) * 0.4
    return _stereo(_norm(body * 0.8 + ring), 0.006)


def whoosh():
    """High-energy transition into a bright chime. Slide 6."""
    dur = 2.2
    n = int(SR * dur)
    t = _t(dur)
    sweep = _noise(dur)
    spec = np.fft.rfft(sweep)
    freq = np.fft.rfftfreq(n, 1 / SR)
    spec *= 1 / (1 + (freq / 5000) ** 2)
    air = np.fft.irfft(spec, n=n)
    air *= np.exp(-((t - 0.75) ** 2) / 0.09)
    chime = np.zeros(n)
    c = _bell(2093, 1.3, ratio=2.0, index=2.5)
    i = int(0.85 * SR)
    chime[i:i + len(c)] += c[:max(0, n - i)]
    return _stereo(_norm(air * 0.9 + chime * 0.6), 0.015)


def mechanical_notches():
    """Ascending notch clicks driving momentum. Slide 7."""
    dur = 2.6
    n = int(SR * dur)
    x = np.zeros(n)
    for k, start in enumerate((0.0, 0.42, 0.84)):
        f = 660 * (1.26 ** k)
        c = _bell(f, 1.0, ratio=1.5, index=2.0)
        i = int(start * SR)
        x[i:i + len(c)] += c[:max(0, n - i)] * 0.9
    return _stereo(_norm(x), 0.01)


def airflow_rings():
    """Suction resolving into three crystal rings. Slide 8."""
    dur = 3.4
    n = int(SR * dur)
    t = _t(dur)
    suction = _band(_noise(dur), low=500, high=4000)
    suction *= np.exp(-((t - 0.6) ** 2) / 0.12)
    rings = np.zeros(n)
    for k, start in enumerate((1.25, 1.62, 1.99)):
        c = _bell(1760 * (1.19 ** k), 1.4, ratio=2.1, index=2.2)
        i = int(start * SR)
        rings[i:i + len(c)] += c[:max(0, n - i)] * 0.75
    return _stereo(_norm(suction * 0.7 + rings), 0.014)


def static_to_tone():
    """Low static resolving into a clear tone. Slide 9 identity shift."""
    dur = 3.6
    n = int(SR * dur)
    t = _t(dur)
    rumble = _band(_noise(dur), high=900) * np.clip(1 - t / 1.9, 0, 1)
    tone = np.sin(2 * np.pi * 659.3 * t) * np.clip((t - 1.4) / 1.0, 0, 1)
    tone *= np.exp(-np.maximum(0, t - 2.6) * 1.4)
    return _stereo(_norm(rumble * 0.6 + tone * 0.55), 0.018)


def bass_riser():
    """Deep riser with a pulse beat. Slide 10, the offer."""
    dur = 4.0
    n = int(SR * dur)
    t = _t(dur)
    sweep = np.sin(2 * np.pi * np.cumsum(np.linspace(45, 190, n)) / SR)
    sweep *= np.minimum(1, t / 2.6)
    pulse = np.zeros(n)
    for start in np.arange(0.0, 3.6, 0.45):
        p = np.sin(2 * np.pi * 70 * _t(0.14)) * _env(int(SR * 0.14), 0.002, 0.1)
        i = int(start * SR)
        pulse[i:i + len(p)] += p[:max(0, n - i)]
    return _stereo(_norm(sweep * 0.7 + pulse * 0.6), 0.008)


def success_chime():
    """Bright two-note confirmation. Slide 11, the victory anchor."""
    dur = 2.4
    n = int(SR * dur)
    x = np.zeros(n)
    for f, start in ((1046.5, 0.0), (1568.0, 0.16)):
        c = _bell(f, 1.8, ratio=2.0, index=2.0)
        i = int(start * SR)
        x[i:i + len(c)] += c[:max(0, n - i)] * 0.8
    return _stereo(_norm(x), 0.012)


def resonant_swell():
    """Deep swell resolving into silence. Slide 12, the close."""
    dur = 5.0
    t = _t(dur)
    low = sum(np.sin(2 * np.pi * f * t) for f in (65.4, 98, 130.8))
    low *= np.minimum(1, t / 1.6) * np.exp(-np.maximum(0, t - 2.0) * 0.7)
    return _stereo(_norm(_band(low, high=1800)), 0.02)


FX = {
    "digital_pulse": digital_pulse,
    "paper_shuffle": paper_shuffle,
    "ticking_clock": ticking_clock,
    "synth_pad": synth_pad,
    "metallic_click": metallic_click,
    "whoosh": whoosh,
    "mechanical_notches": mechanical_notches,
    "airflow_rings": airflow_rings,
    "static_to_tone": static_to_tone,
    "bass_riser": bass_riser,
    "success_chime": success_chime,
    "resonant_swell": resonant_swell,
}


def render_bed(cues, total_seconds, out_path):
    """Lay the cues onto a silent stereo bed and write a 24-bit WAV.

    A cue is {"at": seconds, "fx": name, "gain_db": level}. Levels are set
    per cue rather than globally because a drone under speech and a chime in
    a gap want very different amounts.
    """
    import wave

    n = int(SR * total_seconds)
    bed = np.zeros((n, 2))
    for cue in cues:
        gen = FX.get(cue["fx"])
        if gen is None:
            raise KeyError(f"unknown effect {cue['fx']!r}")
        clip = gen() * (10 ** (cue.get("gain_db", -20) / 20))
        i = int(cue["at"] * SR)
        end = min(n, i + len(clip))
        if end > i:
            bed[i:end] += clip[: end - i]

    peak = np.max(np.abs(bed))
    if peak > 0.99:
        bed *= 0.99 / peak
    data = (bed * 32767).astype("<i2")

    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    return out_path
