'use strict';
const $ = id => document.getElementById(id);
const e = s => String(s ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const money = n => '$' + Number(n||0).toFixed(2);
let busy = false;
async function api(path, options = {}) {
 const res = await fetch(path, {headers:{'Content-Type':'application/json'}, ...options});
 let data; try {data = await res.json()} catch {throw new Error('Server unavailable')}
 if (!res.ok) throw new Error(data.detail || data.error || `Request failed (${res.status})`);
 return data;
}
function toast(txt) {
 const el=document.createElement('div');el.className='notify';el.textContent=txt;document.body.appendChild(el);
 setTimeout(()=>el.remove(),3300);
}
function render(state) {
 const p = state.plan;
 $('stat-dinner').textContent = p ? p.recipe_name : 'Not planned yet';
 $('stat-spend').textContent = money(state.shopping_total);
 $('stat-tasks').textContent = `${state.tasks_pending} ${state.tasks_pending===1?'task':'tasks'}`;
 if (!p) {
  $('dinner-content').innerHTML='<div class="empty"><span class="empty-icon">🍲</span><h4>Good things are cooking</h4><p>Your dinner plan will appear here after you ask Kinship.</p></div>';
  $('shopping-content').innerHTML='<div class="empty"><span class="empty-icon">🛒</span><h4>Nothing on the list</h4><p>Plan a meal and we\'ll find what\'s missing from your pantry.</p></div>';
  $('task-content').innerHTML='<div class="empty compact"><span class="empty-icon">✳</span><p>A little coordination goes a long way.</p></div>';
  return;
 }
 $('dinner-content').innerHTML=`<div class="recipe-title"><span class="recipe-emoji">${e(p.emoji)}</span><div><h4>${e(p.recipe_name)}</h4><small>Made for ${e(p.servings)} · ${e(p.minutes)} min</small></div></div><div class="pillrow"><span class="softpill">🥬 Vegetarian</span><span class="softpill">🏠 ${e(p.pantry_used)} pantry units used</span><span class="softpill ${p.within_budget?'ok':'warn'}">${p.within_budget?'✓ On budget':'⚠ Over budget'}</span></div><div class="reason"><strong>Why this meal?</strong> ${e(p.reason)}</div>`;
 $('shopping-content').innerHTML = state.shopping.length ? `<div>${state.shopping.map(i=>`<label class="shopping-row"><input aria-label="Mark ${e(i.name)} purchased" class="shopping-toggle" data-id="${e(i.id)}" type="checkbox" ${i.purchased?'checked disabled':''}/><span class="item-icon">${e(i.icon)}</span><span><div class="item-name ${i.purchased?'crossed':''}">${e(i.name)}</div><div class="item-meta">${e(i.quantity)} × ${e(i.unit)} · ${money(i.price)} each</div></span><span class="price">${money(i.price*i.quantity)}</span></label>`).join('')}</div><div class="shopping-total"><span>Still to buy</span><b>${money(state.shopping_total)}</b></div>` : '<p class="reason">Everything you need is already in the pantry.</p>';
 $('task-content').innerHTML = `<div>${state.tasks.map(t=>`<label class="task-row"><input class="task-toggle" type="checkbox" data-id="${e(t.id)}" ${t.done?'checked disabled':''} aria-label="Complete ${e(t.title)}"/><span><div class="item-name ${t.done?'crossed':''}">${e(t.title)}</div><div class="item-meta">${t.done?'Completed':'Ready when you are'}</div></span><span class="owner">${e(t.owner)}</span></label>`).join('')}</div>`;
 document.querySelectorAll('.shopping-toggle').forEach(el=>el.addEventListener('change', async ()=>{
  try {let result=await api('/api/shopping/'+encodeURIComponent(el.dataset.id)+'/purchased',{method:'POST'}); toast(result.message);await refresh()} catch(err){toast(err.message);await refresh()}
 }));
 document.querySelectorAll('.task-toggle').forEach(el=>el.addEventListener('change', async ()=>{
  try {let result=await api('/api/tasks/'+encodeURIComponent(el.dataset.id)+'/complete',{method:'POST'});toast('Task completed!');await refresh()} catch(err){toast(err.message);await refresh()}
 }));
}
async function refresh(){render(await api('/api/state'))}
function bubble(message,role='bot'){
 const el=document.createElement('div');el.className='bubble '+role;
 if(role==='bot'){const icon=document.createElement('span');icon.textContent='✳';el.appendChild(icon)}
 const p=document.createElement('p');p.textContent=message;el.appendChild(p);
 $('messages').appendChild(el);$('messages').scrollTop=$('messages').scrollHeight;
}
async function send(text){
 if(busy)return; text=text.trim();if(!text)return;busy=true;$('prompt').value='';bubble(text,'user');
 try{const result=await api('/api/message',{method:'POST',body:JSON.stringify({text})});bubble(result.message||'Done.');await refresh()}catch(err){bubble('I ran into a problem: '+err.message)}finally{busy=false}
}
$('command-form').addEventListener('submit',event=>{event.preventDefault();send($('prompt').value)});
document.querySelectorAll('[data-prompt]').forEach(el=>el.addEventListener('click',()=>send(el.dataset.prompt)));
$('hero-demo').addEventListener('click',()=>{send('Plan a vegetarian dinner for 4 under $15');$('dashboard').scrollIntoView({behavior:'smooth'});});
$('reset').addEventListener('click',async()=>{if(busy)return;try{await api('/api/reset',{method:'POST'});$('messages').innerHTML='';bubble('Demo reset. Ready for a fresh dinner plan!');await refresh();toast('Household data reset')}catch(err){toast(err.message)}});
$('mic').addEventListener('click',()=>{
 const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
 if(!Recognition){toast('Browser speech recognition is not available. Type your request instead.');return}
 const rec=new Recognition();rec.lang='en-US';rec.interimResults=false;rec.maxAlternatives=1;
 rec.onresult=event=>{let words=event.results[0][0].transcript;$('prompt').value=words;send(words)};
 rec.onerror=event=>toast('Speech recognition: '+event.error);rec.start();toast('Listening… browser voice input');
});
refresh().catch(err=>toast('Could not connect: '+err.message));
