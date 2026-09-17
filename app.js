const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const API_BASE = location.protocol === 'chrome-extension:' ? 'http://127.0.0.1:8787' : '';
const request = async (url, options={}) => {
  let response;
  try { response = await fetch(`${API_BASE}${url}`, options); }
  catch { throw new Error('TwinTimes service is offline. Start it with ./run.sh, then try again.'); }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
};
const post = (url, body={}) => request(url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
let digest = {top:[], sections:[], deep:[]};
let bookmarks = [];

function toast(message) {
  const node = $('#toast'); if (!node) return;
  node.textContent = message; node.classList.add('show');
  clearTimeout(toast.timer); toast.timer = setTimeout(() => node.classList.remove('show'), 2400);
}
function excerpt(story, length=165) {
  const text = story.summary || story.why || 'Selected for relevance, timeliness, and significance.';
  return text.length > length ? `${text.slice(0,length).trim()}…` : text;
}
function sourceLabel(story) { return esc((story.source || 'TwinTimes').replace('Google News · ','')); }
function markButton(story) {
  return `<button class="mark-button ${story.newsmarked?'marked':''}" data-mark="${esc(story.id)}" aria-label="${story.newsmarked?'Remove Newsmark':'Save Newsmark'}">${story.newsmarked?'★':'☆'}</button>`;
}
function bindCards(root=document) {
  $$('[data-mark]', root).forEach(button => button.addEventListener('click', async event => {
    event.preventDefault(); event.stopPropagation();
    const id = button.dataset.mark;
    try {
      const result = await post('/api/bookmark', {story_id:id});
      $$(`[data-mark="${CSS.escape(id)}"]`).forEach(node => { node.classList.toggle('marked', result.newsmarked); node.textContent=result.newsmarked?'★':'☆'; });
      toast(result.newsmarked ? 'Saved to Newsmarks' : 'Removed from Newsmarks');
      const count = await request('/api/bookmarks'); const counter=$('#markCount'); if(counter) counter.textContent=count.length;
      loadDiet();
    } catch(error) { toast(error.message); }
  }));
  $$('[data-story-link]', root).forEach(link => link.addEventListener('click', () => post('/api/engage',{story_id:link.dataset.storyLink, action:'open_article'}).then(loadDiet).catch(()=>{})));
}
function renderTop() {
  const grid=$('#topGrid');
  grid.innerHTML = digest.top.length ? digest.top.slice(0,8).map(story => `<article class="top-card"><div class="card-top"><span class="source">${sourceLabel(story)}</span>${markButton(story)}</div><h3>${esc(story.title)}</h3><p>${esc(excerpt(story))}</p><div class="card-foot"><a href="${esc(story.url)}" target="_blank" rel="noreferrer" data-story-link="${esc(story.id)}">Read original ↗</a><span class="score-pill">${Math.round(story.score)} signal</span></div></article>`).join('') : '<div class="empty">Refresh the feeds to build today’s briefing.</div>';
  bindCards(grid);
}
function renderSection(index=0) {
  const section=digest.sections[index]; const panel=$('#sectionPanel');
  if (!section) { panel.innerHTML='<div class="empty">No section stories yet.</div>'; return; }
  panel.innerHTML=section.items.map((story,i)=>`<article class="story-row"><span class="story-number">${String(i+1).padStart(2,'0')}</span><div><h3>${esc(story.title)}</h3><p>${sourceLabel(story)} · ${esc(story.why || excerpt(story,110))}</p></div><div class="row-actions">${markButton(story)}<a href="${esc(story.url)}" target="_blank" rel="noreferrer" data-story-link="${esc(story.id)}">Read ↗</a></div></article>`).join('');
  bindCards(panel);
}
function renderSections() {
  const tabs=$('#sectionTabs');
  tabs.innerHTML=digest.sections.map((section,i)=>`<button class="tab ${i===0?'active':''}" role="tab" data-index="${i}">${esc(section.name)}</button>`).join('');
  $$('.tab',tabs).forEach(tab=>tab.addEventListener('click',()=>{ $$('.tab',tabs).forEach(x=>x.classList.remove('active')); tab.classList.add('active'); renderSection(Number(tab.dataset.index)); }));
  renderSection(0);
}
function renderDeep() {
  const grid=$('#deepGrid');
  grid.innerHTML=digest.deep.length ? digest.deep.slice(0,6).map(story=>`<article class="deep-card"><span class="paper-type">${sourceLabel(story)} · Primary read</span><h3>${esc(story.title)}</h3><p>${esc(excerpt(story,190))}</p><a href="${esc(story.url)}" target="_blank" rel="noreferrer" data-story-link="${esc(story.id)}">Open research ↗</a></article>`).join('') : '<div class="empty">Research releases will appear after a refresh.</div>';
  bindCards(grid);
}
function bars(selector, data=[]) {
  const root=$(selector); if(!root) return;
  const max=Math.max(1,...data.map(item=>item[1]));
  root.innerHTML=data.length?data.slice(0,5).map(([label,value])=>`<div class="bar-row"><span title="${esc(label)}">${esc(label.replaceAll('_',' '))}</span><div class="bar"><i style="width:${Math.round(value/max*100)}%"></i></div><b>${value}</b></div>`).join(''):'<span class="source">Builds as you read</span>';
}
async function loadDiet(){ try{const d=await request('/api/diet'); const n=$('#dietTotal'); if(n)n.textContent=d.total; bars('#topicBars',d.topics); bars('#sourceBars',d.sources);}catch{} }
async function loadPodcasts(){
  const root=$('#podcastGrid'); if(!root)return;
  try{const items=await request('/api/podcasts'); root.innerHTML=items.map(item=>`<article class="podcast-card"><span class="podcast-icon">▶</span><h3>${esc(item.name)}</h3><p>${esc(item.note)}</p><a href="${esc(item.url)}" target="_blank" rel="noreferrer">Listen to the show ↗</a></article>`).join('');}catch{root.innerHTML='<div class="empty">Podcast recommendations are unavailable.</div>';}
}
function updateSignal(){
  const topics={}; digest.top.forEach(story=>(story.topics||[]).forEach(topic=>topics[topic]=(topics[topic]||0)+1));
  const leaders=Object.entries(topics).sort((a,b)=>b[1]-a[1]).slice(0,4).map(x=>x[0].replaceAll('_',' '));
  $('#signalTopics').textContent=leaders.length?leaders.join(' · '):'Your strongest themes will appear here.';
  $('#signalScore').textContent=digest.top.length?Math.round(digest.top.reduce((sum,x)=>sum+x.score,0)/digest.top.length):'—';
  $('#storyCount').textContent=digest.count||digest.top.length; $('#readTime').textContent=Math.max(1,Math.round((digest.count||digest.top.length)*1.2));
}
async function loadBriefing(){
  try{digest=await request('/api/digest'); renderTop(); renderSections(); renderDeep(); updateSignal(); const marks=await request('/api/bookmarks'); $('#markCount').textContent=marks.length; await loadDiet(); loadPodcasts();}
  catch(error){$('#status').textContent='Offline'; $('#topGrid').innerHTML=`<div class="empty"><strong>Local service needed</strong><br>${esc(error.message)}</div>`;}
}
async function refresh(){
  const button=$('#refresh'); button.disabled=true; button.textContent='Scanning…'; $('#status').innerHTML='<i></i> Updating';
  try{const result=await post('/api/refresh'); toast(`${result.inserted||0} new stories found`); $('#updated').textContent='Updated just now'; await loadBriefing();}
  catch(error){toast(error.message); $('#status').textContent='Refresh issue';}
  finally{button.disabled=false; button.textContent='Refresh'; $('#status').innerHTML='<i></i> Live';}
}
function today(value){ if(!value)return false; const d=new Date(value); const now=new Date(); return d.toDateString()===now.toDateString(); }
function renderMarks(filter='all'){
  const root=$('#marksList'); const shown=filter==='today'?bookmarks.filter(x=>today(x.newsmarked_at)):bookmarks;
  root.innerHTML=shown.length?shown.map(story=>`<article class="mark-row"><span class="mark-source">${sourceLabel(story)}</span><div><h2>${esc(story.title)}</h2><p>${esc(excerpt(story,180))}</p></div><div class="row-actions">${markButton({...story,newsmarked:true})}<a href="${esc(story.url)}" target="_blank" rel="noreferrer" data-story-link="${esc(story.id)}">Read ↗</a></div></article>`).join(''):'<div class="empty">No Newsmarks here yet. Save a story from today’s briefing and it will appear here.</div>';
  bindCards(root);
}
async function loadMarks(){try{bookmarks=await request('/api/bookmarks'); $('#markCount').textContent=bookmarks.length; renderMarks();}catch(error){$('#marksList').innerHTML=`<div class="empty">${esc(error.message)}</div>`;}}
function setupEmail(){
  const dialog=$('#emailDialog'); $('#openEmail').addEventListener('click',()=>dialog.showModal()); $('#closeEmail').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  $('#previewEmail').addEventListener('click',async()=>{const notice=$('#emailNotice'); notice.textContent='Building preview…'; try{const result=await post('/api/newsmarks/email',{to:$('#emailTo').value, preview:true}); notice.innerHTML=`<div class="email-preview">${esc(result.preview)}</div>`;}catch(error){notice.textContent=error.message;}});
  $('#emailForm').addEventListener('submit',async event=>{event.preventDefault(); const notice=$('#emailNotice'); notice.textContent='Sending…'; try{const result=await post('/api/newsmarks/email',{to:$('#emailTo').value}); notice.textContent=result.message; toast('Newsmarks sent'); setTimeout(()=>dialog.close(),900);}catch(error){notice.textContent=error.message;}});
}
const page=document.body.dataset.page;
if(page==='briefing'){
  const updatePacificTime=()=>{const now=new Date(); $('#date').textContent=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',weekday:'long',month:'long',day:'numeric'}).format(now); $('#ptTime').textContent=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',hour:'numeric',minute:'2-digit'}).format(now);};
  updatePacificTime(); setInterval(updatePacificTime,30000); $('#refresh').addEventListener('click',refresh); loadBriefing();
} else if(page==='newsmarks'){
  $$('.filter').forEach(button=>button.addEventListener('click',()=>{$$('.filter').forEach(x=>x.classList.remove('active'));button.classList.add('active');renderMarks(button.dataset.filter);})); loadMarks(); setupEmail();
}
