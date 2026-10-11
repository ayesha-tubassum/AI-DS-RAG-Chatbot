import React, { useState, useEffect, useRef } from 'react';

interface TypingEffectProps {
  phrases: string[];
  speed?: number;
  pauseDuration?: number;
}

const TypingEffect: React.FC<TypingEffectProps> = ({
  phrases,
  speed = 90,
  pauseDuration = 1800,
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [phase, setPhase] = useState<'typing' | 'pausing' | 'deleting'>('typing');
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const currentPhrase = phrases[phraseIndex];

    const schedule = (fn: () => void, delay: number) => {
      timeoutRef.current = setTimeout(fn, delay);
    };

    if (phase === 'typing') {
      if (displayedText.length < currentPhrase.length) {
        schedule(() => {
          setDisplayedText(currentPhrase.slice(0, displayedText.length + 1));
        }, speed);
      } else {
        // Full phrase typed — pause
        schedule(() => setPhase('pausing'), pauseDuration);
      }
    } else if (phase === 'pausing') {
      schedule(() => setPhase('deleting'), 0);
    } else if (phase === 'deleting') {
      if (displayedText.length > 0) {
        schedule(() => {
          setDisplayedText(displayedText.slice(0, -1));
        }, speed / 2);
      } else {
        // Done deleting — move to next phrase
        setPhraseIndex((prev) => (prev + 1) % phrases.length);
        setPhase('typing');
      }
    }

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [displayedText, phase, phraseIndex, phrases, speed, pauseDuration]);

  return (
    <div
      className="typing-effect"
      aria-label={`Cycling phrases: ${phrases.join(', ')}`}
      aria-live="polite"
    >
      <span className="typing-effect__text">{displayedText}</span>
      <span className="typing-effect__cursor" aria-hidden="true">|</span>
    </div>
  );
};

export default TypingEffect;