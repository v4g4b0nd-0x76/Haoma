(function(){
var D=document.documentElement,Q=function(s,r){return[].slice.call((r||document).querySelectorAll(s))},H=window.haoma||{},fixed=D.hasAttribute('data-fixed')?D.dataset.culture:null;
var P=(H.getPrefs&&H.getPrefs())||{};
function allowed(){return H.allowed?H.allowed():false}
function save(){if(H.setPrefs)H.setPrefs(P)}
function rememberCulture(p){if(H.setCulture)H.setCulture(p)}
function rememberPlace(){
 if(!allowed()||!H.setLast)return;
 var path=(location.pathname||'/').replace(/\/+/g,'/')||'/';
 /* skip language homes so "continue where you left off" still has a deeper page */
 if(path==='/'||path==='/fa'||path==='/fa/'||/^\/(en\/?)?$/.test(path))return;
 H.setLast(path);
}
var act={
 nav:function(){P.nav=D.dataset.nav==='hidden'?'shown':'hidden';D.dataset.nav=P.nav;if(P.nav==='shown'){P.focus=false;D.dataset.focus='0'}},
 dock:function(){P.dock=D.dataset.dock==='end'?'start':'end';D.dataset.dock=P.dock},
 minus:function(){size(-.1)},plus:function(){size(.1)},
 focus:function(){P.focus=D.dataset.focus!=='1';D.dataset.focus=P.focus?'1':'0'},
 /* PDF export = the browser's own print dialog: nothing leaves the page, and the
    print block in style.css keeps the theme. Safari and older FDMs print on the
    first call, so no re-entrancy guard is needed here. */
 pdf:function(){var go=function(){window.print()};window.haomaPrintPrep?window.haomaPrintPrep().then(go,go):go()}};
function size(d){P.size=Math.min(1.7,Math.max(1,Math.round(((P.size||1.2)+d)*100)/100));D.style.setProperty('--read',P.size+'rem')}
var hasSide=!!document.querySelector('aside.side');
Q('[data-act]').forEach(function(b){if(!hasSide&&/nav|dock/.test(b.dataset.act))b.hidden=true;b.onclick=function(){var fn=act[b.dataset.act];if(typeof fn==='function'){fn();save()}}});
/* culture pick: a listbox, so an option can be tinted with its own colour on hover */
var pick=document.getElementById('culture-pick'),btn=document.getElementById('cpick-btn'),
    list=document.getElementById('cpick-list'),cine=Q('.cine')[0];
function opt(v){return pick&&pick.querySelector('[data-pick="'+v+'"]')}
/* mirror the choice onto the trigger -- label, sigil colour and motif, and the
   option itself. The page theme follows via data-culture on <html>. */
function paintPick(eff){
 var o=opt(eff);if(!o||!pick||!btn)return;
 pick.style.setProperty('--c',o.style.getPropertyValue('--c').trim()||'#9aa3b5');
 pick.style.setProperty('--pat',o.style.getPropertyValue('--pat').trim()||'var(--m-none)');
 var n=btn.querySelector('.cpick__name');if(n)n.textContent=o.dataset.name||'';
 Q('.cpick__opt',pick).forEach(function(x){x.setAttribute('aria-selected',x===o)});
}
function pill(v){return cine&&cine.querySelector('.pills [data-pick="'+v+'"]')}
function hrefFor(p){var pb=pill(p),o=opt(p);return(pb&&pb.dataset.href)||(o&&o.dataset.href)||''}
/* Homepage: filter Latest / Explore / Media cards to the picked culture.
   "All cultures" (base) shows every card. */
function filterHomeCards(p){
 if(!cine)return;
 Q('[data-home-cards] .card').forEach(function(c){
  var dc=c.getAttribute('data-culture')||'';
  c.hidden=!(p==='base'||!dc||dc===p||dc==='base');
 });
 Q('[data-home-cards] .tabpanel, [data-home-cards].slider').forEach(function(box){
  var empty=box.querySelector('[data-home-empty]');
  if(!empty)return;
  var cards=Q('.card',box),vis=cards.filter(function(c){return!c.hidden});
  empty.hidden=!cards.length||vis.length>0;
 });
}
function setPick(p,first){
 rememberCulture(p);
 var eff=fixed||p;D.dataset.pick=p;if(!fixed)D.dataset.culture=p;
 paintPick(eff);
 Q('.cine .pills button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.pick===p)});
 /* Hero pills only retint the page (theme + banner + quote). Never navigate. */
 if(cine){var sl=Q('.slide',cine),on=sl.filter(function(s){return s.dataset.culture===p})[0]||sl[0],q=Q('.quote',cine)[0],en=Q('.enter',cine)[0];
  cine.dataset.culture=p;sl.forEach(function(s){s.classList.toggle('on',s===on)});
  if(q&&on){var tpl=on.querySelector('template'),put=function(){if(tpl)q.innerHTML=tpl.innerHTML;q.style.opacity=1};
  if(first)put();else{q.style.opacity=0;setTimeout(put,250)}}
  if(en){var href=hrefFor(p);
   en.hidden=p==='base';en.setAttribute('aria-hidden',p==='base'?'true':'false');
   /* keep a real href even when hidden — crawlers reject <a> without href */
   if(p==='base'||!href){en.href=hrefFor('base')||en.getAttribute('href')||'/cultures/';en.setAttribute('tabindex','-1')}
   else{en.href=href;en.removeAttribute('tabindex')}}
  filterHomeCards(p)}
}
/* Navigate to a culture (or cultures index for base). */
function pickGo(p){var href=hrefFor(p);if(!href)return;rememberCulture(p);location.href=href}
/* open, close and keyboard: a listbox, not a select */
function openPick(open){
 if(!btn||!list)return;
 btn.setAttribute('aria-expanded',open?'true':'false');list.hidden=!open;
 if(open){var c=pick.querySelector('.cpick__opt[aria-selected=true]')||list.querySelector('.cpick__opt');if(c)c.focus()}
}
if(btn&&list){
 btn.onclick=function(){openPick(btn.getAttribute('aria-expanded')!=='true')};
 var items=Q('.cpick__opt',list);
 items.forEach(function(o){o.tabIndex=-1;o.onclick=function(){pickGo(o.dataset.pick)}});
 list.onkeydown=function(e){
  var i=items.indexOf(document.activeElement);
  if(e.key==='Escape'){e.preventDefault();openPick(false);btn.focus();return}
  if(e.key==='Tab'){openPick(false);return}
  if(e.key==='ArrowDown'||e.key==='ArrowUp'){
   var d=e.key==='ArrowDown'?1:items.length-1;
   e.preventDefault();items[i<0?(d===1?0:items.length-1):(i+d)%items.length].focus();return}
  if(e.key==='Home'){e.preventDefault();items[0].focus();return}
  if(e.key==='End'){e.preventDefault();items[items.length-1].focus();return}
  if(e.key==='Enter'||e.key===' '){var cur=document.activeElement;if(cur&&cur.dataset&&cur.dataset.pick){e.preventDefault();pickGo(cur.dataset.pick)}}};
 btn.onkeydown=function(e){
  if(e.key==='ArrowDown'||e.key==='Enter'||e.key===' '){e.preventDefault();openPick(true)}
  else if(e.key==='Escape'){openPick(false)}};
 document.addEventListener('click',function(e){
  if(btn.getAttribute('aria-expanded')==='true'&&pick&&!pick.contains(e.target))openPick(false)});
}
/* Hero culture chips:
   - single click → preview only (banner + theme + quote)
   - double-click → open that culture's index
   - "Enter this world" link → open the selected culture */
if(cine){
 var pillsRoot=cine.querySelector('.pills');
 var enterBtn=cine.querySelector('.enter');
 if(pillsRoot){
  pillsRoot.addEventListener('click',function(e){
   var b=e.target.closest('[data-pick]');
   if(!b||!pillsRoot.contains(b))return;
   e.preventDefault();e.stopPropagation();
   if(typeof e.stopImmediatePropagation==='function')e.stopImmediatePropagation();
   setPick(b.dataset.pick);
  },true);
  pillsRoot.addEventListener('dblclick',function(e){
   var b=e.target.closest('[data-pick]');
   if(!b||!pillsRoot.contains(b))return;
   e.preventDefault();e.stopPropagation();
   if(b.dataset.pick==='base')return; /* All cultures stays a preview; use Enter */
   pickGo(b.dataset.pick);
  },true);
 }
 if(enterBtn){
  enterBtn.addEventListener('click',function(e){
   e.preventDefault();
   pickGo(D.dataset.pick||'base');
  });
 }
}
var p0=(H.getCulture&&H.getCulture())||D.dataset.pick||'base';
if(!pill(p0)&&!opt(p0)&&p0!=='base')p0='base';
setPick(p0,true);
rememberPlace();
/* slider */
Q('.slider').forEach(function(s){var r=s.querySelector('.rail'),rtl=getComputedStyle(r).direction==='rtl';
 Q('[data-dir]',s).forEach(function(b){b.onclick=function(){r.scrollBy({left:(+b.dataset.dir)*(rtl?-1:1)*r.clientWidth*.8,behavior:'smooth'})}})});
/* tabs — only real panel tabs (aria-controls). Theme/filter chip groups also use
   role=tablist but must keep their own handlers; never overwrite those. */
Q('[role=tablist]').forEach(function(l){
  var bs=Q('button',l).filter(function(b){return b.getAttribute('aria-controls')});
  if(!bs.length)return;
  bs.forEach(function(x){x.addEventListener('click',function(){
    bs.forEach(function(y){
      var on=y===x,panel=document.getElementById(y.getAttribute('aria-controls'));
      y.setAttribute('aria-selected',on?'true':'false');
      if(panel)panel.hidden=!on;
    });
  })});
});

/* Simple keyboard actions for non-tech readers */
function typingInField(el){
  if(!el)return false;
  var tag=(el.tagName||'').toLowerCase();
  return tag==='input'||tag==='textarea'||tag==='select'||el.isContentEditable;
}
function openKeysHelp(on){
  var box=document.getElementById('keys-help');
  if(!box)return;
  box.hidden=!on;
  if(on){var ok=document.getElementById('keys-help-ok');if(ok)ok.focus()}
}
var keysBtn=document.getElementById('keys-help-btn');
var keysOk=document.getElementById('keys-help-ok');
if(keysBtn)keysBtn.onclick=function(){openKeysHelp(true)};
if(keysOk)keysOk.onclick=function(){openKeysHelp(false);keysBtn&&keysBtn.focus()};
var keysBox=document.getElementById('keys-help');
if(keysBox)keysBox.addEventListener('click',function(e){if(e.target===keysBox)openKeysHelp(false)});

var cardFocus=-1;
function cardList(){return Q('.cards .card a, .cards a.card').filter(function(a){return a.offsetParent!==null})}
function focusCard(d){
  var list=cardList();if(!list.length)return;
  cardFocus=Math.max(0,Math.min(list.length-1,cardFocus<0?(d>0?0:list.length-1):cardFocus+d));
  list[cardFocus].focus();
  try{list[cardFocus].scrollIntoView({block:'nearest',behavior:'smooth'})}catch(e){list[cardFocus].scrollIntoView(true)}
}
document.addEventListener('keydown',function(e){
  if(typingInField(e.target))return;
  if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!e.altKey){
    e.preventDefault();
    if(window.haomaSearchOpen)window.haomaSearchOpen();
    return;
  }
  if(e.key==='?'||(e.key==='/'&&e.shiftKey)){
    e.preventDefault();openKeysHelp(true);return;
  }
  if(e.key==='Escape'){
    openKeysHelp(false);
    if(window.haomaSearchClose)window.haomaSearchClose();
    return;
  }
  if(e.key==='j'||e.key==='J'){e.preventDefault();focusCard(1);return}
  if(e.key==='k'||e.key==='K'){e.preventDefault();focusCard(-1);return}
});

/* Reading progress on long articles */
var bar=document.getElementById('read-progress');
var art=document.querySelector('main article');
if(bar&&art){
  function prog(){
    var r=art.getBoundingClientRect(),vh=window.innerHeight||1;
    var total=art.offsetHeight-vh;
    var done=total>40?Math.min(1,Math.max(0,(-r.top)/total)):0;
    bar.style.transform='scaleX('+done+')';
    bar.classList.toggle('is-on',total>40);
  }
  window.addEventListener('scroll',prog,{passive:true});
  window.addEventListener('resize',prog);
  prog();
}

/* ----- cookie consent (themed by current data-culture) + resume ----- */
(function cookieUI(){
  var banner=document.getElementById('cookie-banner');
  var resume=document.getElementById('resume-bar');
  var link=document.getElementById('resume-link');
  var dismiss=document.getElementById('resume-dismiss');
  function isHome(){
    var p=(location.pathname||'/').replace(/\/+/g,'/');
    return p==='/'||p==='/fa'||p==='/fa/'||/^\/(en\/?)?$/.test(p);
  }
  function syncCookieH(){
    if(!banner||banner.hidden){D.style.removeProperty('--cookie-h');return}
    D.style.setProperty('--cookie-h',Math.ceil(banner.getBoundingClientRect().height)+'px');
  }
  function syncResumeH(){
    if(!resume||resume.hidden){D.style.removeProperty('--resume-h');return}
    D.style.setProperty('--resume-h',Math.ceil(resume.getBoundingClientRect().height)+'px');
  }
  function showBanner(on){
    if(!banner)return;
    banner.hidden=!on;
    document.body.classList.toggle('has-cookie',!!on);
    requestAnimationFrame(syncCookieH);
  }
  function showResume(){
    if(!resume||!link||!allowed()||!H.getLast)return;
    var last=H.getLast();
    if(!last||last===location.pathname){resume.hidden=true;syncResumeH();return}
    /* home always; standalone also (study.js may enrich copy) */
    var standalone=false;
    try{standalone=matchMedia('(display-mode: standalone)').matches||!!(navigator.standalone)}catch(e){}
    if(!isHome()&&!standalone){resume.hidden=true;syncResumeH();return}
    link.href=last;
    var tCont=D.getAttribute('data-study-continue');
    var tGo=D.getAttribute('data-study-continue-go');
    var text=resume.querySelector('.resume__text');
    if(tCont&&text)text.textContent=tCont;
    if(tGo)link.textContent=tGo;
    resume.hidden=false;
    requestAnimationFrame(syncResumeH);
  }
  function afterAllow(){
    rememberCulture(D.dataset.pick||'base');
    save();
    rememberPlace();
    showResume();
  }
  if(banner){
    if(!H.consent||!H.consent())showBanner(true);
    banner.querySelectorAll('[data-cookie]').forEach(function(b){
      b.addEventListener('click',function(){
        var allow=b.getAttribute('data-cookie')==='allow';
        if(H.setConsent)H.setConsent(allow);
        showBanner(false);
        if(allow)afterAllow();
        else if(resume)resume.hidden=true;
      });
    });
  }
  Q('[data-cookie-settings]').forEach(function(b){
    b.addEventListener('click',function(){showBanner(true)});
  });
  if(dismiss)dismiss.addEventListener('click',function(){
    if(resume)resume.hidden=true;
    syncResumeH();
    try{sessionStorage.setItem('haoma-resume-hide','1')}catch(e){}
  });
  try{if(sessionStorage.getItem('haoma-resume-hide')==='1'&&resume){resume.hidden=true;syncResumeH()}
  else showResume()}catch(e){showResume()}
  if(banner&&typeof ResizeObserver!=='undefined')new ResizeObserver(syncCookieH).observe(banner);
  if(resume&&typeof ResizeObserver!=='undefined')new ResizeObserver(syncResumeH).observe(resume);
  window.addEventListener('resize',function(){syncCookieH();syncResumeH()});
  syncCookieH();
  syncResumeH();
})();

/* sticky header / listen chrome: keep sticky rails + fixed resume clear of the bar */
(function chromeOffsets(){
  var top=document.querySelector('header.top');
  var listen=document.querySelector('.listen');
  function set(){
    if(top)D.style.setProperty('--top-h',Math.ceil(top.getBoundingClientRect().height)+'px');
    if(listen&&!listen.hidden)D.style.setProperty('--listen-h',Math.ceil(listen.getBoundingClientRect().height)+'px');
    else D.style.removeProperty('--listen-h');
  }
  set();
  window.addEventListener('resize',set,{passive:true});
  if(typeof ResizeObserver!=='undefined'){
    if(top)new ResizeObserver(set).observe(top);
    if(listen)new ResizeObserver(set).observe(listen);
  }
})();
})();
/* ===== v4: sliders, play-on-scroll media, notes ===== */
(function(){
var Q=function(s,r){return[].slice.call((r||document).querySelectorAll(s))},reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;
var PH='data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';
Q('.slider-md').forEach(function(s){var tr=s.querySelector('.sm-track'),sl=Q('.sm-slide',s),dots=s.querySelector('.sm-dots'),i=0,bs=[];
 function mark(){bs.forEach(function(b,k){b.className=k===i?'on':''})}
 function go(k){i=(k+sl.length)%sl.length;tr.scrollTo({left:i*tr.clientWidth*(getComputedStyle(tr).direction==='rtl'?-1:1),behavior:reduced?'auto':'smooth'});mark()}
 sl.forEach(function(_,k){var b=document.createElement('button');b.type='button';b.setAttribute('aria-label','Slide '+(k+1));b.onclick=function(){go(k)};dots.appendChild(b);bs.push(b)});
 s.querySelector('.sm-prev').onclick=function(){go(i-1)};s.querySelector('.sm-next').onclick=function(){go(i+1)};
 tr.addEventListener('scroll',function(){var n=Math.round(Math.abs(tr.scrollLeft)/Math.max(1,tr.clientWidth));if(n!==i&&n<sl.length){i=n;mark()}});
 var a=+s.dataset.auto;if(a>0&&!reduced)setInterval(function(){if(!s.matches(':hover'))go(i+1)},a*1000);mark()});
var media=Q('[data-gif],video[data-scroll]');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){var m=e.target,r=e.intersectionRatio,isIn=e.isIntersecting;
 if(m.dataset.gif){/* hysteresis: start at 60% visible, but only stop once fully out —
    stopping/restarting on every scroll jitter at the threshold made GIFs flicker */
  var was=!!m.dataset.on,on=was?(isIn&&r>0.08):(isIn&&r>=.6);
  if(on&&!was){m.src=m.dataset.gif;m.dataset.on='1'}else if(!on&&was){m.src=PH;m.dataset.on=''}}
 else if(isIn&&r>=.6){var p=m.play();if(p&&p.catch)p.catch(function(){})}else if(!isIn)m.pause()})},{threshold:[0,.08,.6,1]});media.forEach(function(m){io.observe(m)})}
