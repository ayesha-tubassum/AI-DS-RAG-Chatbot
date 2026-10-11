import React, { useEffect, useRef, useState } from 'react';

const ParticleCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number | null>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Disable on mobile (≤ 768px) and reduced-motion
    const mq = window.matchMedia('(max-width: 768px), (prefers-reduced-motion: reduce)');
    if (mq.matches) return;

    setActive(true);

    const handler = (e: MediaQueryListEvent) => {
      if (e.matches) {
        setActive(false);
        if (animRef.current) {
          cancelAnimationFrame(animRef.current);
          animRef.current = null;
        }
      }
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    if (!active) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // ── Particle color constants — change these to restyle the effect ──
    // Dark mode: bright mint so dots show on the dark hero background
    const COLOR_DARK  = '140,235,225';
    // Light mode: deep teal so dots remain visible on the light background
    const COLOR_LIGHT = '20,110,105';

    const getColor = () =>
      document.documentElement.dataset.theme === 'dark' ? COLOR_DARK : COLOR_LIGHT;

    const dpr = window.devicePixelRatio || 1;

    const resize = () => {
      const parent = canvas.parentElement;
      if (!parent) return;
      const { width, height } = parent.getBoundingClientRect();
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener('resize', resize);

    interface Particle { x: number; y: number; vx: number; vy: number; r: number }
    const W = () => canvas.width / dpr;
    const H = () => canvas.height / dpr;

    // Scale dot count with canvas area; cap at 110
    const baseCount = Math.min(110, Math.round((W() * H()) / 12000) + 90);

    const particles: Particle[] = Array.from({ length: baseCount }, () => ({
      x: Math.random() * W(),
      y: Math.random() * H(),
      vx: (Math.random() - 0.5) * 0.364,
      vy: (Math.random() - 0.5) * 0.364,
      r: Math.random() * 2.4 + 1.2,
    }));

    let last = 0;
    const draw = (now: number) => {
      const dt = Math.min(now - last, 64); // cap delta to avoid huge jumps
      last = now;

      const w = W();
      const h = H();
      ctx.clearRect(0, 0, w, h);

      const col = getColor();

      // Dots with soft glow
      ctx.shadowBlur = 8;
      ctx.shadowColor = `rgba(${col},0.6)`;
      for (const p of particles) {
        p.x = (p.x + p.vx * dt * 0.06 + w) % w;
        p.y = (p.y + p.vy * dt * 0.06 + h) % h;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${col},0.75)`;
        ctx.fill();
      }

      // Neural-network lines (no glow on lines — keeps them clean)
      ctx.shadowBlur = 0;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(${col},${(1 - d / 150) * 0.35})`;
            ctx.lineWidth = 1.1;
            ctx.stroke();
          }
        }
      }

      animRef.current = requestAnimationFrame(draw);
    };

    animRef.current = requestAnimationFrame(draw);

    const onVisibility = () => {
      if (document.hidden) {
        if (animRef.current) { cancelAnimationFrame(animRef.current); animRef.current = null; }
      } else {
        last = performance.now();
        animRef.current = requestAnimationFrame(draw);
      }
    };
    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      window.removeEventListener('resize', resize);
      document.removeEventListener('visibilitychange', onVisibility);
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [active]);

  if (!active) return null;

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        display: 'block',
      }}
    />
  );
};

export default ParticleCanvas;