import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';

export default function Home(): ReactNode {
  return (
    <Layout
      title="A beginner's guide to AI and data science"
      description="A practical, beginner-friendly book about AI, data, and machine learning.">
      <main className="book-home">
        <section className="book-hero">
          <div className="book-hero__copy">
            <p className="eyebrow">A practical learning path</p>
            <h1>AI &amp;<br />Data Science</h1>
            <p className="book-hero__lede">
              Build Python foundations, work confidently with data, and develop the skills behind modern AI.
            </p>
            <Link
              className="button button--primary button--lg book-hero__button"
              to="/module-01-python-foundations/variables-data-types">
              Start Reading <span aria-hidden="true">→</span>
            </Link>
            <p className="book-hero__note">Start with Python. No prior AI experience required.</p>
          </div>
          <div className="cover-wrap" aria-hidden="true">
            <div className="book-cover">
              <div className="book-cover__topline">A FIELD GUIDE TO</div>
              <div className="book-cover__title">AI<br />&amp; DATA<br />SCIENCE</div>
              <div className="book-cover__grid" />
              <div className="book-cover__bottomline">BEGINNER EDITION</div>
            </div>
          </div>
        </section>
        <section className="book-promise" aria-label="What you will learn">
          <div><span>01</span><h2>Learn Python</h2><p>Build the foundation for hands-on data work.</p></div>
          <div><span>02</span><h2>Understand data</h2><p>Turn raw information into useful evidence.</p></div>
          <div><span>03</span><h2>Explore AI</h2><p>Progress from core concepts to practical systems.</p></div>
        </section>
      </main>
    </Layout>
  );
}
