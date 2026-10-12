/**
 * BookChatbot — floating chat panel that queries the book's RAG backend.
 *
 * API contract  POST {apiUrl}/api/chat
 *   request  { question: string }
 *   response { answer: string, grounded: boolean,
 *              sources: { title, section, path, score }[] }
 *
 * Each question is sent independently (no conversation memory).
 * No external libraries added; uses Docusaurus's own Link / useBaseUrl /
 * useDocusaurusContext.
 */

import React, {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';

// ── Types ─────────────────────────────────────────────────────────────────────

interface ApiSource {
  title: string;
  section: string;
  path: string;
  score: number;
}

interface ApiResponse {
  answer: string;
  grounded: boolean;
  sources: ApiSource[];
}

type MessageKind = 'user' | 'answer' | 'refusal' | 'error' | 'thinking';

interface Message {
  id: number;
  kind: MessageKind;
  text: string;
  sources?: ApiSource[];
}

// ── Inline SVG icons ──────────────────────────────────────────────────────────

function ChatIcon(): React.ReactElement {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

function CloseIcon(): React.ReactElement {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function SendIcon(): React.ReactElement {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

// ── Source deduplication helper ───────────────────────────────────────────────

function dedupSources(sources: ApiSource[]): ApiSource[] {
  const seen = new Set<string>();
  return sources.filter((s) => {
    const key = `${s.path}|${s.section}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

// ── Individual source link ────────────────────────────────────────────────────

function SourceLink({ source }: { source: ApiSource }): React.ReactElement {
  const href = useBaseUrl(source.path);
  const label = source.section
    ? `${source.title} › ${source.section}`
    : source.title;
  return (
    <li className={styles.sourceItem}>
      <Link to={href} className={styles.sourceLink}>
        {label}
      </Link>
    </li>
  );
}

// ── Single chat message ───────────────────────────────────────────────────────

function ChatMessage({ msg }: { msg: Message }): React.ReactElement {
  if (msg.kind === 'thinking') {
    return (
      <div className={`${styles.bubble} ${styles.bubbleThinking}`}>
        <span className={styles.thinkingDots}>
          <span />
          <span />
          <span />
        </span>
        Thinking…
      </div>
    );
  }

  if (msg.kind === 'user') {
    return <div className={`${styles.bubble} ${styles.bubbleUser}`}>{msg.text}</div>;
  }

  if (msg.kind === 'error') {
    return (
      <div className={`${styles.bubble} ${styles.bubbleError}`}>{msg.text}</div>
    );
  }

  if (msg.kind === 'refusal') {
    return (
      <div className={`${styles.bubble} ${styles.bubbleRefusal}`}>{msg.text}</div>
    );
  }

  // kind === 'answer'
  const unique = dedupSources(msg.sources ?? []);
  return (
    <div className={`${styles.bubble} ${styles.bubbleAnswer}`}>
      {/* plain text: white-space:pre-wrap in CSS, no dangerouslySetInnerHTML */}
      <p className={styles.answerText}>{msg.text}</p>
      {unique.length > 0 && (
        <div className={styles.sources}>
          <p className={styles.sourcesLabel}>Sources</p>
          <ul className={styles.sourcesList}>
            {unique.map((s) => (
              <SourceLink key={`${s.path}|${s.section}`} source={s} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

let _nextId = 1;
function nextId(): number {
  return _nextId++;
}

export default function BookChatbot(): React.ReactElement {
  const { siteConfig } = useDocusaurusContext();
  const apiUrl =
    (siteConfig.customFields?.apiUrl as string | undefined) ??
    'http://localhost:8000';

  const [open, setOpen]         = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft]       = useState('');
  const [loading, setLoading]   = useState(false);

  const bottomRef   = useRef<HTMLDivElement>(null);
  const inputRef    = useRef<HTMLTextAreaElement>(null);
  const panelRef    = useRef<HTMLDivElement>(null);

  // Auto-scroll to newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  // Escape closes the panel
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);

  const send = useCallback(async () => {
    const question = draft.trim();
    if (!question || loading) return;
    if (question.length > 1000) return;

    setDraft('');
    setLoading(true);

    // Add user bubble + thinking bubble
    const thinkingId = nextId();
    setMessages((prev) => [
      ...prev,
      { id: nextId(), kind: 'user', text: question },
      { id: thinkingId, kind: 'thinking', text: '' },
    ]);

    try {
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      // Remove thinking bubble
      setMessages((prev) => prev.filter((m) => m.id !== thinkingId));

      if (!res.ok) {
        let detail = `The assistant returned an error (${res.status}).`;
        try {
          const err = await res.json() as { detail?: string };
          if (err.detail) detail = err.detail;
        } catch {
          // ignore parse error — keep generic message
        }
        setMessages((prev) => [
          ...prev,
          { id: nextId(), kind: 'error', text: 'Could not reach the book assistant. Please make sure the backend is running and try again.' },
        ]);
        return;
      }

      const data = await res.json() as ApiResponse;

      if (data.grounded) {
        setMessages((prev) => [
          ...prev,
          { id: nextId(), kind: 'answer', text: data.answer, sources: data.sources ?? [] },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { id: nextId(), kind: 'refusal', text: data.answer },
        ]);
      }
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== thinkingId));
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          kind: 'error',
          text: 'Could not reach the book assistant. Please make sure the backend is running and try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, draft, loading]);

  const onKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    },
    [send],
  );

  return (
    <>
      {/* Floating toggle button */}
      <button
        className={styles.fab}
        onClick={() => setOpen((v) => !v)}
        aria-label="Ask AI"
        title="Ask AI"
        aria-expanded={open}
        aria-haspopup="dialog"
      >
        <ChatIcon />
        <span className={styles.fabLabel}>Ask AI</span>
      </button>

      {/* Chat panel */}
      {open && (
        <div
          ref={panelRef}
          className={styles.panel}
          role="dialog"
          aria-label="Book chatbot"
          aria-modal="false"
        >
          {/* Header */}
          <div className={styles.header}>
            <span className={styles.headerTitle}>Ask AI</span>
            <button
              className={styles.closeBtn}
              onClick={() => setOpen(false)}
              aria-label="Close chatbot"
            >
              <CloseIcon />
            </button>
          </div>

          {/* Messages */}
          <div className={styles.messages} role="log" aria-live="polite">
            {messages.length === 0 && (
              <p className={styles.emptyHint}>
                Ask anything about the book's content.
              </p>
            )}
            {messages.map((m) => (
              <ChatMessage key={m.id} msg={m} />
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Input row */}
          <div className={styles.inputRow}>
            <textarea
              ref={inputRef}
              className={styles.input}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask a question… (Enter to send)"
              rows={2}
              maxLength={1000}
              disabled={loading}
              aria-label="Your question"
            />
            <button
              className={styles.sendBtn}
              onClick={send}
              disabled={loading || !draft.trim()}
              aria-label="Send"
            >
              <SendIcon />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