else media.forEach(function(m){if(m.dataset.gif)m.src=m.dataset.gif});
Q('.note').forEach(function(n){var p=n.querySelector('.note-pop');function fit(){p.style.setProperty('--nx','0px');var r=p.getBoundingClientRect(),w=document.documentElement.clientWidth,dx=0;if(r.left<8)dx=8-r.left;else if(r.right>w-8)dx=w-8-r.right;p.style.setProperty('--nx',dx+'px')}n.addEventListener('mouseenter',fit);n.addEventListener('focusin',fit)});
 /* PDF/print. A browser snapshots the page the moment print starts and never
    waits for an image that only begins loading then, so anything print needs
    has to be decoded beforehand: the PDF button awaits haomaPrintPrep(), and a
    GIF that has played once already carries its still. The still is the first
    frame painted to a canvas (drawImage uses the default frame of an animated
    image), sitting next to the live GIF as a print-only img. */
 function gifStill(m){if(m.dataset.still)return Promise.resolve();
  return new Promise(function(ok){var im=new Image();im.onload=function(){try{
    var c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;
    c.getContext('2d').drawImage(im,0,0);var s=document.createElement('img');
    s.className='gif-still';s.alt='';s.setAttribute('aria-hidden','true');s.src=c.toDataURL('image/png');
    m.dataset.still='1';m.insertAdjacentElement('afterend',s);
    if(s.decode)s.decode().then(ok,ok);else ok()}catch(e){ok()}};im.onerror=function(){ok()};im.src=m.dataset.gif})}
 Q('[data-gif]').forEach(function(m){m.addEventListener('load',function(){if(m.dataset.on)gifStill(m)})});
 function ready(m){return m.complete?Promise.resolve():new Promise(function(ok){m.addEventListener('load',ok,{once:true});m.addEventListener('error',ok,{once:true})})}
 window.haomaPrintPrep=function(){
  var lazy=Q('img[loading=lazy]');lazy.forEach(function(m){m.loading='eager'});
  var w=lazy.map(ready).concat(Q('[data-gif]').map(gifStill));
  Q('video[preload=metadata]').forEach(function(v){v.preload='auto'});
  return Promise.race([Promise.all(w),new Promise(function(ok){setTimeout(ok,6000)})])};
 function gifPrintOn(){window.haomaPrintPrep();Q('[data-gif]').forEach(function(m){if(!m.dataset.gif)return;
  m.dataset.printPrev=m.getAttribute('src')||'';m.dataset.printWas=m.dataset.on||'';
  m.src=m.dataset.gif;m.dataset.on='1'})}
 function gifPrintOff(){Q('[data-gif]').forEach(function(m){if(!('printPrev' in m.dataset))return;
  m.src=m.dataset.printPrev;m.dataset.on=m.dataset.printWas;
  delete m.dataset.printPrev;delete m.dataset.printWas})}
 window.addEventListener('beforeprint',gifPrintOn);window.addEventListener('afterprint',gifPrintOff);
 if(window.matchMedia){var pm=matchMedia('print');
  if(pm.addEventListener)pm.addEventListener('change',function(e){e.matches?gifPrintOn():gifPrintOff()});
  else if(pm.addListener)pm.addListener(function(e){e.matches?gifPrintOn():gifPrintOff()})}
})();

