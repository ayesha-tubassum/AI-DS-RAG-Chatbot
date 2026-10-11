import React, { useEffect, useRef, useState } from 'react';

const SnakeAnimation: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number | null>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Disable on mobile and reduced-motion
    const mq = window.matchMedia('(max-width: 768px), (prefers-reduced-motion: reduce)');
    if (mq.matches) return;

    setActive(true);

    const handler = (e: MediaQueryListEvent) => {
      if (e.matches) {
        setActive(false);
        if (animRef.current) { cancelAnimationFrame(animRef.current); animRef.current = null; }
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

    const dpr = window.devicePixelRatio || 1;

    const resize = () => {
      const parent = canvas.parentElement;
      if (!parent) return;
      // Cover the first screen: full hero width, height of the first viewport
      const { width } = parent.getBoundingClientRect();
      const height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener('resize', resize);

    // Snake is a series of segments following a sinusoidal path
    const SEGMENTS = 40;
    const SEGMENT_LEN = 18;
    // Head position travels along a wave path
    let headX = 0;
    let last = 0;

    const draw = (now: number) => {
      const dt = Math.min(now - last, 64);
      last = now;

      const w = canvas.width / dpr;
      const h = canvas.height / dpr;
      ctx.clearRect(0, 0, w, h);

      // Advance head
      headX = (headX + dt * 0.04) % (w + SEGMENTS * SEGMENT_LEN);

      // Keep the head between 10% and 55% of the canvas (first screen) height
      const MIN_Y = 0.10;
      const MAX_Y = 0.55;
      const baseY = h * (MIN_Y + MAX_Y) / 2;
      const amplitude = h * (MAX_Y - MIN_Y) / 2;

      // Soft glow so the snake is clearly visible
      ctx.shadowColor = 'rgba(34,95,91,0.5)';
      ctx.shadowBlur = 12;

      // Draw snake body as connected circles (tail → head)
      for (let i = SEGMENTS; i >= 0; i--) {
        const sx = headX - i * SEGMENT_LEN;
        if (sx < -SEGMENT_LEN || sx > w + SEGMENT_LEN) continue;

        const sy = baseY + Math.sin((sx * 0.018) + (now * 0.001)) * amplitude;
        const progress = 1 - i / SEGMENTS; // 0 = tail, 1 = head
        const radius = 3 + progress * 5;
        const opacity = 0.22 + progress * 0.3;

        ctx.beginPath();
        ctx.arc(sx, sy, radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(34,95,91,${opacity})`;
        ctx.fill();
      }

      // Head dot
      const headY = baseY + Math.sin((headX * 0.018) + (now * 0.001)) * amplitude;
      ctx.beginPath();
      ctx.arc(headX, headY, 9, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(34,95,91,0.5)';
      ctx.fill();
      // Eyes (drawn without the glow)
      ctx.shadowBlur = 0;
      ctx.beginPath();
      ctx.arc(headX + 4, headY - 2, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255,255,255,0.7)';
      ctx.fill();

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
        top: 0,
        left: 0,
        width: '100%',
        height: '100vh',
        pointerEvents: 'none',
        display: 'block',
      }}
    />
  );
};

export default SnakeAnimation;