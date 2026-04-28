import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Send, Bot, User, Zap, Plus, MessageSquare,
  Trash2, Menu, Sun, Moon, Pencil, MoreHorizontal,
} from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface Session {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

interface CtxMenu {
  sessionId: string;
  x: number;
  y: number;
}

const STORAGE_KEY  = 'energy_rag_sessions';
const THEME_KEY    = 'energy_rag_theme';

function genId(): string {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function newSession(): Session {
  return { id: genId(), title: 'New Conversation', messages: [], createdAt: Date.now(), updatedAt: Date.now() };
}

function dateLabel(ts: number): string {
  const diff = Math.floor((Date.now() - ts) / 86_400_000);
  if (diff === 0) return 'Today';
  if (diff === 1) return 'Yesterday';
  if (diff < 7)  return 'Previous 7 Days';
  if (diff < 30) return 'Previous 30 Days';
  return new Date(ts).toLocaleString('default', { month: 'long', year: 'numeric' });
}

const DATE_ORDER = ['Today', 'Yesterday', 'Previous 7 Days', 'Previous 30 Days'];

const SUGGESTIONS = [
  'What drives electricity spot price volatility?',
  'Explain mean-reversion in energy markets',
  'What are transmission constraints?',
  'How does weather affect energy prices?',
];

const App: React.FC = () => {
  const [sessions,   setSessions]   = useState<Session[]>([]);
  const [activeId,   setActiveId]   = useState('');
  const [input,      setInput]      = useState('');
  const [isLoading,  setIsLoading]  = useState(false);
  const [sidebarOpen,setSidebarOpen]= useState(true);
  const [theme,      setTheme]      = useState<'dark'|'light'>('dark');
  const [ctxMenu,    setCtxMenu]    = useState<CtxMenu | null>(null);
  const [renaming,   setRenaming]   = useState<{ sessionId: string; value: string } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef    = useRef<HTMLTextAreaElement>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);

  /* ── Boot ── */
  useEffect(() => {
    // Load theme
    const savedTheme = localStorage.getItem(THEME_KEY) as 'dark'|'light' | null;
    if (savedTheme) setTheme(savedTheme);

    // Load sessions
    let saved: Session[] = [];
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) saved = JSON.parse(raw);
    } catch { /* ignore */ }

    const fresh = newSession();
    setSessions([fresh, ...saved]);
    setActiveId(fresh.id);
  }, []);

  /* ── Apply theme to <html> ── */
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  /* ── Persist non-empty sessions ── */
  useEffect(() => {
    if (sessions.length === 0) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions.filter(s => s.messages.length > 0)));
  }, [sessions]);

  /* ── Auto-scroll ── */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [sessions, activeId, isLoading]);

  /* ── Focus rename input when it appears ── */
  useEffect(() => {
    if (renaming) setTimeout(() => renameInputRef.current?.focus(), 50);
  }, [renaming]);

  /* ── Close context menu on outside click ── */
  useEffect(() => {
    if (!ctxMenu) return;
    const close = () => setCtxMenu(null);
    document.addEventListener('click', close);
    document.addEventListener('contextmenu', close);
    return () => {
      document.removeEventListener('click', close);
      document.removeEventListener('contextmenu', close);
    };
  }, [ctxMenu]);

  const activeSession = sessions.find(s => s.id === activeId);

  /* ── Handlers ── */
  const handleNewChat = () => {
    const fresh = newSession();
    setSessions(prev => [fresh, ...prev.filter(s => s.messages.length > 0)]);
    setActiveId(fresh.id);
    setInput('');
  };

  const handleSelect = (id: string) => { setActiveId(id); setInput(''); setCtxMenu(null); };

  const handleDelete = useCallback((id: string) => {
    setCtxMenu(null);
    setSessions(prev => {
      const next = prev.filter(s => s.id !== id);
      if (id === activeId) {
        const fresh = newSession();
        setActiveId(fresh.id);
        return [fresh, ...next.filter(s => s.messages.length > 0)];
      }
      return next;
    });
  }, [activeId]);

  const handleContextMenu = (sessionId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setCtxMenu({ sessionId, x: e.clientX, y: e.clientY });
  };

  const startRename = (sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId);
    if (!session) return;
    setCtxMenu(null);
    setRenaming({ sessionId, value: session.title });
  };

  const submitRename = () => {
    if (!renaming) return;
    const trimmed = renaming.value.trim();
    if (trimmed) {
      setSessions(prev => prev.map(s => s.id === renaming.sessionId ? { ...s, title: trimmed } : s));
    }
    setRenaming(null);
  };

  const handleRenameKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter')  submitRename();
    if (e.key === 'Escape') setRenaming(null);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading || !activeSession) return;
    const userMsg: Message = { id: genId(), role: 'user', content: input.trim(), timestamp: Date.now() };
    const isFirst = activeSession.messages.length === 0;
    const title   = isFirst
      ? userMsg.content.slice(0, 52) + (userMsg.content.length > 52 ? '…' : '')
      : activeSession.title;

    setSessions(prev => prev.map(s =>
      s.id === activeId ? { ...s, title, messages: [...s.messages, userMsg], updatedAt: Date.now() } : s
    ));
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg.content }),
      });
      if (!res.ok) throw new Error('Request failed');
      const data = await res.json();
      const botMsg: Message = { id: genId(), role: 'assistant', content: data.answer, timestamp: Date.now() };
      setSessions(prev => prev.map(s =>
        s.id === activeId ? { ...s, messages: [...s.messages, botMsg], updatedAt: Date.now() } : s
      ));
    } catch {
      const errMsg: Message = {
        id: genId(), role: 'assistant', timestamp: Date.now(),
        content: 'Something went wrong. Please make sure the backend is running and try again.',
      };
      setSessions(prev => prev.map(s =>
        s.id === activeId ? { ...s, messages: [...s.messages, errMsg], updatedAt: Date.now() } : s
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  /* ── Group sessions ── */
  const savedSessions  = sessions.filter(s => s.messages.length > 0);
  const groups = savedSessions.reduce<Record<string, Session[]>>((acc, s) => {
    const lbl = dateLabel(s.updatedAt);
    (acc[lbl] = acc[lbl] || []).push(s);
    return acc;
  }, {});
  const sortedGroups = Object.entries(groups).sort(([a], [b]) => {
    const ai = DATE_ORDER.indexOf(a), bi = DATE_ORDER.indexOf(b);
    if (ai === -1 && bi === -1) return b > a ? 1 : -1;
    if (ai === -1) return 1; if (bi === -1) return -1;
    return ai - bi;
  });

  /* ── Render ── */
  return (
    <div className="app-container">

      {/* ── Sidebar ── */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-top">
          <div className="brand">
            <Zap size={16} fill="currentColor" className="brand-icon" />
            <span className="brand-name">EnergyRAG</span>
          </div>
          <div style={{ display: 'flex', gap: 2 }}>
            <button className="icon-btn" id="new-chat-icon" onClick={handleNewChat} title="New chat">
              <Plus size={18} />
            </button>
            <button className="icon-btn" id="toggle-sidebar" onClick={() => setSidebarOpen(false)} title="Close sidebar">
              <Menu size={18} />
            </button>
          </div>
        </div>

        <div className="session-list">
          {sortedGroups.length === 0 && (
            <p className="no-sessions">No previous conversations yet.</p>
          )}
          {sortedGroups.map(([label, group]) => (
            <div key={label} className="session-group">
              <span className="group-label">{label}</span>
              {group.map(s => (
                <div
                  key={s.id}
                  id={`session-${s.id}`}
                  className={`session-item ${s.id === activeId ? 'active' : ''}`}
                  onClick={() => handleSelect(s.id)}
                  onContextMenu={(e) => handleContextMenu(s.id, e)}
                >
                  <MessageSquare size={14} className="session-icon" />
                  {renaming?.sessionId === s.id ? (
                    <input
                      ref={renameInputRef}
                      className="rename-input"
                      value={renaming.value}
                      onChange={e => setRenaming({ ...renaming, value: e.target.value })}
                      onKeyDown={handleRenameKey}
                      onBlur={submitRename}
                      onClick={e => e.stopPropagation()}
                    />
                  ) : (
                    <span className="session-title">{s.title}</span>
                  )}
                  <button
                    className="more-btn"
                    title="More options"
                    onClick={e => {
                      e.stopPropagation();
                      const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                      setCtxMenu({ sessionId: s.id, x: rect.right + 4, y: rect.top });
                    }}
                  >
                    <MoreHorizontal size={14} />
                  </button>
                </div>
              ))}
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="main-content">

        {/* Header */}
        <header className="chat-header">
          <div className="header-left">
            {!sidebarOpen && (
              <>
                <button className="icon-btn" id="open-sidebar" onClick={() => setSidebarOpen(true)} title="Open sidebar">
                  <Menu size={20} />
                </button>
                <button className="icon-btn" id="header-new-chat" onClick={handleNewChat} title="New chat">
                  <Plus size={20} />
                </button>
              </>
            )}
          </div>

          <span className="header-model">Energy Market Knowledge Assistant</span>

          <div className="header-right">
            <button
              className="icon-btn theme-toggle"
              id="theme-toggle"
              onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="chat-window">
          {activeSession?.messages.length === 0 && (
            <div className="empty-state">
              <div className="empty-logo">
                <Zap size={36} fill="currentColor" />
              </div>
              <h2 className="empty-title">Energy Market Knowledge Assistant</h2>
              <p className="empty-sub">Ask me anything about energy markets, trading, prices, or regulations.</p>
              <div className="suggestion-grid">
                {SUGGESTIONS.map(q => (
                  <button key={q} className="suggestion-btn"
                    onClick={() => { setInput(q); textareaRef.current?.focus(); }}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="message-list">
            {activeSession?.messages.map(msg => (
              <div key={msg.id} className={`message ${msg.role}`}>
                <div className="msg-avatar">
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className="msg-body">
                  {msg.role === 'assistant'
                    ? <div className="markdown-body"><ReactMarkdown>{msg.content}</ReactMarkdown></div>
                    : <p className="user-text">{msg.content}</p>}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="msg-avatar"><Bot size={16} /></div>
                <div className="msg-body">
                  <div className="typing">
                    <div className="dot" /><div className="dot" /><div className="dot" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-box">
            <textarea
              ref={textareaRef}
              id="chat-input"
              placeholder="Ask anything about the energy market…"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              onInput={e => {
                const t = e.target as HTMLTextAreaElement;
                t.style.height = 'auto';
                t.style.height = `${Math.min(t.scrollHeight, 200)}px`;
              }}
            />
            <button id="send-btn" className="send-btn" onClick={handleSend} disabled={!input.trim() || isLoading}>
              <Send size={16} />
            </button>
          </div>
          <p className="input-hint">EnergyRAG may make mistakes. Always verify critical information.</p>
        </div>
      </main>

      {/* ── Right-click context menu ── */}
      {ctxMenu && (
        <div
          className="ctx-menu"
          style={{ top: ctxMenu.y, left: ctxMenu.x }}
          onClick={e => e.stopPropagation()}
        >
          <button className="ctx-item" id="ctx-rename" onClick={() => startRename(ctxMenu.sessionId)}>
            <Pencil size={14} /> Rename
          </button>
          <div className="ctx-divider" />
          <button className="ctx-item danger" id="ctx-delete" onClick={() => handleDelete(ctxMenu.sessionId)}>
            <Trash2 size={14} /> Delete
          </button>
        </div>
      )}
    </div>
  );
};

export default App;
