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
 pdf:function(){window.print()}};
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
function setPick(p,first){
 try{localStorage.setItem('culture',p)}catch(e){}
 var eff=fixed||p;D.dataset.pick=p;if(!fixed)D.dataset.culture=p;
 paintPick(eff);
 Q('.pills button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.pick===p)});
 /* The pick filters the home page only: on the cultures index it hid every card but
    the last culture chosen, so the page "showed only one culture". */
 if(cine)Q('.cards li[data-culture],.panel[data-culture]').forEach(function(e){e.hidden=eff!=='base'&&e.dataset.culture!==eff});
 if(cine){var sl=Q('.slide',cine),on=sl.filter(function(s){return s.dataset.culture===p})[0]||sl[0],q=Q('.quote',cine)[0],en=Q('.enter',cine)[0],o=opt(p);
  cine.dataset.culture=p;sl.forEach(function(s){s.classList.toggle('on',s===on)});
  var put=function(){q.innerHTML=on.querySelector('template').innerHTML;q.style.opacity=1};
  if(first)put();else{q.style.opacity=0;setTimeout(put,250)}
  en.hidden=p==='base';if(o)en.href=o.dataset.href}}
/* choosing a culture always goes straight to that culture's own page */
function pickGo(p){var o=opt(p);if(!o)return;try{localStorage.setItem('culture',p)}catch(e){}if(o.dataset.href)location.href=o.dataset.href}
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
  if(e.key==='End'){e.preventDefault();items[items.length-1].focus();return}};
 btn.onkeydown=function(e){
  if(e.key==='ArrowDown'||e.key==='Enter'||e.key===' '){e.preventDefault();openPick(true)}
  else if(e.key==='Escape'){openPick(false)}};
 document.addEventListener('click',function(e){
  if(btn.getAttribute('aria-expanded')==='true'&&pick&&!pick.contains(e.target))openPick(false)});
}
Q('.pills button').forEach(function(b){b.onclick=function(){pickGo(b.dataset.pick)}});
var p0='iranian';try{p0=localStorage.getItem('culture')||'iranian'}catch(e){}
if(!opt(p0)&&p0!=='base')p0='iranian';
setPick(p0,true);
/* slider */
Q('.slider').forEach(function(s){var r=s.querySelector('.rail'),rtl=getComputedStyle(r).direction==='rtl';
 Q('[data-dir]',s).forEach(function(b){b.onclick=function(){r.scrollBy({left:(+b.dataset.dir)*(rtl?-1:1)*r.clientWidth*.8,behavior:'smooth'})}})});
/* tabs */
Q('[role=tablist]').forEach(function(l){var bs=Q('button',l);bs.forEach(function(x){x.onclick=function(){bs.forEach(function(y){y.setAttribute('aria-selected',y===x);document.getElementById(y.getAttribute('aria-controls')).hidden=y!==x})}})});
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
})();

