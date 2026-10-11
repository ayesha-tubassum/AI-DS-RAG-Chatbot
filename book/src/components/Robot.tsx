import React from 'react';

/**
 * Friendly flat-style robot in inline SVG.
 * Float and blink animations are driven by CSS in custom.css.
 */
const Robot: React.FC = () => {
  return (
    <div className="robot-container" aria-hidden="true">
      <svg
        width="160"
        height="200"
        viewBox="0 0 160 200"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="Friendly robot mascot"
      >
        {/* ── Antenna left ── */}
        <line x1="54" y1="42" x2="44" y2="18" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
        <circle cx="44" cy="14" r="6" fill="currentColor" />

        {/* ── Antenna right ── */}
        <line x1="106" y1="42" x2="116" y2="18" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
        <circle cx="116" cy="14" r="6" fill="currentColor" />

        {/* ── Head ── */}
        <rect x="36" y="40" width="88" height="58" rx="16" fill="currentColor" />

        {/* ── Eye sockets ── */}
        <rect x="48" y="56" width="22" height="16" rx="8" fill="white" />
        <rect x="90" y="56" width="22" height="16" rx="8" fill="white" />

        {/* ── Pupils (blink via CSS scaleY) ── */}
        <rect
          className="robot-pupil robot-pupil--left"
          x="54" y="60" width="10" height="8" rx="4"
          fill="#225f5b"
          style={{ transformOrigin: '59px 64px' }}
        />
        <rect
          className="robot-pupil robot-pupil--right"
          x="96" y="60" width="10" height="8" rx="4"
          fill="#225f5b"
          style={{ transformOrigin: '101px 64px' }}
        />

        {/* ── Smile ── */}
        <path d="M 58 85 Q 80 98 102 85" stroke="white" strokeWidth="3" fill="none" strokeLinecap="round" />

        {/* ── Neck ── */}
        <rect x="68" y="96" width="24" height="10" rx="4" fill="currentColor" />

        {/* ── Body ── */}
        <rect x="28" y="104" width="104" height="76" rx="18" fill="currentColor" />

        {/* ── Chest panel ── */}
        <rect x="52" y="118" width="56" height="36" rx="8" fill="white" opacity="0.15" />
        {/* Chest LED row */}
        <circle cx="66" cy="130" r="4" fill="white" opacity="0.6" />
        <circle cx="80" cy="130" r="4" fill="white" opacity="0.6" />
        <circle cx="94" cy="130" r="4" fill="white" opacity="0.6" />
        {/* Chest bar */}
        <rect x="60" y="142" width="40" height="6" rx="3" fill="white" opacity="0.4" />

        {/* ── Arms ── */}
        <rect x="4" y="108" width="22" height="52" rx="11" fill="currentColor" />
        <rect x="134" y="108" width="22" height="52" rx="11" fill="currentColor" />

        {/* ── Legs ── */}
        <rect x="48" y="176" width="24" height="22" rx="8" fill="currentColor" />
        <rect x="88" y="176" width="24" height="22" rx="8" fill="currentColor" />

        {/* ── Feet ── */}
        <rect x="42" y="192" width="36" height="8" rx="4" fill="currentColor" />
        <rect x="82" y="192" width="36" height="8" rx="4" fill="currentColor" />
      </svg>
    </div>
  );
};

export default Robot;