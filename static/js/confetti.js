// confetti.js - standalone trigger
window.triggerConfetti = function(){
    const colors=['#f43f5e','#8b5cf6','#06b6d4','#22c55e','#f59e0b','#ec4899'];
    for(let i=0;i<80;i++){
      const c=document.createElement('div');
      c.className='confetti';
      c.style.cssText='position:fixed;top:-10px;width:'+(6+Math.random()*8)+'px;height:'+(6+Math.random()*8)+'px;left:'+Math.random()*100+'vw;animation-delay:'+Math.random()*2+'s;background:'+colors[Math.floor(Math.random()*colors.length)]+';border-radius:'+(Math.random()>.5?'50%':'2px')+';animation:confettiFall 3s ease-in forwards;z-index:9999;';
      document.body.appendChild(c);
      setTimeout(()=>c.remove(),3500);
    }
  };