/* ===== v5: interactive myth map — pan, zoom, eras, dock ===== */
(function(){
var Q=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
var dragMap=null,dragLast={x:0,y:0},dragStart={x:0,y:0},dragMoved=false;
document.addEventListener('mousemove',function(e){
  if(!dragMap||!dragMap._mapPan)return;
  if(Math.abs(e.clientX-dragStart.x)+Math.abs(e.clientY-dragStart.y)>6)dragMoved=true;
  dragMap._mapPan(e.clientX-dragLast.x,e.clientY-dragLast.y);dragLast.x=e.clientX;dragLast.y=e.clientY;
});
document.addEventListener('mouseup',function(){
  if(dragMap&&dragMap._mapPanEnd)dragMap._mapPanEnd();
  dragMap=null;
});

Q('.myth-map').forEach(function(map){
  /* Regional / small maps must not zoom out past fit: that only letterboxes and
     breaks the engraved frame. The world overview may still go below 1 via
     data-minzoom (default 1). Pan only when zoomed in enough that there is room. */
  var minZ=parseFloat(map.getAttribute('data-minzoom'));if(!(minZ>0))minZ=1;
  var maxZ=4,z=1,ox=0,oy=0,lastDist=0,inner=null,sx=0,sy=0;
  var mapW=0,mapH=0,innerW=0,innerH=0,zBand='',raf=0,dirty=0,dragging=false;
  var wrap=map.closest('.myth-map-wrap')||map.parentElement;
  var bg=map.querySelector('.myth-map__bg')||map.querySelector('.myth-map__svg');
  var pins=map.querySelector('.myth-map__pins');
  var regions=Q('.myth-region',map);
  var zooms=Q('[data-zm]',map);
  var dock=map.querySelector('[data-map-dock]');
  var dockTitle=map.querySelector('[data-map-dock-title]');
  var dockNote=map.querySelector('[data-map-dock-note]');
  var dockEra=map.querySelector('[data-map-dock-era]');
  var dockOpen=map.querySelector('[data-map-dock-open]');
  var dockClear=map.querySelector('[data-map-dock-clear]');
  var eraBtns=Q('.myth-map__era',map);
  var places=wrap?wrap.querySelector('.myth-map__places'):null;
  var legend=wrap?Q('.myth-map__legend li',wrap):[];
  var eraLabels={};
  eraBtns.forEach(function(b){if(b.dataset.era&&b.dataset.era!=='all')eraLabels[b.dataset.era]=b.textContent.trim()});
  inner=document.createElement('div');inner.className='myth-map__inner';
  if(bg)inner.appendChild(bg);
  regions.forEach(function(rg){inner.appendChild(rg)});
  if(pins)inner.appendChild(pins);
  map.insertBefore(inner,map.querySelector('.myth-map__ctrl'));
  function canPan(){return z>1.001}
  function measure(){
    mapW=map.clientWidth;mapH=map.clientHeight;
    innerW=inner.offsetWidth||mapW;innerH=inner.offsetHeight||mapH;
  }
  function fit(){
    var nw=0,nh=0,tag=bg?bg.tagName.toLowerCase():'';
    if(tag==='img'){nw=bg.naturalWidth;nh=bg.naturalHeight}
    else if(bg){var vb=(bg.getAttribute('viewBox')||'').split(/[\s,]+/);nw=parseFloat(vb[2])||0;nh=parseFloat(vb[3])||0}
    if(!nw||!nh){nw=800;nh=480}
    var ar=nw/nh,cw=map.clientWidth,ch=map.clientHeight,w=cw,h=w/ar;
    if(h>ch){h=ch;w=h*ar}
    inner.style.width=w+'px';inner.style.height=h+'px';
    measure();
  }
  /* --izr keeps hover cards the same on-screen size at every zoom.
     Pan frames only write the transform; chrome/band sync runs on settle. */
  function band(){
    var b=z<0.85?'far':(z>1.6?'near':'mid');
    if(b!==zBand){zBand=b;map.setAttribute('data-zband',b)}
  }
  function syncCtrl(){zooms.forEach(function(b){var v=+b.dataset.zm;
    b.disabled=v===0?z<=1.001&&ox===0&&oy===0:(v<0?z<=minZ+0.001:z>=maxZ-0.001)})}
  function clamp(){
    if(!canPan()){ox=0;oy=0;return}
    if(!mapW)measure();
    var mw=mapW*(z-1)/2,mh=mapH*(z-1)/2;
    ox=Math.max(-mw,Math.min(mw,ox));oy=Math.max(-mh,Math.min(mh,oy));
  }
  function paint(){
    clamp();
    inner.style.transform='translate3d('+ox+'px,'+oy+'px,0) scale('+z+')';
  }
  function settle(){
    paint();
    map.style.setProperty('--iz',z);
    map.style.setProperty('--izr',1/z);
    band();
    map.classList.toggle('myth-map--fixed',!canPan());
    syncCtrl();
  }
  function apply(){settle()}
  function schedule(full){
    dirty|=full?2:1;
    if(raf)return;
    raf=requestAnimationFrame(function(){
      raf=0;
      var want=dirty;dirty=0;
      if(want&2)settle();else paint();
    });
  }
  function setDragging(on){
    dragging=!!on;
    map.classList.toggle('myth-map--drag',dragging);
    if(!dragging)schedule(2);
  }
  map._mapPan=function(dx,dy){ox+=dx;oy+=dy;schedule(0)};
  map._mapPanEnd=function(){setDragging(false)};
  /* Centre a map % point at a neighbour-friendly zoom (not max tight). */
  function goTo(fx,fy,kind){
    fx=Math.max(0,Math.min(100,fx))/100;fy=Math.max(0,Math.min(100,fy))/100;
    var target=kind==='region'?1.35:1.55;
    target=Math.max(minZ,Math.min(maxZ,target));
    z=target;
    if(!innerW)measure();
    ox=-(fx-0.5)*innerW*z;oy=-(fy-0.5)*innerH*z;settle();
  }
  function pointOf(el){
    if(!el)return null;
    if(el.classList.contains('myth-pin')){
      var x=parseFloat(el.style.left),y=parseFloat(el.style.top);
      if(isFinite(x)&&isFinite(y))return{x:x,y:y,kind:'pin'};
    }
    var hx=parseFloat(el.style.getPropertyValue('--hx')),hy=parseFloat(el.style.getPropertyValue('--hy'));
    if(isFinite(hx)&&isFinite(hy))return{x:hx,y:hy,kind:'region'};
    return null;
  }
  var prePrint={z:1,ox:0,oy:0};
  function mapPrintOn(){prePrint={z:z,ox:ox,oy:oy};z=1;ox=0;oy=0;apply()}
  function mapPrintOff(){z=prePrint.z;ox=prePrint.ox;oy=prePrint.oy;apply()}
  window.addEventListener('beforeprint',mapPrintOn);window.addEventListener('afterprint',mapPrintOff);
  if(window.matchMedia){var mpm=matchMedia('print');
   if(mpm.addEventListener)mpm.addEventListener('change',function(e){e.matches?mapPrintOn():mapPrintOff()});
   else if(mpm.addListener)mpm.addListener(function(e){e.matches?mapPrintOn():mapPrintOff()})}
  zooms.forEach(function(b){b.onclick=function(){var v=+b.dataset.zm;if(v===0){z=1;ox=0;oy=0}else{z=Math.max(minZ,Math.min(maxZ,z+v*0.4))}settle()}});
  var wheelT=0;
  map.addEventListener('wheel',function(e){
    e.preventDefault();
    z=Math.max(minZ,Math.min(maxZ,z-e.deltaY*0.001));
    schedule(1);
    clearTimeout(wheelT);wheelT=setTimeout(function(){schedule(2)},80);
  },{passive:false});
  map.addEventListener('mousedown',function(e){
    if(e.target.closest('.myth-pin,.myth-region__hit,.myth-map__zoom,.myth-map__era,.myth-map__dock'))return;
    if(!canPan())return;dragMoved=false;dragStart.x=sx=e.clientX;dragStart.y=sy=e.clientY;
    dragMap=map;dragLast.x=e.clientX;dragLast.y=e.clientY;setDragging(true);e.preventDefault()});
  map.addEventListener('click',function(e){if(dragMoved){e.preventDefault();e.stopPropagation();dragMoved=false}},true);
  map.addEventListener('touchstart',function(e){
    sx=e.touches[0].clientX;sy=e.touches[0].clientY;dragMoved=false;
    if(e.touches.length===2){lastDist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);setDragging(true)}
    else if(e.touches.length===1){dragLast.x=e.touches[0].clientX;dragLast.y=e.touches[0].clientY;if(canPan())setDragging(true)}
  },{passive:true});
  map.addEventListener('touchmove',function(e){
    if(Math.abs(e.touches[0].clientX-sx)+Math.abs(e.touches[0].clientY-sy)>8)dragMoved=true;
    if(e.touches.length===2){
      var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
      z=Math.max(minZ,Math.min(maxZ,z*(d/lastDist)));lastDist=d;schedule(1);
    }else if(e.touches.length===1&&canPan()){
      ox+=e.touches[0].clientX-dragLast.x;oy+=e.touches[0].clientY-dragLast.y;
      dragLast.x=e.touches[0].clientX;dragLast.y=e.touches[0].clientY;schedule(0);
    }
    e.preventDefault();
  },{passive:false});
  map.addEventListener('touchend',function(){setDragging(false)});
  map.addEventListener('touchcancel',function(){setDragging(false)});

  function setEra(era){
    era=era||'all';
    map.setAttribute('data-era',era);
    eraBtns.forEach(function(b){b.classList.toggle('is-on',b.dataset.era===era)});
    function vis(el){var e=el.getAttribute('data-era')||'';return era==='all'||!e||e===era}
    Q('.myth-region,.myth-pin',map).forEach(function(el){el.hidden=!vis(el)});
    legend.forEach(function(li){li.hidden=!vis(li)});
  }
  eraBtns.forEach(function(b){b.addEventListener('click',function(){setEra(b.dataset.era)})});

  function itemCopy(el){
    var kind=el.getAttribute('data-kind')||'pin';
    var mid=el.getAttribute('data-mid')||'';
    var era=el.getAttribute('data-era')||'';
    var label='',note='';
    if(kind==='region'){
      var pop=el.querySelector('.myth-region__pop');
      if(pop){var b=pop.querySelector('b');var s=pop.querySelector('span');label=b?b.textContent.trim():'';note=s?s.textContent.trim():''}
    }else{
      label=(el.querySelector('.myth-pin__label')||{}).textContent||'';
      note=(el.querySelector('.myth-pin__pop')||{}).textContent||'';
      label=String(label).trim();note=String(note).trim();
    }
    if(!label)label=el.getAttribute('aria-label')||mid;
    var href=el.tagName==='A'?el.getAttribute('href')||'':'';
    return{el:el,kind:kind,mid:mid,era:era,label:label,note:note,href:href};
  }
  function closeDock(){
    if(!dock)return;dock.hidden=true;map.classList.remove('myth-map--dock');
    Q('.myth-pin.is-focus,.myth-region.is-focus',map).forEach(function(el){el.classList.remove('is-focus')});
  }
  function openDock(el){
    if(!dock||!el)return;
    var info=itemCopy(el);
    dockTitle.textContent=info.label||'';
    dockNote.textContent=info.note||'';
    dockNote.hidden=!info.note;
    if(info.era&&eraLabels[info.era]){dockEra.hidden=false;dockEra.textContent=eraLabels[info.era]}
    else{dockEra.hidden=true;dockEra.textContent=''}
    if(info.href){dockOpen.hidden=false;dockOpen.href=info.href}else{dockOpen.hidden=true;dockOpen.removeAttribute('href')}
    Q('.myth-pin.is-focus,.myth-region.is-focus',map).forEach(function(n){n.classList.remove('is-focus')});
    el.classList.add('is-focus');
    dock.hidden=false;map.classList.add('myth-map--dock');
    if(info.mid){try{history.replaceState(null,'','#pin-'+info.mid)}catch(err){}}
  }
  if(dockClear)dockClear.addEventListener('click',function(){closeDock();try{history.replaceState(null,'',location.pathname+location.search)}catch(err){}});

  function onItemActivate(e){
    var el=e.target.closest('.myth-pin,.myth-region');
    if(!el||!map.contains(el))return;
    if(dragMoved)return;
    e.preventDefault();
    flyTo(el);
  }
  map.addEventListener('click',onItemActivate);
  /* Pin tooltip edge-fitting */
  Q('.myth-pin',map).forEach(function(pin){var pop=pin.querySelector('.myth-pin__pop');if(!pop)return;
   function fitPop(){pop.style.setProperty('--nx','0px');pin.classList.remove('myth-pin--below');
    var mr=map.getBoundingClientRect(),r=pop.getBoundingClientRect(),dx=0;
    if(r.top<mr.top+8){pin.classList.add('myth-pin--below');r=pop.getBoundingClientRect()}
    if(r.left<mr.left+8)dx=mr.left+8-r.left;else if(r.right>mr.right-8)dx=mr.right-8-r.right;pop.style.setProperty('--nx',dx/z+'px')}
   pin.addEventListener('mouseenter',fitPop);pin.addEventListener('focusin',fitPop)});
  /* Shared region hover tip above every border */
  var tip=document.createElement('div');tip.className='myth-region__pop myth-map__tip';tip.setAttribute('aria-hidden','true');
  inner.appendChild(tip);map.classList.add('myth-map--tip');
  Q('.myth-region',map).forEach(function(rg){var pop=rg.querySelector('.myth-region__pop'),hit=rg.querySelector('.myth-region__hit');if(!pop||!hit)return;
   function show(){if(rg.hidden)return;tip.innerHTML=pop.innerHTML;tip.style.setProperty('--hx',rg.style.getPropertyValue('--hx'));
    tip.style.setProperty('--hy',rg.style.getPropertyValue('--hy'));tip.style.setProperty('--pc',getComputedStyle(rg).getPropertyValue('--pc'));
    tip.style.setProperty('--nx','0px');tip.style.setProperty('--ny','0px');tip.classList.add('on');
    var r=tip.getBoundingClientRect(),mr=map.getBoundingClientRect(),dx=0,dy=0;
    if(r.left<mr.left+8)dx=mr.left+8-r.left;else if(r.right>mr.right-8)dx=mr.right-8-r.right;
    if(r.top<mr.top+8)dy=mr.top+8-r.top;else if(r.bottom>mr.bottom-8)dy=mr.bottom-8-r.bottom;
    tip.style.setProperty('--nx',dx/z+'px');tip.style.setProperty('--ny',dy/z+'px')}
   function hide(){tip.classList.remove('on')}
   hit.addEventListener('mouseenter',show);hit.addEventListener('mouseleave',hide);
   rg.addEventListener('focusin',show);rg.addEventListener('focusout',hide)});

  function flyTo(el){
    if(!el)return;
    if(el.hidden){
      var era=el.getAttribute('data-era')||'';
      setEra(era||'all');
    }
    var pt=pointOf(el);
    if(pt)goTo(pt.x,pt.y,pt.kind);
    openDock(el);
    legend.forEach(function(li){
      var on=li.getAttribute('data-mid')===(el.getAttribute('data-mid')||'');
      var b=li.querySelector('.myth-map__leg-btn');if(b)b.classList.toggle('is-on',on);
    });
    try{el.focus({preventScroll:true})}catch(err){}
  }
  legend.forEach(function(li){
    var btn=li.querySelector('.myth-map__leg-btn');if(!btn)return;
    btn.addEventListener('click',function(){
      var mid=li.getAttribute('data-mid');if(!mid)return;
      var el=map.querySelector('[data-mid="'+CSS.escape(mid)+'"]')||map.querySelector('[data-mid="'+mid+'"]');
      if(!el)return;
      if(places&&!places.open)places.open=true;
      flyTo(el);
    });
  });

  function focusHash(){
    var h=location.hash||'';
    var m=/^#pin-(.+)$/.exec(h);if(!m)return;
    var el=map.querySelector('[data-mid="'+CSS.escape(m[1])+'"]')||map.querySelector('[data-mid="'+m[1]+'"]');
    if(!el)return;
    var era=el.getAttribute('data-era')||'';
    if(era)setEra(era);else setEra('all');
    if(places)places.open=true;
    flyTo(el);
  }

  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){map.classList.toggle('myth-map--off',!e.isIntersecting)});
    },{rootMargin:'60px',threshold:0.01});
    io.observe(map);
  }

  fit();
  if(bg&&bg.tagName.toLowerCase()==='img'){if(bg.complete&&bg.naturalWidth)fit();else bg.addEventListener('load',fit)}
  var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(function(){fit();settle()},120)});
  if(window.ResizeObserver){new ResizeObserver(function(){fit();settle()}).observe(map)}
  setEra(map.getAttribute('data-era')||'all');
  settle();
  focusHash();
  window.addEventListener('hashchange',focusHash);
});
})();

