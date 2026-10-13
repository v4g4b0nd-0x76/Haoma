(function(){var D=document.documentElement,p='iranian',P={};try{p=localStorage.getItem('culture')||'iranian';P=JSON.parse(localStorage.getItem('prefs')||'{}')}catch(e){}
D.dataset.pick=p;if(!D.hasAttribute('data-fixed'))D.dataset.culture=p;
D.style.setProperty('--read',(P.size||1.2)+'rem');D.dataset.dock=P.dock||'start';D.dataset.nav=P.nav||'shown';D.dataset.focus=P.focus?'1':'0'})();
