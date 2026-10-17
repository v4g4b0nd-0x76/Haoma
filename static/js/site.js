(function(){
var D=document.documentElement,Q=function(s,r){return[].slice.call((r||document).querySelectorAll(s))},P={},fixed=D.hasAttribute('data-fixed')?D.dataset.culture:null;
try{P=JSON.parse(localStorage.getItem('prefs')||'{}')}catch(e){}
function save(){try{localStorage.setItem('prefs',JSON.stringify(P))}catch(e){}}
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
Q('[data-act]').forEach(function(b){if(!hasSide&&/nav|dock/.test(b.dataset.act))b.hidden=true;b.onclick=function(){act[b.dataset.act]();save()}});
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
function setPick(p,first){
 try{localStorage.setItem('culture',p)}catch(e){}
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
   if(p==='base'||!href){en.removeAttribute('href');en.setAttribute('tabindex','-1')}
   else{en.href=href;en.removeAttribute('tabindex')}}}
}
/* Navigate to a culture (or cultures index for base). */
function pickGo(p){var href=hrefFor(p);if(!href)return;try{localStorage.setItem('culture',p)}catch(e){}location.href=href}
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
var p0='iranian';try{p0=localStorage.getItem('culture')||'iranian'}catch(e){}
if(!pill(p0)&&!opt(p0)&&p0!=='base')p0='iranian';
setPick(p0,true);
/* slider */
Q('.slider').forEach(function(s){var r=s.querySelector('.rail'),rtl=getComputedStyle(r).direction==='rtl';
 Q('[data-dir]',s).forEach(function(b){b.onclick=function(){r.scrollBy({left:(+b.dataset.dir)*(rtl?-1:1)*r.clientWidth*.8,behavior:'smooth'})}})});
/* tabs */
Q('[role=tablist]').forEach(function(l){var bs=Q('button',l);bs.forEach(function(x){x.onclick=function(){bs.forEach(function(y){y.setAttribute('aria-selected',y===x);document.getElementById(y.getAttribute('aria-controls')).hidden=y!==x})}})});

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