/* ===== custom audio player + click-to-play YouTube ===== */
(function(){
function fmt(t){if(!isFinite(t)||t<0)return'—:—';var m=Math.floor(t/60),s=Math.floor(t%60);return m+':'+(s<10?'0':'')+s}
function wirePlayer(root){
  var a=root.querySelector('audio'),btn=root.querySelector('[data-ha-play]'),seek=root.querySelector('[data-ha-seek]');
  var fill=root.querySelector('[data-ha-fill]'),knob=root.querySelector('[data-ha-knob]');
  var cur=root.querySelector('[data-ha-cur]'),dur=root.querySelector('[data-ha-dur]');
  if(!a||!btn||!seek)return;
  function setPlaying(on){root.classList.toggle('is-playing',on);btn.setAttribute('aria-label',on?(btn.dataset.pause||'Pause'):(btn.dataset.play||'Play'))}
  function pct(){return a.duration?Math.max(0,Math.min(1,a.currentTime/a.duration)):0}
  function paint(){var p=pct()*100;if(fill)fill.style.width=p+'%';if(knob)knob.style.insetInlineStart=p+'%';if(cur)cur.textContent=fmt(a.currentTime);if(dur)dur.textContent=fmt(a.duration);seek.setAttribute('aria-valuenow',String(Math.round(p)))}
  function seekTo(clientX){var r=seek.getBoundingClientRect(),x=clientX-r.left,p=r.width?x/r.width:0;
    if(getComputedStyle(document.documentElement).direction==='rtl')p=1-p;
    if(a.duration){a.currentTime=Math.max(0,Math.min(1,p))*a.duration;paint()}}
  function mediaMeta(){
    if(!('mediaSession' in navigator))return;
    var titleEl=root.querySelector('.ha-player__title');
    var title=(titleEl&&titleEl.textContent)||document.title||'Haoma';
    var art=[];
    try{
      var icon=document.querySelector('link[rel="apple-touch-icon"],link[rel="icon"][sizes="192x192"]');
      if(icon&&icon.href)art=[{src:icon.href,sizes:'192x192',type:'image/png'}];
    }catch(e){}
    try{
      navigator.mediaSession.metadata=new MediaMetadata({title:title,artist:'Haoma',album:document.documentElement.lang==='fa'?'هوم':'Haoma',artwork:art});
    }catch(e2){}
  }
  function bindMediaSession(){
    if(!('mediaSession' in navigator))return;
    try{
      navigator.mediaSession.setActionHandler('play',function(){a.play().catch(function(){})});
      navigator.mediaSession.setActionHandler('pause',function(){a.pause()});
      navigator.mediaSession.setActionHandler('seekbackward',function(){if(a.duration)a.currentTime=Math.max(0,a.currentTime-10)});
      navigator.mediaSession.setActionHandler('seekforward',function(){if(a.duration)a.currentTime=Math.min(a.duration,a.currentTime+10)});
    }catch(e){}
  }
  btn.addEventListener('click',function(){if(a.paused){document.querySelectorAll('[data-ha-player] audio').forEach(function(o){if(o!==a)o.pause()});a.play().catch(function(){})}else a.pause()});
  a.addEventListener('play',function(){setPlaying(true);mediaMeta();try{navigator.mediaSession.playbackState='playing'}catch(e){}});
  a.addEventListener('pause',function(){setPlaying(false);try{navigator.mediaSession.playbackState='paused'}catch(e){}});
  a.addEventListener('ended',function(){setPlaying(false);paint();try{navigator.mediaSession.playbackState='none'}catch(e){}});
  a.addEventListener('timeupdate',paint);
  a.addEventListener('loadedmetadata',paint);
  var drag=false;
  seek.addEventListener('pointerdown',function(e){drag=true;seek.setPointerCapture(e.pointerId);seekTo(e.clientX)});
  seek.addEventListener('pointermove',function(e){if(drag)seekTo(e.clientX)});
  seek.addEventListener('pointerup',function(){drag=false});
  seek.addEventListener('pointercancel',function(){drag=false});
  seek.addEventListener('keydown',function(e){if(!a.duration)return;var step=Math.max(2,a.duration*0.05);
    if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();a.currentTime=Math.max(0,Math.min(a.duration,a.currentTime+(e.key==='ArrowRight'?step:-step)));paint()}});
  bindMediaSession();
  paint();
}
document.querySelectorAll('[data-ha-player]').forEach(wirePlayer);

document.querySelectorAll('[data-yt-card]').forEach(function(card){
  var id=card.getAttribute('data-yt-id');if(!id)return;
  var hit=card.querySelector('[data-yt-play]');if(!hit)return;
  hit.addEventListener('click',function(){
    if(card.classList.contains('is-playing'))return;
    var f=document.createElement('iframe');
    f.src='https://www.youtube-nocookie.com/embed/'+encodeURIComponent(id)+'?autoplay=1&rel=0';
    f.title='YouTube';f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen=true;f.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
    card.appendChild(f);card.classList.add('is-playing');
  });
});
})();

