import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useChatResults } from '../chatResults'
import ProductCard from './ProductCard'

/**
 * "From the chat": when the shopper asks the chat about a type of item, its matches appear here,
 * at the top of whatever page they're on, as the same product cards the Products page uses.
 * Each card opens the single-item page. On an item page the section folds to a slim bar.
 */
export default function ChatResultsSection() {
  const { results, clear } = useChatResults()
  const { pathname } = useLocation()
  const onItemPage = /^\/products\/[^/]+$/.test(pathname)
  const [open, setOpen] = useState(true)
  const ref = useRef<HTMLElement>(null)

  // A new search opens the section and brings it into view (not on first load of a saved result).
  const firstId = useRef(results?.id)
  useEffect(() => {
    if (!results || results.id === firstId.current) return
    setOpen(true)
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [results?.id])

  // Opening an item folds the results away; coming back to a list page shows them again.
  useEffect(() => setOpen(!onItemPage), [onItemPage])

  if (!results) return null
  const { question, products, page } = results

  return (
    <section ref={ref} className={`chat-results container ${open ? '' : 'folded'}`} aria-label="Chat search results">
      <div className="chat-results-head">
        <div>
          <p className="eyebrow">From the chat · “{question}”</p>
          <h2>{page.headline ?? page.title}</h2>
          <p className="muted">
            Showing {products.length} of {page.total} {page.total === 1 ? 'match' : 'matches'}
            {page.browse_url && page.total > products.length && (
              <> · <Link to={page.browse_url}>See all {page.total} →</Link></>
            )}
          </p>
        </div>
        <div className="chat-results-actions">
          <button className="link-button" onClick={() => setOpen(!open)}>{open ? 'Hide' : `Show ${products.length} matches`}</button>
          <button className="chat-results-close" aria-label="Clear chat results" onClick={clear}>×</button>
        </div>
      </div>
      <p className="sr-only" aria-live="polite">{`${products.length} matches for ${page.title} added to the page.`}</p>
      {open && (
        <div className="product-grid chat-results-grid">
          {products.map((p) => <ProductCard key={p.product_id} product={p} showActions />)}
        </div>
      )}
    </section>
  )
}
