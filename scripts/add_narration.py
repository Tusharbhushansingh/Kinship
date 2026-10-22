"""Add a descriptive speech track to the existing captioned Kinship demo.

Optional build dependency: system 'espeak' and ffmpeg; pip 'pydub'.
Video visuals remain unchanged. This is an automated/robotic English narration
that should be replaced by an authentic voice recording for a polished pitch.
"""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path
from pydub import AudioSegment

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'assets' / 'kinship-demo.mp4'
NARRATED = ROOT / 'assets' / 'kinship-demo-narrated.mp4'
SPEECH = [
    (0.12, 'Meet Kinship, a household co-pilot built with a real Model Context Protocol server.'),
    (6.15, 'Ask Kinship to plan a vegetarian dinner for four people, under fifteen dollars.'),
    (12.85, 'It checks pantry stock, compares five recipes, and selects coconut chickpea curry, within the budget.'),
    (22.85, 'The shopping list includes only missing ingredients. Two items cost an estimated four dollars and ten cents.'),
    (32.85, 'Mark groceries as purchased. Kinship updates the pantry and the amount remaining to spend.'),
    (41.85, 'Cooking tasks are shared between Alex and Sam. Completing a task saves the new status.'),
    (50.85, 'Ask, what is left to do? Kinship remembers the pending groceries and tasks, even after you reload.'),
    (59.35, 'Eight M C P tools power this Python backend. The interface simulates Alexa plus; it does not connect to an Echo device.'),
]

def main():
    for binary in ('espeak', 'ffmpeg', 'ffprobe'):
        if not shutil.which(binary):
            raise RuntimeError(f'Missing optional build tool: {binary}')
    duration_s = float(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(ORIGINAL)
    ]).decode().strip())
    audio = AudioSegment.silent(duration=int(duration_s * 1000) + 150, frame_rate=44100).set_channels(2)
    with tempfile.TemporaryDirectory() as tmp:
        for index, (start, words) in enumerate(SPEECH):
            filepath = Path(tmp) / f'voice_{index:02}.wav'
            subprocess.run(['espeak', '-v', 'en-us+m2', '-s', '164', '-p', '49', '-a', '145',
                            '-w', str(filepath), words], check=True)
            segment = AudioSegment.from_wav(filepath).set_frame_rate(44100).set_channels(2)
            segment = segment.fade_in(35).fade_out(70).apply_gain(-1.5)
            audio = audio.overlay(segment, position=round(start * 1000))
        audio = audio[:round(duration_s * 1000)]
        wav = Path(tmp) / 'narration.wav'
        audio.export(wav, format='wav')
        subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(ORIGINAL),
                        '-i', str(wav), '-map', '0:v:0', '-map', '1:a:0',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                        '-af', 'alimiter=limit=0.9', '-movflags', '+faststart', '-shortest',
                        str(NARRATED)], check=True)
    print(f'Created narrated demo: {NARRATED}')

if __name__ == '__main__':
    main()
