// particles.js - ambient background particles
(function(){
    const canvas = document.getElementById('particleCanvas');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const particles = Array.from({length:40},()=>({
      x: Math.random()*canvas.width, y: Math.random()*canvas.height,
      r: Math.random()*2+1, vx:(Math.random()-.5)*.4, vy:(Math.random()-.5)*.4,
      a: Math.random()*.4+.1
    }));
    function draw(){
      ctx.clearRect(0,0,canvas.width,canvas.height);
      particles.forEach(p=>{
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle='rgba(139,92,246,'+p.a+')'; ctx.fill();
        p.x+=p.vx; p.y+=p.vy;
        if(p.x<0||p.x>canvas.width) p.vx*=-1;
        if(p.y<0||p.y>canvas.height) p.vy*=-1;
      });
      requestAnimationFrame(draw);
    }
    draw();
    window.addEventListener('resize',()=>{canvas.width=window.innerWidth;canvas.height=window.innerHeight;});
  })();