"""Optional developer utility: record an authentic, captioned ~68-second demo.

Requires playwright, requests, pillow and opencv-python, and local Chromium.
Video uses frames of an actually running local app; does not imply Alexa access.
"""
from __future__ import annotations
import io, json, os, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import requests
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PORT=8766
BASE=f'http://127.0.0.1:{PORT}'
OUT=ROOT/'assets'/'kinship-demo.mp4'
DB=Path('/tmp/kinship-video-data.db')
if DB.exists(): DB.unlink()
ENV=dict(os.environ,KINSHIP_DB=str(DB))
server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(PORT)],
                        cwd=ROOT,env=ENV,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
for i in range(70):
    try:
        if requests.get(BASE+'/api/health',timeout=.5).ok:break
    except requests.RequestException:time.sleep(.1)
else:
    raise RuntimeError('local demo server failed to start')

W,H=1280,720
fps=6
v=cv2.VideoWriter(str(OUT),cv2.VideoWriter_fourcc(*'mp4v'),fps,(W,H))
if not v.isOpened():raise RuntimeError('VideoWriter failed')
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(FONT,21)
font_small=ImageFont.truetype(FONT,15)
font_bold=ImageFont.truetype(BOLD,23)

def bridge(path,method,body):
 r=requests.request(method,BASE+path,data=body,headers={'Content-Type':'application/json'},timeout=10)
 try: js=r.json()
 except: js={'error':r.text}
 return {'status':r.status_code,'json':js}

def snap(page):
 data=page.screenshot(type='png',animations='disabled')
 return Image.open(io.BytesIO(data)).convert('RGB').resize((W,H),Image.Resampling.BICUBIC)

def frame(img,caption,sub='',seconds=5):
 count=int(seconds*fps)
 for t in range(count):
  im=img.copy().convert('RGBA')
  overlay=Image.new('RGBA',(W,H),(0,0,0,0));od=ImageDraw.Draw(overlay)
  od.rounded_rectangle((32, H-128, W-32, H-18),radius=18,fill=(22,20,36,234))
  od.rounded_rectangle((32,H-129,W-32,H-121),radius=4,fill=(153,126,227,130))
  od.rounded_rectangle((32,H-129,32+max(15,int((W-64)*(t+1)/count)),H-121),radius=4,fill=(183,161,255,255))
  od.text((54,H-115),caption,font=font_bold,fill=(248,245,255,255))
  if sub:od.text((54,H-77),sub,font=font,fill=(196,187,215,255))
  od.rounded_rectangle((W-250,24,W-25,59),radius=17,fill=(24,22,36,210))
  od.text((W-233,32),'MCP · LIVE DEMO',font=font_small,fill=(234,220,255,255))
  im=Image.alpha_composite(im,overlay).convert('RGB')
  v.write(cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR))

def animate_typing(page,command):
 for n in range(1,len(command)+1,2):
  page.locator('#prompt').fill(command[:n]);frame(snap(page),'One everyday request. Five coordinated actions.','Plain English in an Alexa+-inspired web simulator',seconds=0.40)

try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.getenv('CHROME_BIN','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':W,'height':H},device_scale_factor=1)
  html=(ROOT/'static/index.html').read_text().replace('<link rel="stylesheet" href="/static/styles.css" />','').replace('<script src="/static/app.js" defer></script>','')
  css=(ROOT/'static/styles.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');",'')
  page.expose_function('backendRequest',bridge)
  page.set_content(html)
  page.add_style_tag(content=css)
  page.evaluate("""() => {window.fetch = async (path, options = {}) => {const data=await window.backendRequest(path,options.method || 'GET', options.body||null); return {ok:data.status>=200&&data.status<300,status:data.status,json:async()=>data.json}}}""")
  page.add_script_tag(content=(ROOT/'static/app.js').read_text())
  page.wait_for_timeout(450)
  frame(snap(page),'Kinship — more living, less juggling','A real self-hosted MCP 2025-11-25 household co-pilot',seconds=6)
  page.locator('#prompt').scroll_into_view_if_needed()
  animate_typing(page,'Plan a vegetarian dinner for 4 under $15')
  page.locator('#prompt').fill('Plan a vegetarian dinner for 4 under $15')
  page.locator('#command-form button[type="submit"]').click()
  page.wait_for_timeout(750)
  assert page.locator('#stat-dinner').inner_text()=='Coconut chickpea curry'
  frame(snap(page),'Dinner planned: Coconut chickpea curry','Pantry, five recipes, budget and task allocation in one workflow',seconds=10)
  page.evaluate("window.scrollTo(0, document.querySelector('#plan').getBoundingClientRect().top + window.scrollY - 80)")
  page.wait_for_timeout(250)
  frame(snap(page),'Only missing ingredients make the shopping list','Two items needed · estimated cost $4.10 · within budget',seconds=10)
  page.evaluate("window.scrollTo(0, document.querySelector('#shopping').getBoundingClientRect().top + window.scrollY - 80)")
  page.locator('.shopping-toggle').first.click()
  page.wait_for_timeout(440)
  assert page.locator('#stat-spend').inner_text()=='$2.65'
  frame(snap(page),'Tick “purchased” — watch household state change','The shopping balance updates and pantry stock increases',seconds=9)
  page.evaluate("window.scrollTo(0, document.querySelector('#tasks').getBoundingClientRect().top + window.scrollY - 80)")
  page.locator('.task-toggle').first.click()
  page.wait_for_timeout(430)
  assert page.locator('#stat-tasks').inner_text()=='2 tasks'
  frame(snap(page),'Small steps shared between Alex and Sam','Finishing a task updates the persistent household database',seconds=9)
  page.locator('[data-prompt="What\'s left to do?"]').click()
  page.wait_for_timeout(500)
  page.evaluate("window.scrollTo(0, document.querySelector('.chat-card').getBoundingClientRect().top + window.scrollY - 75)")
  frame(snap(page),'Context-aware follow-up: “What’s left to do?”','Kinship recalls remaining groceries and incomplete tasks',seconds=9)
  headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':'2025-11-25'}
  mcp=requests.post(BASE+'/mcp',headers=headers,json={'jsonrpc':'2.0','id':9,'method':'tools/list'},timeout=5).json()
  assert len(mcp['result']['tools'])==8
  page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
  page.wait_for_timeout(150)
  frame(snap(page),'Under the hood: eight real MCP tools','POST /mcp · JSON-RPC 2.0 · spec version 2025-11-25',seconds=8)
  browser.close()
finally:
 v.release()
 server.terminate()
 try:server.wait(timeout=5)
 except subprocess.TimeoutExpired:server.kill()
print('Created',OUT,'size',OUT.stat().st_size,'bytes')
