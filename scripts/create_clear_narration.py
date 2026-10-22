"""Make a slower, clearly enunciated synthetic voiceover for the demo.

Requires espeak, ffmpeg, and pydub. This is still an offline synthetic voice,
not professional natural speech. See docs/RECORD_YOUR_VOICE.md for a human VO.
"""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path
from pydub import AudioSegment

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / 'assets' / 'kinship-demo.mp4'
OUTPUT = ROOT / 'assets' / 'kinship-demo-clear-voice.mp4'
AUDIO_OUT = ROOT / 'assets' / 'kinship-clear-narration.wav'
# Keep short, easy-to-follow sentences. Segment starts match live-demo sequence.
LINES = [
 (0.5, 'This is Kinship, a household helper powered by M C P.'),
 (6.5, 'Ask it to plan dinner for four people, for under fifteen dollars.'),
 (14.2, "It checks the pantry and five recipes. Tonight's choice is chickpea curry."),
 (23.5, 'Only missing ingredients go on your shopping list. The total is four dollars and ten cents.'),
 (33.4, 'Mark an item as purchased. The pantry and budget update automatically.'),
 (42.1, 'Alex and Sam share cooking tasks. Tick a task when it is done.'),
 (51.3, 'Ask, what is left to do? Kinship remembers your unfinished tasks.'),
 (59.5, 'Eight M C P tools run this demo. It does not connect to Alexa.'),
]

def main() -> None:
 for name in ('ffmpeg','ffprobe','espeak'):
  if not shutil.which(name): raise RuntimeError(f'{name} must be installed')
 duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries', 'format=duration','-of','default=nw=1:nk=1',str(VIDEO)]))
 audio = AudioSegment.silent(duration=int(duration * 1000), frame_rate=48000).set_channels(2)
 with tempfile.TemporaryDirectory() as tmp:
  for idx, (start, line) in enumerate(LINES):
   wav = Path(tmp) / f'clip_{idx}.wav'
   subprocess.run(['espeak','-v','en-us','-s','145','-p','50','-a','155','-g','4','-w',str(wav),line],check=True)
   seg = AudioSegment.from_file(wav).set_frame_rate(48000).set_channels(2)
   seg = seg.fade_in(60).fade_out(85)
   next_start = LINES[idx+1][0] if idx+1 < len(LINES) else duration
   if start + seg.duration_seconds > next_start + 0.07:
    raise ValueError(f'Narration segment {idx} overlaps scene boundary by {start+seg.duration_seconds-next_start:.1f}s')
   audio = audio.overlay(seg,position=round(start*1000))
  audio.export(AUDIO_OUT,format='wav')
  subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(VIDEO),'-i',str(AUDIO_OUT),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-ar','48000','-af', 'highpass=f=110,lowpass=f=7800,acompressor=threshold=-18dB:ratio=2:attack=15:release=200,loudnorm=I=-17:TP=-1.5:LRA=9', '-movflags','+faststart','-shortest',str(OUTPUT)],check=True)
 print(f'Created {OUTPUT}, {OUTPUT.stat().st_size:,} bytes')

if __name__ == '__main__': main()
