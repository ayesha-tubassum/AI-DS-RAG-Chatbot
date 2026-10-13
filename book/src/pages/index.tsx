import type { ReactNode } from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import Layout from '@theme/Layout';
import BrowserOnly from '@docusaurus/BrowserOnly';
import TypingEffect from '../components/TypingEffect';
import ParticleCanvas from '../components/ParticleCanvas';
import { FeatureCards } from '../components/FeatureCard';

const phrases = ['Learn Python.', 'Master Data Science.', 'Build AI projects.'];

function HeroSection(): ReactNode {
  return (
    <section className="book-hero" aria-labelledby="hero-title">
      <div className="book-hero__background">
        <ParticleCanvas />
      </div>
      <div className="book-hero__content">
        <div className="book-hero__copy">
          <p className="eyebrow">A practical learning path</p>
          <h1 id="hero-title" className="book-hero__title">
            AI &<br />Data Science
          </h1>
          <p className="book-hero__lede">
            Build Python foundations, work confidently with data, and develop the skills behind modern AI.
          </p>
          <TypingEffect phrases={phrases} />
          <Link
            className="button button--primary button--lg book-hero__button"
            to="/module-01-python-foundations/variables-data-types"
            aria-label="Start Reading">
            {/* Left: circular gradient icon badge */}
            <span className="book-hero__button-badge" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
              </svg>
            </span>
            {/* Center: label */}
            <span className="book-hero__button-label">Start Reading</span>
            {/* Right: arrow */}
            <span className="book-hero__button-arrow" aria-hidden="true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"/>
                <polyline points="12 5 19 12 12 19"/>
              </svg>
            </span>
          </Link>
          <p className="book-hero__note">Start with Python. No prior AI experience required.</p>
        </div>
        <div className="cover-wrap" aria-hidden="true">
          <div className="book-cover">
            <img
              src={useBaseUrl('/img/cover-texture.jpg')}
              alt=""
              aria-hidden="true"
              onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
              style={{
                position: 'absolute',
                inset: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                opacity: 0.5,
                mixBlendMode: 'normal',
                filter: 'saturate(0.9) contrast(1.05)',
                pointerEvents: 'none',
                zIndex: 0,
              }}
            />
            <div className="book-cover__topline">A FIELD GUIDE TO</div>
            <div className="book-cover__title">AI<br />& DATA<br />SCIENCE</div>
            <div className="book-cover__grid" />
            <div className="book-cover__bottomline">BEGINNER EDITION</div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  return (
    <Layout
      title="A beginner's guide to AI and data science"
      description="A practical, beginner-friendly book about AI, data, and machine learning.">
      <main className="book-home">
        <BrowserOnly fallback={<div className="book-hero-fallback" />}>
          {() => <HeroSection />}
        </BrowserOnly>
        <section className="book-promise" aria-label="What's inside the book">
          <div className="book-promise__header">
            <span className="eyebrow">What's inside</span>
            <h2>Nine chapters. One complete path.</h2>
          </div>
          <FeatureCards
            items={[
              {
                icon: '🐍',
                title: 'Python Foundations',
                description: 'Variables, control flow, functions, OOP, and hands-on projects.',
              },
              {
                icon: '📊',
                title: 'Data Science Essentials',
                description: 'NumPy, pandas, visualization, cleaning, and exploratory analysis.',
              },
              {
                icon: '📐',
                title: 'Statistics & Math for ML',
                description: 'Probability, distributions, hypothesis testing, linear algebra.',
              },
              {
                icon: '🤖',
                title: 'Machine Learning',
                description: 'Supervised & unsupervised learning, model evaluation, practical projects.',
              },
              {
                icon: '🧠',
                title: 'Deep Learning',
                description: 'Neural networks, CNNs, RNNs, transfer learning, and NLP basics.',
              },
              {
                icon: '🚀',
                title: 'MLOps & Deployment',
                description: 'FastAPI, Docker, MLflow, CI/CD, monitoring, cloud platforms.',
              },
              {
                icon: '☁️',
                title: 'Big Data & Cloud',
                description: 'Spark, distributed computing, cloud ML, data lakes.',
              },
              {
                icon: '✨',
                title: 'Generative AI & LLMs',
                description: 'Transformers, fine-tuning, RAG, vector databases, agents.',
              },
              {
                icon: '🔗',
                title: 'Agentic AI',
                description: 'Tool-use, reasoning, multi-agent frameworks, autonomous systems.',
              },
            ]}
          />
        </section>
      </main>
    </Layout>
  );
}