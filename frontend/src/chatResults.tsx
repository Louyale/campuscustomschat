import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import type { PageResults, ProductSummary } from './api'

/** The latest chat search, shown as product cards on the page (Problem 7). */
export interface ChatResults {
  question: string
  products: ProductSummary[]
  page: PageResults
  id: number // changes on every new search so the page can scroll to it
}

interface ChatResultsState {
  results: ChatResults | null
  show: (question: string, products: ProductSummary[], page: PageResults) => void
  clear: () => void
}

const Context = createContext<ChatResultsState | null>(null)

const STORAGE_KEY = 'cc_chat_results'

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  // Kept for this browser session, so the matches survive a reload or a trip to an item page.
  const [results, setResults] = useState<ChatResults | null>(() => {
    try {
      return JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? 'null')
    } catch {
      return null
    }
  })
  useEffect(() => {
    if (results) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(results))
    else sessionStorage.removeItem(STORAGE_KEY)
  }, [results])
  const show = useCallback((question: string, products: ProductSummary[], page: PageResults) => {
    setResults({ question, products, page, id: Date.now() })
  }, [])
  const clear = useCallback(() => setResults(null), [])
  return <Context.Provider value={{ results, show, clear }}>{children}</Context.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useChatResults() {
  const value = useContext(Context)
  if (!value) throw new Error('useChatResults must be used inside <ChatResultsProvider>')
  return value
}
