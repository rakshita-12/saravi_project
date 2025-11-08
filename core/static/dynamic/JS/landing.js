// LINES + DOTS BACKGROUND (full-page, behind content)
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');

let W = innerWidth;
let H = innerHeight;
canvas.width = W;
canvas.height = H;

window.addEventListener('resize', () => {
  W = innerWidth; H = innerHeight;
  canvas.width = W; canvas.height = H;
  initParticles();
});

const PARTICLE_COUNT = Math.max(60, Math.floor((W * H) / 150000));
const CONNECT_DIST = 140;
let particles = [];

function rand(min, max) { return Math.random() * (max - min) + min; }

function initParticles() {
  particles = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: rand(-0.4, 0.4),
      vy: rand(-0.4, 0.4),
      r: rand(0.8, 1.8),
      c: Math.random() > 0.5 ? '#8b5cf6' : '#06b6d4'
    });
  }
}
initParticles();

let mouse = { x: null, y: null, active: false };
window.addEventListener('mousemove', (e) => { mouse.x = e.clientX; mouse.y = e.clientY; mouse.active = true; });
window.addEventListener('mouseout', () => { mouse.active = false; mouse.x = null; mouse.y = null; });

function draw() {
  ctx.clearRect(0, 0, W, H);

  // particles
  for (const p of particles) {
    // slight attraction to mouse
    if (mouse.active && mouse.x !== null) {
      const dx = mouse.x - p.x, dy = mouse.y - p.y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < 200) {
        p.vx += (dx / dist) * 0.0007;
        p.vy += (dy / dist) * 0.0007;
      }
    } else {
      p.vx += (Math.random()-0.5)*0.0003;
      p.vy += (Math.random()-0.5)*0.0003;
    }

    p.vx = Math.max(-1.2, Math.min(1.2, p.vx));
    p.vy = Math.max(-1.2, Math.min(1.2, p.vy));
    p.x += p.vx; p.y += p.vy;

    if (p.x < 0) { p.x = 0; p.vx *= -1; }
    if (p.x > W) { p.x = W; p.vx *= -1; }
    if (p.y < 0) { p.y = 0; p.vy *= -1; }
    if (p.y > H) { p.y = H; p.vy *= -1; }

    ctx.beginPath();
    ctx.fillStyle = p.c === '#8b5cf6' ? 'rgba(139,92,246,0.9)' : 'rgba(6,182,212,0.95)';
    ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
    ctx.fill();
  }

  // lines
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const a = particles[i], b = particles[j];
      const dx = a.x - b.x, dy = a.y - b.y;
      const d = Math.sqrt(dx*dx + dy*dy);
      if (d < CONNECT_DIST) {
        const alpha = 1 - d / CONNECT_DIST;
        ctx.strokeStyle = (j % 2 === 0) ? `rgba(139,92,246,${alpha*0.35})` : `rgba(6,182,212,${alpha*0.35})`;
        ctx.lineWidth = 0.8;
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
    }
  }

  requestAnimationFrame(draw);
}
draw();

// smooth scroll for nav links
document.querySelectorAll('.nav-links a[href^="#"]').forEach(a=>{
  a.addEventListener('click', e=>{
    e.preventDefault();
    const target = document.querySelector(a.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior:'smooth', block:'start' });
  });
});
