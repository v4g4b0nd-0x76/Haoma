(function(){
var D=document.documentElement,Q=function(s,r){return[].slice.call((r||document).querySelectorAll(s))},P={},fixed=D.hasAttribute('data-fixed')?D.dataset.culture:null;
try{P=JSON.parse(localStorage.getItem('prefs')||'{}')}catch(e){}
function save(){try{localStorage.setItem('prefs',JSON.stringify(P))}catch(e){}}
var act={
 nav:function(){P.nav=D.dataset.nav==='hidden'?'shown':'hidden';D.dataset.nav=P.nav;if(P.nav==='shown'){P.focus=false;D.dataset.focus='0'}},
 dock:function(){P.dock=D.dataset.dock==='end'?'start':'end';D.dataset.dock=P.dock},
 minus:function(){size(-.1)},plus:function(){size(.1)},
 focus:function(){P.focus=D.dataset.focus!=='1';D.dataset.focus=P.focus?'1':'0'}};
function size(d){P.size=Math.min(1.7,Math.max(1,Math.round(((P.size||1.2)+d)*100)/100));D.style.setProperty('--read',P.size+'rem')}
var hasSide=!!document.querySelector('aside.side');
Q('[data-act]').forEach(function(b){if(!hasSide&&/nav|dock/.test(b.dataset.act))b.hidden=true;b.onclick=function(){act[b.dataset.act]();save()}});
/* culture pick */
var sel=document.getElementById('culture-pick'),cine=Q('.cine')[0];
function opt(v){return sel&&sel.querySelector('option[value="'+v+'"]')}
function setPick(p,first){
 try{localStorage.setItem('culture',p)}catch(e){}
 var eff=fixed||p;D.dataset.pick=p;if(!fixed)D.dataset.culture=p;
 if(sel)sel.value=eff;
 Q('.pills button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.pick===p)});
 Q('.cards li[data-culture],.panel[data-culture]').forEach(function(e){e.hidden=eff!=='base'&&e.dataset.culture!==eff});
 if(cine){var sl=Q('.slide',cine),on=sl.filter(function(s){return s.dataset.culture===p})[0]||sl[0],q=Q('.quote',cine)[0],en=Q('.enter',cine)[0],o=opt(p);
  cine.dataset.culture=p;sl.forEach(function(s){s.classList.toggle('on',s===on)});
  var put=function(){q.innerHTML=on.querySelector('template').innerHTML;q.style.opacity=1};
  if(first)put();else{q.style.opacity=0;setTimeout(put,250)}
  en.hidden=p==='base';if(o)en.href=o.dataset.href}}
if(sel)sel.onchange=function(){var v=sel.value;setPick(v);if(fixed&&v!==fixed)location.href=opt(v).dataset.href};
Q('.pills button').forEach(function(b){b.onclick=function(){setPick(b.dataset.pick)}});
var p0='base';try{p0=localStorage.getItem('culture')||'base'}catch(e){}
if(!opt(p0)&&p0!=='base')p0='base';
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
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){var m=e.target,on=e.isIntersecting&&e.intersectionRatio>=.6;
 if(m.dataset.gif){if(on&&!m.dataset.on)m.src=m.dataset.gif;if(!on&&m.dataset.on)m.src=PH;m.dataset.on=on?'1':''}
 else if(on){var p=m.play();if(p&&p.catch)p.catch(function(){})}else m.pause()})},{threshold:[0,.6,1]});media.forEach(function(m){io.observe(m)})}
else media.forEach(function(m){if(m.dataset.gif)m.src=m.dataset.gif});
Q('.note').forEach(function(n){var p=n.querySelector('.note-pop');function fit(){p.style.setProperty('--nx','0px');var r=p.getBoundingClientRect(),w=document.documentElement.clientWidth,dx=0;if(r.left<8)dx=8-r.left;else if(r.right>w-8)dx=w-8-r.right;p.style.setProperty('--nx',dx+'px')}n.addEventListener('mouseenter',fit);n.addEventListener('focusin',fit)});
})();
