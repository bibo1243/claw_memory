/**
 * Habit Snowball — Canvas Snowball Visualization
 * 雪球成長視覺化：7 個進化階段，每個都有獨特的繪製邏輯
 */

const SnowballVis = (() => {
  let canvas, ctx;
  let animFrame;
  let time = 0;
  let currentStage = null;
  let targetScale = 1;
  let currentScale = 1;
  let glowIntensity = 0;
  let isTransitioning = false;
  let transitionProgress = 0;
  let prevStageId = null;
  let currentPoints = 0;

  function init(canvasEl) {
    canvas = canvasEl;
    ctx = canvas.getContext('2d');
    resize();
    window.addEventListener('resize', resize);
  }

  function resize() {
    const container = canvas.parentElement;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = container.clientWidth * dpr;
    canvas.height = container.clientHeight * dpr;
    canvas.style.width = container.clientWidth + 'px';
    canvas.style.height = container.clientHeight + 'px';
    ctx.scale(dpr, dpr);
  }

  function getCenter() {
    const w = canvas.width / (window.devicePixelRatio || 1);
    const h = canvas.height / (window.devicePixelRatio || 1);
    return { x: w / 2, y: h / 2, w, h };
  }

  function setStage(stage) {
    if (currentStage && currentStage.id !== stage.id) {
      prevStageId = currentStage.id;
      isTransitioning = true;
      transitionProgress = 0;
    }
    currentStage = stage;
  }

  function pulse(scale = 1.15) {
    targetScale = scale;
    setTimeout(() => { targetScale = 1; }, 300);
  }

  function shrink() {
    targetScale = 0.85;
    setTimeout(() => { targetScale = 1; }, 400);
  }

  // ---------- Stage-specific drawing functions ----------

  function drawFlake(cx, cy, progress) {
    const baseSize = 30 + progress * 20;
    const s = baseSize * currentScale;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(time * 0.005);

    // Main snowflake
    ctx.strokeStyle = currentStage.color1;
    ctx.lineWidth = 2;
    ctx.shadowBlur = 15 + Math.sin(time * 0.02) * 5;
    ctx.shadowColor = currentStage.color2;
    ctx.globalAlpha = 0.9;

    for (let i = 0; i < 6; i++) {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(s, 0);
      // Branch
      ctx.moveTo(s * 0.5, 0);
      ctx.lineTo(s * 0.7, -s * 0.3);
      ctx.moveTo(s * 0.5, 0);
      ctx.lineTo(s * 0.7, s * 0.3);
      // Tip branch
      ctx.moveTo(s * 0.75, 0);
      ctx.lineTo(s * 0.9, -s * 0.2);
      ctx.moveTo(s * 0.75, 0);
      ctx.lineTo(s * 0.9, s * 0.2);
      ctx.stroke();
      ctx.rotate(Math.PI / 3);
    }

    // Center glow
    const grd = ctx.createRadialGradient(0, 0, 0, 0, 0, s * 0.3);
    grd.addColorStop(0, 'rgba(168, 216, 234, 0.4)');
    grd.addColorStop(1, 'rgba(168, 216, 234, 0)');
    ctx.fillStyle = grd;
    ctx.beginPath();
    ctx.arc(0, 0, s * 0.3, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  function drawBall(cx, cy, progress) {
    const r = (35 + progress * 20) * currentScale;

    ctx.save();

    // Shadow on ground
    ctx.fillStyle = 'rgba(147, 197, 253, 0.1)';
    ctx.beginPath();
    ctx.ellipse(cx, cy + r + 10, r * 0.8, r * 0.2, 0, 0, Math.PI * 2);
    ctx.fill();

    // Main ball
    const grd = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r);
    grd.addColorStop(0, '#f0f9ff');
    grd.addColorStop(0.5, '#bae6fd');
    grd.addColorStop(1, '#7dd3fc');

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.shadowBlur = 20;
    ctx.shadowColor = 'rgba(147, 197, 253, 0.5)';
    ctx.fill();

    // Specular highlight
    ctx.beginPath();
    ctx.arc(cx - r * 0.25, cy - r * 0.25, r * 0.3, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.fill();

    // Snow texture dots
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    for (let i = 0; i < 8; i++) {
      const a = (Math.PI * 2 * i) / 8 + time * 0.003;
      const d = r * 0.5 + Math.sin(time * 0.01 + i) * r * 0.1;
      ctx.beginPath();
      ctx.arc(cx + Math.cos(a) * d, cy + Math.sin(a) * d, 2, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }

  function drawCrystal(cx, cy, progress) {
    const r = (40 + progress * 20) * currentScale;

    ctx.save();

    // Outer glow
    const glowGrd = ctx.createRadialGradient(cx, cy, r * 0.5, cx, cy, r * 1.5);
    glowGrd.addColorStop(0, 'rgba(192, 132, 252, 0.15)');
    glowGrd.addColorStop(1, 'rgba(192, 132, 252, 0)');
    ctx.fillStyle = glowGrd;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 1.5, 0, Math.PI * 2);
    ctx.fill();

    // Crystal ball
    const grd = ctx.createRadialGradient(cx - r * 0.2, cy - r * 0.2, 0, cx, cy, r);
    grd.addColorStop(0, 'rgba(240, 171, 252, 0.8)');
    grd.addColorStop(0.4, 'rgba(192, 132, 252, 0.6)');
    grd.addColorStop(0.8, 'rgba(139, 92, 246, 0.4)');
    grd.addColorStop(1, 'rgba(109, 40, 217, 0.3)');

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.shadowBlur = 30;
    ctx.shadowColor = 'rgba(192, 132, 252, 0.5)';
    ctx.fill();

    // Internal light swirls
    for (let i = 0; i < 3; i++) {
      const a = time * 0.008 + (Math.PI * 2 * i) / 3;
      const d = r * 0.4;
      const sx = cx + Math.cos(a) * d;
      const sy = cy + Math.sin(a) * d;
      const lightGrd = ctx.createRadialGradient(sx, sy, 0, sx, sy, r * 0.3);
      lightGrd.addColorStop(0, 'rgba(240, 171, 252, 0.4)');
      lightGrd.addColorStop(1, 'rgba(240, 171, 252, 0)');
      ctx.beginPath();
      ctx.arc(sx, sy, r * 0.3, 0, Math.PI * 2);
      ctx.fillStyle = lightGrd;
      ctx.fill();
    }

    // Specular
    ctx.beginPath();
    ctx.arc(cx - r * 0.3, cy - r * 0.3, r * 0.2, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.fill();

    ctx.restore();
  }

  function drawEnergy(cx, cy, progress) {
    const r = (45 + progress * 20) * currentScale;
    const pulse = Math.sin(time * 0.03) * 5;

    ctx.save();

    // Pulsing glow rings
    for (let ring = 3; ring >= 1; ring--) {
      const ringR = r + ring * 15 + pulse;
      ctx.beginPath();
      ctx.arc(cx, cy, ringR, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(245, 158, 11, ${0.1 / ring})`;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Energy core
    const grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, r + pulse);
    grd.addColorStop(0, '#fef3c7');
    grd.addColorStop(0.3, '#fbbf24');
    grd.addColorStop(0.6, '#f59e0b');
    grd.addColorStop(1, '#dc2626');

    ctx.beginPath();
    ctx.arc(cx, cy, r + pulse, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.shadowBlur = 40 + pulse * 2;
    ctx.shadowColor = '#f59e0b';
    ctx.fill();

    // Energy streams
    ctx.lineWidth = 2;
    for (let i = 0; i < 5; i++) {
      const a = time * 0.015 + (Math.PI * 2 * i) / 5;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(a) * r * 0.3, cy + Math.sin(a) * r * 0.3);
      const cp1x = cx + Math.cos(a + 0.5) * r * 0.7;
      const cp1y = cy + Math.sin(a + 0.5) * r * 0.7;
      const ex = cx + Math.cos(a + 1) * (r + 10);
      const ey = cy + Math.sin(a + 1) * (r + 10);
      ctx.quadraticCurveTo(cp1x, cp1y, ex, ey);
      ctx.strokeStyle = `rgba(251, 191, 36, ${0.4 + Math.sin(time * 0.05 + i) * 0.2})`;
      ctx.stroke();
    }

    ctx.restore();
  }

  function drawPlanet(cx, cy, progress) {
    const r = (50 + progress * 20) * currentScale;

    ctx.save();

    // Atmosphere glow
    const atmoGrd = ctx.createRadialGradient(cx, cy, r * 0.8, cx, cy, r * 1.3);
    atmoGrd.addColorStop(0, 'rgba(52, 211, 153, 0)');
    atmoGrd.addColorStop(0.5, 'rgba(52, 211, 153, 0.1)');
    atmoGrd.addColorStop(1, 'rgba(52, 211, 153, 0)');
    ctx.fillStyle = atmoGrd;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 1.3, 0, Math.PI * 2);
    ctx.fill();

    // Planet body
    const grd = ctx.createRadialGradient(cx - r * 0.2, cy - r * 0.2, 0, cx, cy, r);
    grd.addColorStop(0, '#6ee7b7');
    grd.addColorStop(0.4, '#34d399');
    grd.addColorStop(0.7, '#059669');
    grd.addColorStop(1, '#064e3b');

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.shadowBlur = 25;
    ctx.shadowColor = 'rgba(52, 211, 153, 0.4)';
    ctx.fill();

    // Surface features (continents)
    ctx.globalCompositeOperation = 'overlay';
    for (let i = 0; i < 4; i++) {
      const angle = time * 0.003 + (Math.PI * 2 * i) / 4;
      const px = cx + Math.cos(angle) * r * 0.4;
      const py = cy + Math.sin(angle) * r * 0.3;
      const pGrd = ctx.createRadialGradient(px, py, 0, px, py, r * 0.3);
      pGrd.addColorStop(0, 'rgba(16, 185, 129, 0.4)');
      pGrd.addColorStop(1, 'rgba(16, 185, 129, 0)');
      ctx.beginPath();
      ctx.arc(px, py, r * 0.3, 0, Math.PI * 2);
      ctx.fillStyle = pGrd;
      ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';

    // Cloud wisps
    ctx.globalAlpha = 0.25;
    for (let i = 0; i < 3; i++) {
      const cAngle = time * 0.005 + (Math.PI * 2 * i) / 3;
      const cX = cx + Math.cos(cAngle) * r * 0.5;
      const cY = cy + Math.sin(cAngle) * r * 0.2;
      ctx.beginPath();
      ctx.ellipse(cX, cY, r * 0.3, r * 0.08, cAngle, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    // Highlight
    ctx.beginPath();
    ctx.arc(cx - r * 0.3, cy - r * 0.3, r * 0.25, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.fill();

    ctx.restore();
  }

  function drawStar(cx, cy, progress) {
    const r = (50 + progress * 25) * currentScale;
    const pulse = Math.sin(time * 0.04) * 8;

    ctx.save();

    // Corona / rays
    for (let i = 0; i < 12; i++) {
      const a = (Math.PI * 2 * i) / 12 + time * 0.002;
      const rayLen = r * 1.5 + Math.sin(time * 0.05 + i) * 20;
      const grd = ctx.createLinearGradient(
        cx + Math.cos(a) * r * 0.5,
        cy + Math.sin(a) * r * 0.5,
        cx + Math.cos(a) * rayLen,
        cy + Math.sin(a) * rayLen
      );
      grd.addColorStop(0, 'rgba(251, 191, 36, 0.4)');
      grd.addColorStop(1, 'rgba(251, 191, 36, 0)');

      ctx.beginPath();
      ctx.moveTo(
        cx + Math.cos(a - 0.05) * r * 0.8,
        cy + Math.sin(a - 0.05) * r * 0.8
      );
      ctx.lineTo(
        cx + Math.cos(a) * rayLen,
        cy + Math.sin(a) * rayLen
      );
      ctx.lineTo(
        cx + Math.cos(a + 0.05) * r * 0.8,
        cy + Math.sin(a + 0.05) * r * 0.8
      );
      ctx.fillStyle = grd;
      ctx.fill();
    }

    // Outer glow
    const glowGrd = ctx.createRadialGradient(cx, cy, r * 0.3, cx, cy, r * 2);
    glowGrd.addColorStop(0, 'rgba(251, 191, 36, 0.3)');
    glowGrd.addColorStop(0.5, 'rgba(244, 114, 182, 0.1)');
    glowGrd.addColorStop(1, 'rgba(244, 114, 182, 0)');
    ctx.fillStyle = glowGrd;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 2, 0, Math.PI * 2);
    ctx.fill();

    // Star body
    const starGrd = ctx.createRadialGradient(cx, cy, 0, cx, cy, r + pulse);
    starGrd.addColorStop(0, '#fffbeb');
    starGrd.addColorStop(0.2, '#fef3c7');
    starGrd.addColorStop(0.5, '#fbbf24');
    starGrd.addColorStop(0.8, '#f59e0b');
    starGrd.addColorStop(1, '#f472b6');

    ctx.beginPath();
    ctx.arc(cx, cy, r + pulse, 0, Math.PI * 2);
    ctx.fillStyle = starGrd;
    ctx.shadowBlur = 60;
    ctx.shadowColor = '#fbbf24';
    ctx.fill();

    // Surface turbulence
    ctx.globalCompositeOperation = 'soft-light';
    for (let i = 0; i < 5; i++) {
      const a = time * 0.01 + i * 1.2;
      const tx = cx + Math.cos(a) * r * 0.4;
      const ty = cy + Math.sin(a) * r * 0.4;
      const tGrd = ctx.createRadialGradient(tx, ty, 0, tx, ty, r * 0.4);
      tGrd.addColorStop(0, 'rgba(255, 255, 255, 0.3)');
      tGrd.addColorStop(1, 'rgba(255, 255, 255, 0)');
      ctx.beginPath();
      ctx.arc(tx, ty, r * 0.4, 0, Math.PI * 2);
      ctx.fillStyle = tGrd;
      ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';

    ctx.restore();
  }

  function drawGalaxy(cx, cy, progress) {
    const baseR = (55 + progress * 25) * currentScale;

    ctx.save();

    // Outer nebula glow
    const nebulaGrd = ctx.createRadialGradient(cx, cy, 0, cx, cy, baseR * 2);
    nebulaGrd.addColorStop(0, 'rgba(139, 92, 246, 0.15)');
    nebulaGrd.addColorStop(0.5, 'rgba(6, 182, 212, 0.08)');
    nebulaGrd.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = nebulaGrd;
    ctx.beginPath();
    ctx.arc(cx, cy, baseR * 2, 0, Math.PI * 2);
    ctx.fill();

    // Spiral arms
    const arms = 2;
    const totalDots = 200;
    const rotation = time * 0.002;

    for (let arm = 0; arm < arms; arm++) {
      const armOffset = (Math.PI * 2 * arm) / arms;

      for (let i = 0; i < totalDots; i++) {
        const t = i / totalDots;
        const angle = armOffset + t * Math.PI * 3 + rotation;
        const dist = t * baseR * 1.5;
        const scatter = (Math.random() - 0.5) * 15 * t;

        const x = cx + Math.cos(angle) * dist + scatter;
        const y = cy + Math.sin(angle) * dist * 0.6 + scatter * 0.6;

        const alpha = (1 - t) * 0.8;
        const size = (1 - t) * 2.5 + 0.5;

        const colorMix = t;
        const r = Math.floor(139 * (1 - colorMix) + 6 * colorMix);
        const g = Math.floor(92 * (1 - colorMix) + 182 * colorMix);
        const b = Math.floor(246 * (1 - colorMix) + 212 * colorMix);

        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        ctx.fill();
      }
    }

    // Central core
    const coreGrd = ctx.createRadialGradient(cx, cy, 0, cx, cy, baseR * 0.4);
    coreGrd.addColorStop(0, 'rgba(255, 255, 255, 0.9)');
    coreGrd.addColorStop(0.3, 'rgba(251, 191, 36, 0.6)');
    coreGrd.addColorStop(0.6, 'rgba(192, 132, 252, 0.3)');
    coreGrd.addColorStop(1, 'rgba(139, 92, 246, 0)');

    ctx.beginPath();
    ctx.arc(cx, cy, baseR * 0.4, 0, Math.PI * 2);
    ctx.fillStyle = coreGrd;
    ctx.shadowBlur = 40;
    ctx.shadowColor = 'rgba(192, 132, 252, 0.5)';
    ctx.fill();

    ctx.restore();
  }

  // ---------- Main render loop ----------

  function render() {
    if (!canvas || !ctx || !currentStage) return;

    const { x: cx, y: cy, w, h } = getCenter();

    // Clear
    ctx.clearRect(0, 0, w, h);

    // Smooth scale interpolation
    currentScale += (targetScale - currentScale) * 0.1;

    // Transition
    if (isTransitioning) {
      transitionProgress += 0.02;
      if (transitionProgress >= 1) {
        isTransitioning = false;
        transitionProgress = 0;
      }
    }

    // Calculate stage progress
    const progress = ScoringEngine.getStageProgress(currentPoints) / 100;

    // Draw stage
    switch (currentStage.id) {
      case 'flake':   drawFlake(cx, cy, progress); break;
      case 'ball':    drawBall(cx, cy, progress); break;
      case 'crystal': drawCrystal(cx, cy, progress); break;
      case 'energy':  drawEnergy(cx, cy, progress); break;
      case 'planet':  drawPlanet(cx, cy, progress); break;
      case 'star':    drawStar(cx, cy, progress); break;
      case 'galaxy':  drawGalaxy(cx, cy, progress); break;
    }

    // Spawn & draw particles
    ParticleSystem.spawnAmbient(currentStage, cx, cy, w, h, progress);
    ParticleSystem.update();
    ParticleSystem.draw(ctx);

    time++;
    animFrame = requestAnimationFrame(render);
  }

  function start() {
    if (animFrame) cancelAnimationFrame(animFrame);
    render();
  }

  function stop() {
    if (animFrame) cancelAnimationFrame(animFrame);
  }

  return {
    init,
    start,
    stop,
    setStage,
    setPoints: function(pts) { currentPoints = pts; },
    pulse,
    shrink,
    resize,
    getCenter
  };
})();
