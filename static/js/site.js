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