/* ===== v5: interactive myth map — pan, zoom, pin tooltips ===== */
(function(){
var Q=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
Q('.myth-map').forEach(function(map){
  var minZ=0.5,maxZ=4,z=1,ox=0,oy=0,dragging=false,lastX=0,lastY=0,lastDist=0,inner=null,moved=false,sx=0,sy=0;
  /* Wrap bg + regions + pins in one transform layer: everything that carries a
     position on the artwork (background, country borders, pins, route) has to
     pan and zoom together, and each one's % coordinates are measured against
     this box rather than the outer frame. */
  var bg=map.querySelector('.myth-map__bg')||map.querySelector('.myth-map__svg');
  var pins=map.querySelector('.myth-map__pins');
  var regions=Q('.myth-region',map);
  inner=document.createElement('div');inner.className='myth-map__inner';
  if(bg)inner.appendChild(bg);
  regions.forEach(function(rg){inner.appendChild(rg)});
  if(pins)inner.appendChild(pins);
  map.insertBefore(inner,map.querySelector('.myth-map__ctrl'));
  /* Fit the layer to the artwork's own aspect ratio: the image is drawn edge-to-edge
     inside it (object-fit:fill), so pin percentages land on true map positions and
     zooming out reveals the whole map instead of empty letterbox. */
  function fit(){
    var nw=0,nh=0,tag=bg?bg.tagName.toLowerCase():'';
    if(tag==='img'){nw=bg.naturalWidth;nh=bg.naturalHeight}
    else if(bg){var vb=(bg.getAttribute('viewBox')||'').split(/[\s,]+/);nw=parseFloat(vb[2])||0;nh=parseFloat(vb[3])||0}
    if(!nw||!nh){nw=800;nh=480}
    var ar=nw/nh,cw=map.clientWidth,ch=map.clientHeight,w=cw,h=w/ar;
    if(h>ch){h=ch;w=h*ar}
    inner.style.width=w+'px';inner.style.height=h+'px';
  }
  /* --iz carries the current zoom to CSS so the hover cards can cancel it and
     stay the same on-screen size no matter how far the map is zoomed */
  function apply(){inner.style.transform='translate('+ox+'px,'+oy+'px) scale('+z+')';map.style.setProperty('--iz',z);map.style.setProperty('--izr',1/z)}
  function clamp(){if(z<=1.001){ox=0;oy=0;return}var mw=map.clientWidth*(z-1)/2,mh=map.clientHeight*(z-1)/2;ox=Math.max(-mw,Math.min(mw,ox));oy=Math.max(-mh,Math.min(mh,oy))}
  /* Zoom controls */
  Q('[data-zm]',map).forEach(function(b){b.onclick=function(){var v=+b.dataset.zm;if(v===0){z=1;ox=0;oy=0}else{z=Math.max(minZ,Math.min(maxZ,z+v*0.4))}apply()}});
  /* Wheel zoom */
  map.addEventListener('wheel',function(e){e.preventDefault();z=Math.max(minZ,Math.min(maxZ,z-e.deltaY*0.001));clamp();apply()},{passive:false});
  /* Mouse drag — you can start a drag on a region border or a pin, so remember where
     the pointer went down and swallow the click that follows a real drag: panning the
     map must never follow a link. */
  map.addEventListener('mousedown',function(e){sx=e.clientX;sy=e.clientY;moved=false;if(e.target.closest('.myth-pin,.myth-map__zoom'))return;dragging=true;lastX=e.clientX;lastY=e.clientY;e.preventDefault()});
  document.addEventListener('mousemove',function(e){if(!dragging)return;if(Math.abs(e.clientX-sx)+Math.abs(e.clientY-sy)>6)moved=true;ox+=e.clientX-lastX;oy+=e.clientY-lastY;lastX=e.clientX;lastY=e.clientY;clamp();apply()});
  document.addEventListener('mouseup',function(){dragging=false});
  map.addEventListener('click',function(e){if(moved){e.preventDefault();e.stopPropagation();moved=false}},true);
  /* Touch pan + pinch-zoom */
  map.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY;moved=false;if(e.touches.length===2){lastDist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY)}else if(e.touches.length===1){lastX=e.touches[0].clientX;lastY=e.touches[0].clientY}},{passive:true});
  map.addEventListener('touchmove',function(e){if(Math.abs(e.touches[0].clientX-sx)+Math.abs(e.touches[0].clientY-sy)>8)moved=true;if(e.touches.length===2){var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);z=Math.max(minZ,Math.min(maxZ,z*(d/lastDist)));lastDist=d;clamp();apply()}else if(e.touches.length===1){ox+=e.touches[0].clientX-lastX;oy+=e.touches[0].clientY-lastY;lastX=e.touches[0].clientX;lastY=e.touches[0].clientY;clamp();apply()}e.preventDefault()},{passive:false});
  /* Pin tooltip edge-fitting */
  Q('.myth-pin',map).forEach(function(pin){var pop=pin.querySelector('.myth-pin__pop');if(!pop)return;
   function fit(){pop.style.setProperty('--nx','0px');var r=pop.getBoundingClientRect(),mr=map.getBoundingClientRect(),dx=0;if(r.left<mr.left+8)dx=mr.left+8-r.left;else if(r.right>mr.right-8)dx=mr.right-8-r.right;pop.style.setProperty('--nx',dx+'px')}
   pin.addEventListener('mouseenter',fit);pin.addEventListener('focusin',fit)});
  /* Region descriptions: keep the tooltip inside the frame, horizontally and vertically */
  Q('.myth-region',map).forEach(function(rg){var pop=rg.querySelector('.myth-region__pop'),hit=rg.querySelector('.myth-region__hit');if(!pop||!hit)return;
   function fit(){pop.style.setProperty('--nx','0px');pop.style.setProperty('--ny','0px');
    var r=pop.getBoundingClientRect(),mr=map.getBoundingClientRect(),dx=0,dy=0;
    if(r.left<mr.left+8)dx=mr.left+8-r.left;else if(r.right>mr.right-8)dx=mr.right-8-r.right;
    if(r.top<mr.top+8)dy=mr.top+8-r.top;else if(r.bottom>mr.bottom-8)dy=mr.bottom-8-r.bottom;
    pop.style.setProperty('--nx',dx+'px');pop.style.setProperty('--ny',dy+'px')}
   hit.addEventListener('mouseenter',fit);rg.addEventListener('focusin',fit)});
  fit();
  if(bg&&bg.tagName.toLowerCase()==='img'){if(bg.complete&&bg.naturalWidth)fit();else bg.addEventListener('load',fit)}
  var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(fit,120)});
  if(window.ResizeObserver){new ResizeObserver(fit).observe(map)}/* refit if shown from a hidden tab */
  apply();
});
})();

/* ===== hero height comes from CSS (--hero-h): the same box on every page, so
   nothing is measured or stretched to the viewport here ===== */
