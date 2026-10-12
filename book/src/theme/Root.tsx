/**
 * Root.tsx — Docusaurus swizzled Root component.
 *
 * Wraps every page in the site so BookChatbot appears globally,
 * without touching any docs or page component.
 *
 * This file is picked up automatically by Docusaurus; no config change needed.
 * https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */

import React from 'react';
import type { ReactNode } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import BookChatbot from '../components/BookChatbot';

interface Props {
  children: ReactNode;
}

export default function Root({ children }: Props): React.ReactElement {
  return (
    <>
      {children}
      {/* BrowserOnly: the chatbot uses browser APIs (fetch, window events) */}
      <BrowserOnly>{() => <BookChatbot />}</BrowserOnly>
    </>
  );
}