/* ===== culture easter eggs (fixed culture hubs + articles only) ===== */
(function(){
  var D=document.documentElement,reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;
  if(!D.hasAttribute('data-fixed'))return;
  var cult=D.getAttribute('data-culture')||'';
  if(!cult||cult==='base')return;

  var whispers={
    iranian:'asha',
    greek:'athena',
    indian:'padma',
    mesopotamian:'inanna',
    norse:'futhark'
  };

  /* Hidden glyph in the motif rail — hover the rail or triple-click the brand */
  var motif=document.querySelector('.motif');
  if(motif){
    var egg=document.createElement('span');
    egg.className='cult-egg';egg.setAttribute('aria-hidden','true');
    egg.dataset.whisper=whispers[cult]||cult;
    motif.appendChild(egg);
    var hideT;
    function showEgg(ms){
      motif.classList.add('is-egg');egg.classList.add('is-on');
      clearTimeout(hideT);
      hideT=setTimeout(function(){motif.classList.remove('is-egg');egg.classList.remove('is-on')},ms||2200);
    }
    motif.addEventListener('mouseenter',function(){showEgg(2800)});
    var brand=document.querySelector('.brand');
    if(brand){
      var taps=0,tapT;
      brand.addEventListener('click',function(){
        taps++;clearTimeout(tapT);
        tapT=setTimeout(function(){taps=0},700);
        if(taps>=3){taps=0;showEgg(3600)}
      });
    }
  }

  /* Hero seal brightens on hover / long-press focus */
  var hero=document.querySelector('.hero-art');
  if(hero){
    hero.addEventListener('mouseenter',function(){hero.classList.add('is-seal')});
    hero.addEventListener('mouseleave',function(){hero.classList.remove('is-seal')});
    hero.addEventListener('focusin',function(){hero.classList.add('is-seal')});
    hero.addEventListener('focusout',function(){hero.classList.remove('is-seal')});
  }

  /* Scroll-reveal section headings (and first card row) */
  if(!reduced&&'IntersectionObserver' in window){
    var nodes=[].slice.call(document.querySelectorAll('article h2, article h3, .trad-hub, .atlas, article .cards'));
    nodes.forEach(function(n){n.classList.add('cult-reveal')});
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(e.isIntersecting){e.target.classList.add('is-in');io.unobserve(e.target)}
      });
    },{rootMargin:'0px 0px -8% 0px',threshold:0.12});
    nodes.forEach(function(n){io.observe(n)});
  }
})();

