import { useEffect, useRef, useState, type FormEvent } from 'react'
import { sendChat, type ChatTurn, type ProductSummary } from '../api'
import { useAuth } from '../auth'
import ProductCard from './ProductCard'

interface Message extends ChatTurn {
  products?: ProductSummary[]
  error?: boolean
}

const WELCOME: Message = {
  role: 'assistant',
  content:
    "Hey! I'm the Campus Customs assistant. Ask me about sizes, stock, prices, or what to wear to The Game.",
}

const QUICK_REPLIES = ['Best-selling hoodies', 'Residential college gear', 'Gifts for Yale parents', 'Shipping & returns']

/** Opens the chat from anywhere, optionally with a question already typed. */
export function openChat(prefill = '') {
  window.dispatchEvent(new CustomEvent('open-chat', { detail: prefill }))
}

export default function ChatWidget() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([WELCOME])
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

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
  }, [messages, busy])

  async function send(text: string) {
    const message = text.trim()
    if (!message || busy) return
    const history = messages.filter((m) => !m.error && m !== WELCOME).map(({ role, content }) => ({ role, content }))
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setDraft('')
    setBusy(true)
    try {
      const response = await sendChat(message, history)
      setMessages((prev) => [...prev, { role: 'assistant', content: response.reply, products: response.products }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Sorry, I couldn't reach the shop just now (${(err as Error).message}). Please try again.`, error: true },
      ])
    } finally {
      setBusy(false)
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    send(draft)
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" role="dialog" aria-label="Campus Customs chat">
          <header className="chat-header">
            <div>
              <strong>Campus Customs Help</strong>
              <small>Real prices and stock, straight from the shop</small>
            </div>
            <button className="chat-close" aria-label="Close chat" onClick={() => setOpen(false)}>×</button>
          </header>
          <div className="chat-messages" ref={listRef} aria-live="polite">
            {messages.map((m, i) => (

              <div key={i} className={`chat-msg chat-${m.role} ${m.error ? 'chat-error' : ''}`}>
                <p>{m === WELCOME && user ? m.content.replace('Hey!', `Hey ${user.first_name}!`) : m.content}</p>
                {m.products && m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.map((p) => (
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
          {messages.length === 1 && (
            <div className="chat-chips">
              {QUICK_REPLIES.map((q) => (
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
              placeholder="Ask about a size, price, or gift idea…"
              maxLength={2000}
              autoComplete="off"
            />
            <button type="submit" disabled={busy || !draft.trim()}>Send</button>
          </form>
        </section>
      )}
      <button
        className="chat-launcher"
        aria-label={open ? 'Close chat' : 'Open chat'}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        {!open && <span className="chat-launcher-label">Hey! Need help?</span>}
        <span className="chat-launcher-icon" aria-hidden="true">
          {open ? '×' : (
            <svg viewBox="0 0 24 24" width="26" height="26">
              <path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z" />
            </svg>
          )}
        </span>
      </button>
    </div>
  )
}
