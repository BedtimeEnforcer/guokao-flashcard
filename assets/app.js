(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const STORAGE_KEY = 'zhixu-progress-v1';
  const LETTERS = ['A', 'B', 'C', 'D'];
  const DAY = 86400000;
  const data = {cards: [], comparisons: [], questions: []};
  let state = readState();
  let cardList = [], cardIndex = 0, revealed = false;
  let questionList = [], questionIndex = 0, answered = false, sessionAttempts = 0, sessionCorrect = 0;
  let currentView = 'today', toastTimer;

  function safe(text) {return String(text ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function safeUrl(url) {try {const parsed = new URL(url); return ['https:','http:'].includes(parsed.protocol) ? parsed.href : '#';} catch {return '#';}}
  function cleanState(raw) {
    const out = {version: 1, reviews: {}, bookmarks: {}, answers: {}};
    if (!raw || typeof raw !== 'object') return out;
    for (const key of ['reviews','bookmarks','answers']) if (raw[key] && typeof raw[key] === 'object' && !Array.isArray(raw[key])) out[key] = raw[key];
    return out;
  }
  function readState() {try {return cleanState(JSON.parse(localStorage.getItem(STORAGE_KEY)));} catch {return cleanState(null);}}
  function saveState() {try {localStorage.setItem(STORAGE_KEY, JSON.stringify(state));} catch {toast('浏览器存储不可用，请导出进度备份。');}}
  function toast(message) {const el = $('toast'); el.textContent = message; el.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 3100);}
  function dateText() {return new Intl.DateTimeFormat('zh-CN', {month:'long',day:'numeric',weekday:'long'}).format(new Date());}
  function reviewOf(id) {const r=state.reviews[id]; return r && typeof r === 'object' ? r : null;}
  function isDue(card) {const r=reviewOf(card.id); return !!r && Number(r.due) <= Date.now();}
  function totalAttempted() {return Object.values(state.answers).reduce((n,x)=>n+(Number(x?.attempts)||0),0);}
  function totalCorrect() {return Object.values(state.answers).reduce((n,x)=>n+(Number(x?.correct)||0),0);}
  function updateStats() {
    const learned=data.cards.filter(c=>reviewOf(c.id)).length;
    const due=data.cards.filter(isDue).length;
    const attempts=totalAttempted();
    $('stat-due').textContent=due;
    $('stat-learned').textContent=learned;
    $('stat-new').textContent=data.cards.length-learned;
    $('stat-accuracy').textContent=attempts ? Math.round(totalCorrect()/attempts*100)+'%' : '—';
    $('report-total').textContent=data.cards.length;
    $('report-learned').textContent=learned;
    $('report-saved').textContent=data.cards.filter(c=>state.bookmarks[c.id]).length;
    $('report-questions').textContent=attempts;
    $('progress-fill').style.width=data.cards.length ? Math.round(learned/data.cards.length*100)+'%' : '0%';
    $('report-summary').textContent=data.cards.length ? `共 ${data.cards.length} 张词卡，已学习 ${learned} 张，今天有 ${due} 张到期。` : '正式词卡尚未导入。导入后，这里会显示你的学习节奏。';
  }
  function showView(view) {
    if (!['today','cards','compare','quiz','progress'].includes(view)) view='today';
    currentView=view;
    document.querySelectorAll('.view').forEach(el=>el.classList.toggle('active',el.id==='view-'+view));
    document.querySelectorAll('[data-view]').forEach(el=>{const active=el.dataset.view===view; el.classList.toggle('active',active); if(el.classList.contains('nav-item')) active ? el.setAttribute('aria-current','page') : el.removeAttribute('aria-current');});
    if(view==='cards') applyCardFilter();
    if(view==='compare') renderComparisons();
    if(view==='quiz') renderQuestion();
    if(view==='progress'||view==='today') updateStats();
    if(location.hash.slice(1)!==view) history.replaceState(null,'','#'+view);
    window.scrollTo({top:0,behavior:'smooth'});
  }
  function cardMatches(card,query) {return [card.term,card.definition,card.usage,card.topic,...(card.tags||[]),...(card.collocations||[])].some(value=>String(value||'').toLowerCase().includes(query));}
  function applyCardFilter(preferredId) {
    const query=$('card-search').value.trim().toLowerCase();
    const kind=$('card-kind').value, mode=$('card-filter').value, topic=$('card-topic').value;
    cardList=data.cards.filter(card=>(kind==='all'||card.kind===kind)&&(topic==='all'||card.topic===topic)&&(!query||cardMatches(card,query))&&(mode==='all'||(mode==='due'&&isDue(card))||(mode==='new'&&!reviewOf(card.id))||(mode==='saved'&&state.bookmarks[card.id])));
    const preferred=cardList.findIndex(c=>c.id===preferredId);
    cardIndex=preferred>=0 ? preferred : Math.min(cardIndex,Math.max(0,cardList.length-1));
    revealed=false; renderCard();
  }
  function sourceHtml(source) {
    if(!source) return '';
    const label=safe(source.title)+(source.locator?' · '+safe(source.locator):'');
    return `<div class="card-source">词义参考：<a href="${safe(safeUrl(source.url))}" target="_blank" rel="noopener noreferrer">${label} ↗</a></div>`;
  }
  function field(label,value) {return value ? `<div class="card-section"><h3>${label}</h3><p>${safe(value)}</p></div>` : '';}
  function renderCard() {
    const card=cardList[cardIndex];
    const area=$('flashcard'), content=$('flashcard-content');
    $('card-position').textContent=card ? `${cardIndex+1} / ${cardList.length}` : `0 / ${cardList.length}`;
    $('card-kind-label').textContent=card ? (card.kind==='idiom'?'成语':'实词') : '词语卡';
    $('prev-card').disabled=!card||cardIndex===0;
    $('next-card').disabled=!card||cardIndex>=cardList.length-1;
    $('reveal-card').disabled=!card;
    $('card-feedback').hidden=!card||!revealed;
    $('reveal-card').textContent=revealed?'收起解析':'显示解析';
    area.classList.toggle('empty',!card);
    if(!card) {area.setAttribute('aria-label','没有符合条件的词卡'); content.innerHTML=`<div class="empty-state"><strong>${data.cards.length?'这里暂时没有词卡':'正式词卡正在准备中'}</strong><p>${data.cards.length?'调整筛选条件，或稍后再来复习。':'内容文件通过校验并发布后，会自动出现在这里。'}</p></div>`;return;}
    area.setAttribute('aria-label',revealed?'收起解析':'显示词语解析');
    const tags=(card.tags||[]).slice(0,5).map(t=>`<span class="tag">${safe(t)}</span>`).join('');
    content.innerHTML=`<div class="card-kicker">${card.kind==='idiom'?'IDIOM · 成语':'WORD · 实词'} · 难度 ${safe(card.difficulty||2)}</div><button class="bookmark-button ${state.bookmarks[card.id]?'saved':''}" data-bookmark="${safe(card.id)}" aria-label="${state.bookmarks[card.id]?'取消收藏':'收藏词卡'}">${state.bookmarks[card.id]?'★ 已收藏':'☆ 收藏'}</button><div class="word-heading">${safe(card.term)}</div>${revealed?`${field('准确释义',card.definition)}${field('适用语境',card.usage)}${field('常见搭配',(card.collocations||[]).join(' · '))}${field('与易混词的区别',card.distinction)}${field('正确例句',card.example)}${field('常见误用',card.misuse)}${field('误用原因',card.misuse_reason)}<div class="tag-list">${tags}</div>${sourceHtml(card.source)}`:`<p class="card-prompt">先不看答案：你能说出它的核心意思、适用对象和一个恰当语境吗？<br>想好后点击卡片，或使用下方按钮揭晓。</p><div class="tag-list">${tags}</div>`}`;
  }
  function rateCard(rating) {
    const card=cardList[cardIndex]; if(!card||!revealed) return;
    const previous=reviewOf(card.id); const stage=rating==='again'?0:rating==='hard'?Math.max(1,previous?.stage||0):Math.min(6,(previous?.stage||0)+1);
    const interval=rating==='again'?10*60000:rating==='hard'?DAY:[0,DAY,3*DAY,7*DAY,14*DAY,30*DAY,60*DAY][stage];
    state.reviews[card.id]={stage,due:Date.now()+interval,last:Date.now(),count:(previous?.count||0)+1};
    saveState(); updateStats();
    const nextId=cardList[cardIndex+1]?.id;
    applyCardFilter(nextId);
    toast(rating==='again'?'已安排稍后重看':rating==='hard'?'已安排明天复习':'已记录，复习间隔已延长');
  }
  function renderComparisons() {
    const query=$('compare-search').value.trim().toLowerCase();
    const list=data.comparisons.filter(item=>[...(item.terms||[]),item.shared,item.difference,...(item.tags||[])].some(x=>String(x||'').toLowerCase().includes(query)));
    $('compare-count').textContent=`${list.length} 组`;
    $('comparison-grid').innerHTML=list.length ? list.map(item=>`<article class="comparison-card"><h2>${(item.terms||[]).map(safe).join('<span>vs</span>')}</h2><div class="compare-lead">共同点：${safe(item.shared)}</div><div class="divider"></div><strong>判断关键</strong><p>${safe(item.difference)}</p>${(item.examples||[]).map(ex=>`<div class="card-section"><strong>${safe(ex.term)}</strong><p>${safe(ex.sentence)}</p></div>`).join('')}${sourceHtml(item.source)}</article>`).join('') : `<div class="empty-state"><strong>${data.comparisons.length?'没有找到对应辨析':'辨析内容正在准备中'}</strong><p>${data.comparisons.length?'试试其他词语。':'正式辨析通过校验后，会在这里展示。'}</p></div>`;
  }
  function renderQuestion() {
    const q=questionList[questionIndex]; answered=false;
    $('quiz-explanation').hidden=true; $('quiz-next').hidden=true; $('quiz-skip').hidden=!q;
    $('quiz-number').textContent=q?`题目 ${questionIndex+1} / ${questionList.length}`:'题目 — / —';
    $('quiz-difficulty').textContent=q?'原创语境题':'';
    $('quiz-stem').textContent=q?q.stem:'语境练习正在准备中';
    $('quiz-choices').innerHTML=q?q.choices.map((choice,i)=>`<button class="choice" data-choice="${i}"><span class="choice-letter">${LETTERS[i]}</span>${safe(choice)}</button>`).join(''):'<div class="empty-state"><p>题目文件通过校验并发布后，这里会出现完整的四选一练习。</p></div>';
    $('session-correct').textContent=`${sessionCorrect} / ${sessionAttempts}`;
  }
  function selectChoice(index) {
    const q=questionList[questionIndex]; if(!q||answered) return;
    answered=true;sessionAttempts++; if(index===q.answer)sessionCorrect++;
    const record=state.answers[q.id]||{attempts:0,correct:0};record.attempts++;if(index===q.answer)record.correct++;state.answers[q.id]=record;saveState();updateStats();
    document.querySelectorAll('.choice').forEach((el,i)=>{el.disabled=true;if(i===q.answer)el.classList.add('correct');else if(i===index)el.classList.add('wrong');});
    const details=(q.choice_explanations||[]).map((x,i)=>`<li><strong>${LETTERS[i]}.</strong> ${safe(x)}</li>`).join('');
    const related=(q.tested_terms||[]).slice(0,6).map(term=>`<button class="related-term" data-lookup="${safe(term)}">${safe(term)} ↗</button>`).join('');
    $('quiz-explanation').innerHTML=`<strong>${index===q.answer?'答对了':'这题需要再辨析'} · 正确答案 ${LETTERS[q.answer]} ${safe(q.choices[q.answer])}</strong><p>${safe(q.explanation)}</p>${details?`<ul>${details}</ul>`:''}${related?`<div class="related-list"><span>回看词卡</span>${related}</div>`:''}${sourceHtml(q.source)}`;
    $('quiz-explanation').hidden=false;$('quiz-next').hidden=false;$('quiz-skip').hidden=true;
    $('session-correct').textContent=`${sessionCorrect} / ${sessionAttempts}`;
  }
  function nextQuestion() {if(!questionList.length)return;questionIndex=(questionIndex+1)%questionList.length;renderQuestion();}
  function validateRow(type,x) {
    if(!x||typeof x!=='object'||!x.id)return false;
    if(type==='cards')return !!x.source?.url&&safeUrl(x.source.url).startsWith('http')&&typeof x.term==='string'&&['idiom','word'].includes(x.kind)&&typeof x.definition==='string'&&typeof x.usage==='string'&&typeof x.example==='string';
    if(type==='comparisons')return Array.isArray(x.terms)&&x.terms.length>=2&&typeof x.shared==='string'&&typeof x.difference==='string';
    return typeof x.stem==='string'&&Array.isArray(x.choices)&&x.choices.length===4&&new Set(x.choices).size===4&&Number.isInteger(x.answer)&&x.answer>=0&&x.answer<4&&typeof x.explanation==='string'&&Array.isArray(x.choice_explanations)&&[0,4].includes(x.choice_explanations.length);
  }
  function parseJsonl(text,type) {
    const rows=[];const ids=new Set();
    for(const [i,line] of text.split(/\r?\n/).entries()) {if(!line.trim())continue;let row;try{row=JSON.parse(line);}catch{throw Error(`${type} 第 ${i+1} 行不是有效 JSON`);}if(!validateRow(type,row))throw Error(`${type} 第 ${i+1} 行字段不完整`);if(ids.has(row.id))throw Error(`${type} 有重复 ID：${row.id}`);ids.add(row.id);rows.push(row);}
    return rows;
  }
  function checkRelations(next) {
    const terms=new Set(next.cards.map(x=>x.term));
    for(const q of next.questions)for(const t of q.tested_terms||[])if(!terms.has(t))throw Error(`题目「${q.id}」引用了未收录词语：${t}`);
  }
  function installContent(next) {checkRelations(next);Object.assign(data,next);questionList=[...data.questions];cardIndex=questionIndex=0;const topics=[...new Set(data.cards.map(x=>x.topic).filter(Boolean))];const select=$('card-topic');select.innerHTML='<option value="all">全部主题</option>'+topics.map(topic=>`<option value="${safe(topic)}">${safe(topic)}</option>`).join('');if($('card-filter').value==='due'&&!data.cards.some(isDue))$('card-filter').value='new';applyCardFilter();renderComparisons();renderQuestion();updateStats();}
  async function loadContent() {
    const files=[['cards','data/cards.jsonl'],['comparisons','data/comparisons.jsonl'],['questions','data/questions.jsonl']];
    const next={cards:[],comparisons:[],questions:[]};
    try {for(const [type,url] of files) {const response=await fetch(url,{cache:'no-cache'});if(!response.ok)throw Error(`内容文件无法读取：${url}`);next[type]=parseJsonl(await response.text(),type);}installContent(next);$('data-status').textContent=`已加载 ${data.cards.length} 张词卡、${data.comparisons.length} 组辨析、${data.questions.length} 道题。`;} catch(error) {console.error(error);$('data-status').textContent=`内容未加载：${error.message}`;toast('内容文件未通过校验，网站暂时显示空状态。');}
  }
  function download(name,content) {const a=document.createElement('a');const url=URL.createObjectURL(new Blob([content],{type:'application/json;charset=utf-8'}));a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function exportProgress() {download(`zhixu-progress-${new Date().toISOString().slice(0,10)}.json`,JSON.stringify(state,null,2));toast('进度已导出。');}
  function openSettings() {$('settings-dialog').showModal();}
  document.addEventListener('click',event=>{
    const nav=event.target.closest('[data-view]');if(nav){showView(nav.dataset.view);return;}
    const lookup=event.target.closest('[data-lookup]');if(lookup){$('card-search').value=lookup.dataset.lookup;$('card-topic').value='all';$('card-kind').value='all';$('card-filter').value='all';cardIndex=0;showView('cards');return;}
    const bookmark=event.target.closest('[data-bookmark]');if(bookmark){const id=bookmark.dataset.bookmark;state.bookmarks[id]?delete state.bookmarks[id]:state.bookmarks[id]=true;saveState();if($('card-filter').value==='saved')applyCardFilter();else renderCard();updateStats();return;}
    const rating=event.target.closest('[data-rating]');if(rating){rateCard(rating.dataset.rating);return;}
    const choice=event.target.closest('[data-choice]');if(choice){selectChoice(Number(choice.dataset.choice));return;}
  });
  $('flashcard').addEventListener('click',event=>{if(event.target.closest('button,a'))return;if(cardList.length){revealed=!revealed;renderCard();}});
  $('flashcard').addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&!event.target.closest('button,a')){event.preventDefault();if(cardList.length){revealed=!revealed;renderCard();}}});
  $('reveal-card').addEventListener('click',()=>{if(cardList.length){revealed=!revealed;renderCard();}});
  $('prev-card').addEventListener('click',()=>{if(cardIndex>0){cardIndex--;revealed=false;renderCard();}});
  $('next-card').addEventListener('click',()=>{if(cardIndex<cardList.length-1){cardIndex++;revealed=false;renderCard();}});
  ['card-search','card-topic','card-kind','card-filter'].forEach(id=>$(id).addEventListener(id==='card-search'?'input':'change',()=>{cardIndex=0;applyCardFilter();}));
  $('compare-search').addEventListener('input',renderComparisons);
  $('quiz-skip').addEventListener('click',nextQuestion);$('quiz-next').addEventListener('click',nextQuestion);
  $('start-study').addEventListener('click',()=>{if(data.cards.some(isDue))$('card-filter').value='due';else $('card-filter').value='new';showView('cards');});
  ['open-settings','top-settings'].forEach(id=>$(id).addEventListener('click',openSettings));
  ['export-progress','report-export'].forEach(id=>$(id).addEventListener('click',exportProgress));
  $('import-progress').addEventListener('click',()=>$('progress-file').click());
  $('progress-file').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{const raw=JSON.parse(await file.text());if(!raw||raw.version!==1||typeof raw.reviews!=='object'||typeof raw.answers!=='object')throw Error('进度文件格式不符合本网站要求');state=cleanState(raw);saveState();applyCardFilter();updateStats();toast('进度导入成功。');}catch(error){toast(error.message);}event.target.value='';});
  $('import-content').addEventListener('click',()=>$('content-files').click());
  $('content-files').addEventListener('change',async event=>{const files=[...event.target.files];if(!files.length)return;const next={cards:[],comparisons:[],questions:[]};try{for(const file of files){const type=file.name.split('.')[0];if(!(type in next))throw Error(`文件名必须为 cards、comparisons 或 questions：${file.name}`);next[type]=parseJsonl(await file.text(),type);}installContent(next);$('data-status').textContent=`本机预览：${next.cards.length} 张词卡、${next.comparisons.length} 组辨析、${next.questions.length} 道题。刷新后恢复公开内容。`;toast('内容文件已在本机预览。');$('settings-dialog').close();}catch(error){toast(error.message);}event.target.value='';});
  $('reset-progress').addEventListener('click',()=>{if(!confirm('确定清空当前浏览器的全部学习进度吗？建议先导出备份。'))return;state=cleanState(null);saveState();applyCardFilter();updateStats();toast('本机进度已清空。');});
  $('show-content-info').addEventListener('click',()=>$('info-dialog').showModal());
  window.addEventListener('hashchange',()=>showView(location.hash.slice(1)));
  $('today-date').textContent=dateText();updateStats();loadContent();showView(location.hash.slice(1)||'today');
  if('serviceWorker' in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));
})();