/* ===== hero height comes from CSS (--hero-h): the same box on every page, so
   nothing is measured or stretched to the viewport here ===== */

/* ===== Culture easter eggs (culture-bound pages only: data-fixed) =====
   Soft, tasteful: scroll seal, brand triple-click, ↑↑↓↓ chord.
   Motifs are CSS masks already on the page — no fan-art downloads.
   Documented in AI.md §5. Honours prefers-reduced-motion (still shows
   static seal / glyph; skips motion classes that only animate). */
(function(){
  var D=document.documentElement;
  if(!D.hasAttribute('data-fixed'))return;
  var cult=D.dataset.culture;if(!cult||cult==='base')return;
  var eggs=document.querySelector('[data-culture-eggs]');
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var litTimer=0;
  function lightEgg(ms){
    D.classList.add('egg-lit');
    clearTimeout(litTimer);
    litTimer=setTimeout(function(){D.classList.remove('egg-lit')},ms||2200);
  }
  /* Motif appears once you have read a bit of the page */
  function onScroll(){
    if(!eggs)return;
    var max=Math.max(1,document.documentElement.scrollHeight-window.innerHeight);
    if(window.scrollY/max>=.38){D.classList.add('eggs-awake');window.removeEventListener('scroll',onScroll)}
  }
  if(eggs){
    window.addEventListener('scroll',onScroll,{passive:true});
    onScroll();
  }
  /* Brand: double-click (single click still goes home) → brief sigil flash */
  var brand=document.querySelector('.brand');
  if(brand){
    brand.addEventListener('dblclick',function(e){
      e.preventDefault();
      lightEgg(2400);D.classList.add('eggs-awake');
    });
  }
  /* Konami-light: ↑ ↑ ↓ ↓ (no need for the full arcade string) */
  var seq=[],want=['ArrowUp','ArrowUp','ArrowDown','ArrowDown'];
  document.addEventListener('keydown',function(e){
    if(e.metaKey||e.ctrlKey||e.altKey)return;
    if(e.target&&(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.target.isContentEditable))return;
    if(e.key!=='ArrowUp'&&e.key!=='ArrowDown'){seq=[];return}
    seq.push(e.key);if(seq.length>want.length)seq.shift();
    if(seq.length===want.length&&seq.every(function(k,i){return k===want[i]})){
      seq=[];lightEgg(2800);D.classList.add('eggs-awake');
    }
  });
  /* Culture-specific quiet hover: long-press motif strip reveals footer glyph */
  var motif=document.querySelector('.motif');
  if(motif){
    var hold=0;
    motif.addEventListener('pointerdown',function(){
      hold=setTimeout(function(){lightEgg(2000)},650);
    });
    ['pointerup','pointerleave','pointercancel'].forEach(function(ev){
      motif.addEventListener(ev,function(){clearTimeout(hold)});
    });
  }
  if(reduce){/* keep eggs-awake/egg-lit as opacity reveals; CSS kills motion */}
})();