/* ===== v5: interactive myth map — pan, zoom, pin tooltips ===== */
(function(){
var Q=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
Q('.myth-map').forEach(function(map){
  /* Regional / small maps must not zoom out past fit: that only letterboxes and
     breaks the engraved frame. The world overview may still go below 1 via
     data-minzoom (default 1). Pan only when zoomed in enough that there is room. */
  var minZ=parseFloat(map.getAttribute('data-minzoom'));if(!(minZ>0))minZ=1;
  var maxZ=4,z=1,ox=0,oy=0,dragging=false,lastX=0,lastY=0,lastDist=0,inner=null,moved=false,sx=0,sy=0;
  var bg=map.querySelector('.myth-map__bg')||map.querySelector('.myth-map__svg');
  var pins=map.querySelector('.myth-map__pins');
  var regions=Q('.myth-region',map);
  var zooms=Q('[data-zm]',map);
  inner=document.createElement('div');inner.className='myth-map__inner';
  if(bg)inner.appendChild(bg);
  regions.forEach(function(rg){inner.appendChild(rg)});
  if(pins)inner.appendChild(pins);
  map.insertBefore(inner,map.querySelector('.myth-map__ctrl'));
  function canPan(){return z>1.001}
  function fit(){
    var nw=0,nh=0,tag=bg?bg.tagName.toLowerCase():'';
    if(tag==='img'){nw=bg.naturalWidth;nh=bg.naturalHeight}
    else if(bg){var vb=(bg.getAttribute('viewBox')||'').split(/[\s,]+/);nw=parseFloat(vb[2])||0;nh=parseFloat(vb[3])||0}
    if(!nw||!nh){nw=800;nh=480}
    var ar=nw/nh,cw=map.clientWidth,ch=map.clientHeight,w=cw,h=w/ar;
    if(h>ch){h=ch;w=h*ar}
    inner.style.width=w+'px';inner.style.height=h+'px';
  }
  /* --izr keeps hover cards the same on-screen size at every zoom */
  function band(){map.setAttribute('data-zband',z<0.85?'far':(z>1.6?'near':'mid'))}
  function syncCtrl(){zooms.forEach(function(b){var v=+b.dataset.zm;
    b.disabled=v===0?z<=1.001&&ox===0&&oy===0:(v<0?z<=minZ+0.001:z>=maxZ-0.001)})}
  function apply(){clamp();inner.style.transform='translate('+ox+'px,'+oy+'px) scale('+z+')';
    map.style.setProperty('--iz',z);map.style.setProperty('--izr',1/z);band();
    map.classList.toggle('myth-map--fixed',!canPan());syncCtrl()}
  function clamp(){if(!canPan()){ox=0;oy=0;return}var mw=map.clientWidth*(z-1)/2,mh=map.clientHeight*(z-1)/2;
    ox=Math.max(-mw,Math.min(mw,ox));oy=Math.max(-mh,Math.min(mh,oy))}
  var prePrint={z:1,ox:0,oy:0};
  function mapPrintOn(){prePrint={z:z,ox:ox,oy:oy};z=1;ox=0;oy=0;apply()}
  function mapPrintOff(){z=prePrint.z;ox=prePrint.ox;oy=prePrint.oy;apply()}
  window.addEventListener('beforeprint',mapPrintOn);window.addEventListener('afterprint',mapPrintOff);
  if(window.matchMedia){var mpm=matchMedia('print');
   if(mpm.addEventListener)mpm.addEventListener('change',function(e){e.matches?mapPrintOn():mapPrintOff()});
   else if(mpm.addListener)mpm.addListener(function(e){e.matches?mapPrintOn():mapPrintOff()})}
  zooms.forEach(function(b){b.onclick=function(){var v=+b.dataset.zm;if(v===0){z=1;ox=0;oy=0}else{z=Math.max(minZ,Math.min(maxZ,z+v*0.4))}apply()}});
  map.addEventListener('wheel',function(e){e.preventDefault();z=Math.max(minZ,Math.min(maxZ,z-e.deltaY*0.001));apply()},{passive:false});
  map.addEventListener('mousedown',function(e){if(!canPan())return;sx=e.clientX;sy=e.clientY;moved=false;if(e.target.closest('.myth-pin,.myth-map__zoom'))return;dragging=true;lastX=e.clientX;lastY=e.clientY;e.preventDefault()});
  document.addEventListener('mousemove',function(e){if(!dragging)return;if(Math.abs(e.clientX-sx)+Math.abs(e.clientY-sy)>6)moved=true;ox+=e.clientX-lastX;oy+=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;apply()});
  document.addEventListener('mouseup',function(){dragging=false});
  map.addEventListener('click',function(e){if(moved){e.preventDefault();e.stopPropagation();moved=false}},true);
  map.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY;moved=false;if(e.touches.length===2){lastDist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY)}else if(e.touches.length===1){lastX=e.touches[0].clientX;lastY=e.touches[0].clientY}},{passive:true});
  map.addEventListener('touchmove',function(e){if(Math.abs(e.touches[0].clientX-sx)+Math.abs(e.touches[0].clientY-sy)>8)moved=true;
    if(e.touches.length===2){var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);z=Math.max(minZ,Math.min(maxZ,z*(d/lastDist)));lastDist=d;apply()}
    else if(e.touches.length===1&&canPan()){ox+=e.touches[0].clientX-lastX;oy+=e.touches[0].clientY-lastY;lastX=e.touches[0].clientX;lastY=e.touches[0].clientY;apply()}
    e.preventDefault()},{passive:false});
  /* Pin tooltip edge-fitting: slide sideways to stay in the frame, and open below
     the pin when the frame's top edge would cut the card off */
  Q('.myth-pin',map).forEach(function(pin){var pop=pin.querySelector('.myth-pin__pop');if(!pop)return;
   function fit(){pop.style.setProperty('--nx','0px');pin.classList.remove('myth-pin--below');
    var mr=map.getBoundingClientRect(),r=pop.getBoundingClientRect(),dx=0;
    if(r.top<mr.top+8){pin.classList.add('myth-pin--below');r=pop.getBoundingClientRect()}
    if(r.left<mr.left+8)dx=mr.left+8-r.left;else if(r.right>mr.right-8)dx=mr.right-8-r.right;pop.style.setProperty('--nx',dx/z+'px')}
   pin.addEventListener('mouseenter',fit);pin.addEventListener('focusin',fit)});
  /* Region descriptions. Each region is its own stacking layer, so a card drawn
     inside one sits under every border painted after it. One shared card above
     all regions and pins carries the hovered region's text instead; it takes no
     pointer events, so the pins under it stay hoverable. */
  var tip=document.createElement('div');tip.className='myth-region__pop myth-map__tip';tip.setAttribute('aria-hidden','true');
  inner.appendChild(tip);map.classList.add('myth-map--tip');
  Q('.myth-region',map).forEach(function(rg){var pop=rg.querySelector('.myth-region__pop'),hit=rg.querySelector('.myth-region__hit');if(!pop||!hit)return;
   function show(){tip.innerHTML=pop.innerHTML;tip.style.setProperty('--hx',rg.style.getPropertyValue('--hx'));
    tip.style.setProperty('--hy',rg.style.getPropertyValue('--hy'));tip.style.setProperty('--pc',getComputedStyle(rg).getPropertyValue('--pc'));
    tip.style.setProperty('--nx','0px');tip.style.setProperty('--ny','0px');tip.classList.add('on');
    var r=tip.getBoundingClientRect(),mr=map.getBoundingClientRect(),dx=0,dy=0;
    if(r.left<mr.left+8)dx=mr.left+8-r.left;else if(r.right>mr.right-8)dx=mr.right-8-r.right;
    if(r.top<mr.top+8)dy=mr.top+8-r.top;else if(r.bottom>mr.bottom-8)dy=mr.bottom-8-r.bottom;
    tip.style.setProperty('--nx',dx/z+'px');tip.style.setProperty('--ny',dy/z+'px')}
   function hide(){tip.classList.remove('on')}
   hit.addEventListener('mouseenter',show);hit.addEventListener('mouseleave',hide);
   rg.addEventListener('focusin',show);rg.addEventListener('focusout',hide)});
  fit();
  if(bg&&bg.tagName.toLowerCase()==='img'){if(bg.complete&&bg.naturalWidth)fit();else bg.addEventListener('load',fit)}
  var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(fit,120)});
  if(window.ResizeObserver){new ResizeObserver(fit).observe(map)}/* refit if shown from a hidden tab */
  apply();
});
})();

/* ===== hero height comes from CSS (--hero-h): the same box on every page, so
   nothing is measured or stretched to the viewport here ===== */
