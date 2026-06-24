/**
 * Habit Snowball — Particle System
 * 各階段粒子效果：雪花飄落、能量軌道、星雲塵埃
 * progress-aware: 隨階段內進度增加粒子數量與品質
 */

const ParticleSystem = (() => {
  let particles = [];
  let burstParticles = [];

  class Particle {
    constructor(x, y, opts = {}) {
      this.x = x;
      this.y = y;
      this.vx = opts.vx || (Math.random() - 0.5) * 2;
      this.vy = opts.vy || (Math.random() - 0.5) * 2;
      this.size = opts.size || Math.random() * 3 + 1;
      this.life = opts.life || 1;
      this.decay = opts.decay || 0.003 + Math.random() * 0.005;
      this.color = opts.color || '#ffffff';
      this.alpha = opts.alpha || 1;
      this.type = opts.type || 'default';
      this.angle = opts.angle || Math.random() * Math.PI * 2;
      this.angularSpeed = opts.angularSpeed || (Math.random() - 0.5) * 0.02;
      this.orbitRadius = opts.orbitRadius || 0;
      this.orbitCenterX = opts.orbitCenterX || x;
      this.orbitCenterY = opts.orbitCenterY || y;
      this.wobble = Math.random() * Math.PI * 2;
      this.wobbleSpeed = Math.random() * 0.03 + 0.01;
    }

    update() {
      this.life -= this.decay;

      switch (this.type) {
        case 'snow':
          this.x += Math.sin(this.wobble) * 0.5;
          this.y += this.vy;
          this.wobble += this.wobbleSpeed;
          this.angle += this.angularSpeed;
          break;

        case 'orbit':
          this.angle += this.angularSpeed;
          this.x = this.orbitCenterX + Math.cos(this.angle) * this.orbitRadius;
          this.y = this.orbitCenterY + Math.sin(this.angle) * this.orbitRadius;
          break;

        case 'nebula':
          this.x += this.vx * 0.3;
          this.y += this.vy * 0.3;
          this.angle += this.angularSpeed;
          this.size *= 0.999;
          break;

        case 'burst':
          this.x += this.vx;
          this.y += this.vy;
          this.vx *= 0.97;
          this.vy *= 0.97;
          this.size *= 0.98;
          break;

        case 'sparkle':
          this.x += this.vx * 0.5;
          this.y += this.vy * 0.5;
          this.alpha = Math.sin(this.life * Math.PI) * 0.8;
          break;

        default:
          this.x += this.vx;
          this.y += this.vy;
          break;
      }

      return this.life > 0 && this.size > 0.1;
    }

    draw(ctx) {
      ctx.save();
      ctx.globalAlpha = this.life * this.alpha;

      if (this.type === 'snow') {
        this.drawSnowflake(ctx);
      } else if (this.type === 'sparkle') {
        this.drawSparkle(ctx);
      } else {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.shadowBlur = this.size * 3;
        ctx.shadowColor = this.color;
        ctx.fill();
      }

      ctx.restore();
    }

    drawSnowflake(ctx) {
      ctx.translate(this.x, this.y);
      ctx.rotate(this.angle);
      ctx.strokeStyle = this.color;
      ctx.lineWidth = 0.8;
      ctx.shadowBlur = 4;
      ctx.shadowColor = this.color;

      const s = this.size;
      for (let i = 0; i < 6; i++) {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(s * 2, 0);
        if (s > 1.5) {
          ctx.moveTo(s, 0);
          ctx.lineTo(s * 1.4, -s * 0.6);
          ctx.moveTo(s, 0);
          ctx.lineTo(s * 1.4, s * 0.6);
        }
        ctx.stroke();
        ctx.rotate(Math.PI / 3);
      }
    }

    drawSparkle(ctx) {
      ctx.translate(this.x, this.y);
      ctx.fillStyle = this.color;
      ctx.shadowBlur = this.size * 4;
      ctx.shadowColor = this.color;

      const s = this.size;
      ctx.beginPath();
      for (let i = 0; i < 4; i++) {
        ctx.lineTo(0, -s * 2);
        ctx.lineTo(s * 0.5, -s * 0.5);
        ctx.rotate(Math.PI / 2);
      }
      ctx.fill();
    }
  }

  /**
   * Spawn ambient particles. Rate & quality scale with progress (0-1).
   */
  function spawnAmbient(stage, cx, cy, canvasW, canvasH, progress) {
    const p = progress || 0;
    // Spawn chance scales: 15% at 0 progress → 60% at full progress
    const spawnChance = 0.15 + p * 0.45;
    const count = Math.random() < spawnChance ? 1 : 0;
    // Sometimes spawn extra at high progress
    const extraCount = (p > 0.5 && Math.random() < (p - 0.5) * 0.6) ? 1 : 0;
    const total = count + extraCount;

    for (let i = 0; i < total; i++) {
      switch (stage.id) {
        case 'flake': {
          // More snowflakes, bigger, richer colors with progress
          const colors = ['#a8d8ea', '#bde0fe', '#d0e8ff', '#c2e7ff', '#89c4e8', '#6bb8d9'];
          const colorIndex = Math.floor(p * (colors.length - 1));
          const color = colors[Math.min(colorIndex + Math.floor(Math.random() * 2), colors.length - 1)];
          particles.push(new Particle(
            Math.random() * canvasW,
            -10,
            {
              type: 'snow',
              vy: Math.random() * 0.8 + 0.3,
              size: (Math.random() * 2 + 1) * (1 + p * 0.8),
              color: color,
              decay: 0.001,
              life: 1.5 + p * 0.5
            }
          ));
          break;
        }

        case 'ball': {
          const size = (Math.random() * 2 + 0.5) * (1 + p * 0.6);
          particles.push(new Particle(
            cx + (Math.random() - 0.5) * (80 + p * 60),
            cy + 60,
            {
              type: 'snow',
              vy: -Math.random() * 0.5 - 0.2,
              size: size,
              color: p > 0.5 ? '#c2e7ff' : '#e0f2fe',
              decay: 0.004
            }
          ));
          break;
        }

        case 'crystal': {
          const colors = ['#c084fc', '#f0abfc', '#e9d5ff', '#d8b4fe', '#a855f7'];
          particles.push(new Particle(
            cx, cy,
            {
              type: 'sparkle',
              vx: (Math.random() - 0.5) * (2 + p * 2),
              vy: (Math.random() - 0.5) * (2 + p * 2),
              size: (Math.random() * 2 + 1) * (1 + p * 0.5),
              color: colors[Math.floor(Math.random() * (2 + Math.floor(p * 3)))],
              decay: 0.006
            }
          ));
          break;
        }

        case 'energy': {
          const orbitR = (50 + Math.random() * 30) * (1 + p * 0.4);
          particles.push(new Particle(
            cx, cy,
            {
              type: 'orbit',
              orbitCenterX: cx,
              orbitCenterY: cy,
              orbitRadius: orbitR,
              angularSpeed: (Math.random() * 0.02 + 0.01) * (1 + p * 0.5) * (Math.random() > 0.5 ? 1 : -1),
              size: (Math.random() * 2 + 0.5) * (1 + p * 0.4),
              color: Math.random() > 0.5 ? stage.color1 : stage.color2,
              decay: 0.002
            }
          ));
          break;
        }

        case 'planet': {
          if (Math.random() < 0.4 + p * 0.2) {
            particles.push(new Particle(
              cx, cy,
              {
                type: 'orbit',
                orbitCenterX: cx,
                orbitCenterY: cy,
                orbitRadius: (60 + Math.random() * 20) * (1 + p * 0.3),
                angularSpeed: (0.004 + Math.random() * 0.004) * (1 + p * 0.5),
                size: (Math.random() * 1.5 + 0.5) * (1 + p * 0.3),
                color: p > 0.6 ? '#4ade80' : '#86efac',
                decay: 0.002
              }
            ));
          } else {
            particles.push(new Particle(
              Math.random() * canvasW,
              Math.random() * canvasH,
              {
                type: 'sparkle',
                vx: 0, vy: 0,
                size: Math.random() * (1 + p) + 0.5,
                color: '#ffffff',
                decay: 0.004,
                alpha: 0.4 + p * 0.3
              }
            ));
          }
          break;
        }

        case 'star': {
          const angle = Math.random() * Math.PI * 2;
          const dist = (35 + Math.random() * 15) * (1 + p * 0.3);
          const speed = (Math.random() * 1.5 + 0.5) * (1 + p * 0.5);
          particles.push(new Particle(
            cx + Math.cos(angle) * dist,
            cy + Math.sin(angle) * dist,
            {
              type: 'default',
              vx: Math.cos(angle) * speed,
              vy: Math.sin(angle) * speed,
              size: (Math.random() * 2.5 + 1) * (1 + p * 0.4),
              color: Math.random() > 0.3 ? stage.color1 : (p > 0.5 ? '#fb923c' : stage.color2),
              decay: 0.008
            }
          ));
          break;
        }

        case 'galaxy': {
          const armAngle = Math.random() * Math.PI * 2;
          const armDist = (20 + Math.random() * 60) * (1 + p * 0.5);
          const spiralOffset = armAngle + armDist * 0.02;
          const colors = [stage.color1, stage.color2, '#fbbf24', '#f0abfc', '#60a5fa', '#34d399'];
          particles.push(new Particle(
            cx + Math.cos(spiralOffset) * armDist,
            cy + Math.sin(spiralOffset) * armDist * 0.6,
            {
              type: 'nebula',
              vx: (Math.random() - 0.5) * 0.3,
              vy: (Math.random() - 0.5) * 0.3,
              angularSpeed: 0.01,
              size: (Math.random() * 2 + 0.5) * (1 + p * 0.5),
              color: colors[Math.floor(Math.random() * (3 + Math.floor(p * 3)))],
              decay: 0.001
            }
          ));
          break;
        }
      }
    }
  }

  function spawnBurst(cx, cy, color, count = 30, isPositive = true) {
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
      const speed = Math.random() * 5 + 2;
      burstParticles.push(new Particle(cx, cy, {
        type: 'burst',
        vx: Math.cos(angle) * speed * (isPositive ? 1 : 0.6),
        vy: Math.sin(angle) * speed * (isPositive ? 1 : 0.6),
        size: Math.random() * 4 + 1,
        color: color,
        decay: 0.015 + Math.random() * 0.01,
        life: 1
      }));
    }
  }

  function spawnCelebration(cx, cy, canvasW, canvasH) {
    const colors = ['#fbbf24', '#f472b6', '#34d399', '#60a5fa', '#c084fc', '#f59e0b'];
    for (let i = 0; i < 80; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 8 + 3;
      burstParticles.push(new Particle(cx, cy, {
        type: 'burst',
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 2,
        size: Math.random() * 5 + 2,
        color: colors[Math.floor(Math.random() * colors.length)],
        decay: 0.008,
        life: 1.5
      }));
    }
  }

  function update() {
    particles = particles.filter(p => p.update());
    burstParticles = burstParticles.filter(p => p.update());
  }

  function draw(ctx) {
    particles.forEach(p => p.draw(ctx));
    burstParticles.forEach(p => p.draw(ctx));
  }

  function clear() {
    particles = [];
    burstParticles = [];
  }

  function getCount() {
    return particles.length + burstParticles.length;
  }

  return {
    spawnAmbient,
    spawnBurst,
    spawnCelebration,
    update,
    draw,
    clear,
    getCount
  };
})();
