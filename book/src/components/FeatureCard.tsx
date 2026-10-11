import React, { useEffect, useRef, useState } from 'react';

interface FeatureCardProps {
  icon?: string;
  title: string;
  description: string;
  visible?: boolean;
  delay?: number;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  visible = false,
  delay = 0,
}) => (
  <div
    className={`feature-card${visible ? ' feature-card--visible' : ''}`}
    style={{ transitionDelay: `${delay}ms` }}
  >
    {icon && <div className="feature-card__icon" aria-hidden="true">{icon}</div>}
    <h3 className="feature-card__title">{title}</h3>
    <p className="feature-card__desc">{description}</p>
  </div>
);

interface FeatureCardsProps {
  items: { icon?: string; title: string; description: string }[];
}

export const FeatureCards: React.FC<FeatureCardsProps> = ({ items }) => {
  const [visibleSet, setVisibleSet] = useState<Set<number>>(new Set());
  const refs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) {
      setVisibleSet(new Set(items.map((_, i) => i)));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const idx = Number((entry.target as HTMLElement).dataset.index);
            setVisibleSet((prev) => {
              const next = new Set(prev);
              next.add(idx);
              return next;
            });
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    refs.current.forEach((el) => {
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [items.length]);

  return (
    <div className="feature-cards" aria-label="What's inside the book">
      {items.map((item, index) => (
        <div
          key={index}
          ref={(el) => { refs.current[index] = el; }}
          data-index={index}
        >
          <FeatureCard
            icon={item.icon}
            title={item.title}
            description={item.description}
            visible={visibleSet.has(index)}
            delay={Math.min(index % 3, 2) * 100}
          />
        </div>
      ))}
    </div>
  );
};

export default FeatureCard;