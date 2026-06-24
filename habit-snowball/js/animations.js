/**
 * Habit Snowball — UI Animations
 * 加分/扣分動畫、數字飛入、慶祝特效
 */

const Animations = (() => {

  /**
   * 分數飛入動畫
   */
  function flyScore(containerEl, points, color) {
    const el = document.createElement('div');
    el.className = 'fly-score';
    el.textContent = (points > 0 ? '+' : '') + points;
    el.style.color = color || (points > 0 ? '#34d399' : '#ef4444');

    const rect = containerEl.getBoundingClientRect();
    el.style.left = (rect.width / 2) + 'px';
    el.style.top = '50%';

    containerEl.appendChild(el);

    requestAnimationFrame(() => {
      el.classList.add('animate');
    });

    setTimeout(() => el.remove(), 1500);
  }

  /**
   * 數字跳動動畫（計數器效果）
   */
  function countUp(el, from, to, duration = 800) {
    const start = performance.now();
    const diff = to - from;

    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(from + diff * eased);
      el.textContent = current.toLocaleString();

      if (progress < 1) {
        requestAnimationFrame(tick);
      }
    }

    requestAnimationFrame(tick);
  }

  /**
   * 元素震動效果
   */
  function shake(el, intensity = 5) {
    el.style.animation = 'none';
    el.offsetHeight; // trigger reflow
    el.style.animation = `shake ${intensity > 5 ? '0.6s' : '0.4s'} ease-out`;
    setTimeout(() => { el.style.animation = ''; }, 600);
  }

  /**
   * 脈衝光暈效果
   */
  function glowPulse(el, color, duration = 800) {
    el.style.boxShadow = `0 0 30px ${color}, 0 0 60px ${color}40`;
    setTimeout(() => {
      el.style.transition = `box-shadow ${duration}ms ease-out`;
      el.style.boxShadow = '';
      setTimeout(() => { el.style.transition = ''; }, duration);
    }, 50);
  }

  /**
   * 新項目滑入
   */
  function slideIn(el, direction = 'bottom') {
    el.style.opacity = '0';
    el.style.transform = direction === 'bottom'
      ? 'translateY(20px)' : 'translateX(-20px)';

    requestAnimationFrame(() => {
      el.style.transition = 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
      el.style.opacity = '1';
      el.style.transform = 'translateY(0) translateX(0)';
      setTimeout(() => { el.style.transition = ''; }, 500);
    });
  }

  /**
   * Toast notification
   */
  function toast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${message}</span>`;

    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, duration);
  }

  function createToastContainer() {
    const c = document.createElement('div');
    c.id = 'toast-container';
    document.body.appendChild(c);
    return c;
  }

  /**
   * Stage up celebration overlay
   */
  function stageUpCelebration(stageName, emoji) {
    const overlay = document.createElement('div');
    overlay.className = 'celebration-overlay';
    overlay.innerHTML = `
      <div class="celebration-content">
        <div class="celebration-emoji">${emoji}</div>
        <div class="celebration-text">階段提升！</div>
        <div class="celebration-stage">${stageName}</div>
      </div>
    `;

    document.body.appendChild(overlay);
    requestAnimationFrame(() => overlay.classList.add('show'));

    setTimeout(() => {
      overlay.classList.remove('show');
      setTimeout(() => overlay.remove(), 600);
    }, 2500);
  }

  return {
    flyScore,
    countUp,
    shake,
    glowPulse,
    slideIn,
    toast,
    stageUpCelebration
  };
})();
