import { useEffect, useRef, useState, type FormEvent } from 'react'
import { getChatHistory, sendChat, type ChatTurn, type ProductSummary } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import ProductCard from './ProductCard'

interface Message extends ChatTurn {
  products?: ProductSummary[]
  onPage?: number // how many matches were put on the page
  suggestions?: string[]
  error?: boolean
}

const QUICK_REPLIES = ['Best sellers', 'Residential colleges', 'Gifts for parents', 'Shipping & returns']

/** Opens the chat from anywhere, optionally with a question already typed. */
export function openChat(prefill = '') {
  window.dispatchEvent(new CustomEvent('open-chat', { detail: prefill }))
}

export default function ChatWidget() {
  const { user } = useAuth()
  const chatResults = useChatResults()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Logged-in shoppers get their saved chat back; logging out starts a fresh guest chat.
  useEffect(() => {
    let active = true
    if (!user) {
      setMessages([])
      return
    }
    getChatHistory()
      .then((saved) => active && setMessages(saved.map(({ role, content, products }) => ({ role, content, products }))))
      .catch(() => active && setMessages([]))
    return () => {
      active = false
    }
  }, [user])

  useEffect(() => {
    const handler = (event: Event) => {
      setOpen(true)
      setDraft((event as CustomEvent<string>).detail ?? '')
      setTimeout(() => inputRef.current?.focus(), 50)
    }
    window.addEventListener('open-chat', handler)
    return () => window.removeEventListener('open-chat', handler)
  }, [])

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, busy, open])

  async function send(text: string) {
    const message = text.trim()
    if (!message || busy) return
    // Guests send recent turns with each message; the server keeps logged-in shoppers' history itself.
    const history = user ? [] : messages.filter((m) => !m.error).map(({ role, content }) => ({ role, content }))
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setDraft('')
    setBusy(true)
    try {
      const response = await sendChat(message, history)
      // A search for a type of item fills the page with its matches; the chat keeps a short preview.
      if (response.page && response.products.length) {
        chatResults.show(message, response.products, response.page)
        // On a phone the chat covers the page, so step aside and let the cards show.
        if (window.matchMedia('(max-width: 719px)').matches) setOpen(false)
      }
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.reply, products: response.products, suggestions: response.suggestions,
          onPage: response.page ? response.products.length : undefined },
      ])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: (err as Error).message, error: true }])
    } finally {
      setBusy(false)
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    send(draft)
  }

  const last = messages[messages.length - 1]
  const chips = busy ? [] : !last ? QUICK_REPLIES : last.role === 'assistant' ? last.suggestions ?? [] : []

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" role="dialog" aria-label="Campus Customs chat">
          <header className="chat-header">
            <div>
              <strong>Campus Customs</strong>
              <small>{user ? 'Saved to your account' : 'Live prices and stock'}</small>
            </div>
            <button className="chat-close" aria-label="Close chat" onClick={() => setOpen(false)}>×</button>
          </header>
          <div className="chat-messages" ref={listRef} aria-live="polite">
            {user && <p className="chat-note">Welcome back, {user.first_name}.</p>}
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg chat-${m.role} ${m.error ? 'chat-error' : ''}`}>
                <p>{m.content}</p>
                {m.onPage ? <p className="chat-on-page">{m.onPage} {m.onPage === 1 ? 'match is' : 'matches are'} on the page ↖</p> : null}
                {m.products && m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.slice(0, m.onPage ? 3 : 6).map((p) => (
                      <ProductCard key={p.product_id} product={p} showDescription={false} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {busy && (
              <div className="chat-msg chat-assistant chat-typing" aria-label="Assistant is typing">
                <span /><span /><span />
              </div>
            )}
          </div>
          {chips.length > 0 && (
            <div className="chat-chips">
              {chips.map((q) => (
                <button key={q} type="button" onClick={() => send(q)}>{q}</button>
              ))}
            </div>
          )}
          <form className="chat-form" onSubmit={submit}>
            <label htmlFor="chat-input" className="sr-only">Message</label>
            <input
              id="chat-input"
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Message"
              maxLength={2000}
              autoComplete="off"
            />
            <button type="submit" aria-label="Send" disabled={busy || !draft.trim()}>
              <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
                <path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </form>
        </section>
      )}
      <button
        className="chat-launcher"
        aria-label={open ? 'Close chat' : 'Open chat'}
        title={open ? 'Close' : 'Chat with Campus Customs'}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <span className="chat-launcher-icon" aria-hidden="true">
          {open ? '×' : (
            <svg viewBox="0 0 24 24" width="44" height="44">
              <path d="M4.5 5.5h15v10h-9l-4 3.5v-3.5h-2z" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
            </svg>
          )}
        </span>
      </button>
    </div>
  )
}
