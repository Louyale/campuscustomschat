// Typed calls to the FastAPI backend (backend/main.py). Vite proxies /api and /images.
import type { PageContext } from './pageContext'

export type StockStatus = 'in_stock' | 'low_stock' | 'sold_out'

export interface ProductSummary {
  product_id: string
  name: string
  garment_type: string
  category: string
  group: 'Apparel' | 'Accessories'
  one_size: boolean
  collections: string[]
  short_description: string
  price: number
  image_url: string
  colors: string[]
  best_seller_rank: number | null
  total_stock: number
  in_stock: boolean
}

export interface Size {
  size: string
  quantity: number
  status: StockStatus
}

export interface Product extends ProductSummary {
  description: string
  search_tags: string[]
  sizes: Size[]
}

export interface Facet {
  name: string
  count: number
  group?: 'Apparel' | 'Accessories'
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface PageResults {
  title: string
  headline: string // e.g. "We have Hoodies!"
  total: number
  browse_url: string | null
}

export interface ChatResponse {
  reply: string
  products: ProductSummary[]
  page: PageResults | null // set when the chat searched for a type of item: show the matches on the page
  suggestions: string[]
  saved: boolean
}

export interface SavedChatMessage extends ChatTurn {
  products: ProductSummary[]
  created_at: string | null
}

export type ProductQuery = Partial<{
  q: string
  group: string
  category: string
  collection: string
  in_stock: string
  min_price: string
  max_price: string
  sort: string
  limit: string
}>

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init)
  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    const message = typeof detail?.detail === 'string' ? detail.detail : `Request failed (${response.status})`
    throw new Error(message)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function getProducts(query: ProductQuery = {}): Promise<ProductSummary[]> {
  const params = new URLSearchParams(Object.entries(query).filter(([, v]) => v) as [string, string][])
  return request(`/api/products?${params}`)
}

export function getProduct(productId: string): Promise<Product> {
  return request(`/api/products/${encodeURIComponent(productId)}`)
}

export function getFacets(): Promise<{ categories: Facet[]; collections: Facet[]; groups: Facet[] }> {
  return request('/api/categories')
}

export const getChatHistory = () => request<SavedChatMessage[]>('/api/chat/history')

export function sendChat(message: string, history: ChatTurn[], page?: PageContext): Promise<ChatResponse> {
  return request('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history, page }),
  })
}

export const money = (value: number) =>
  value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })

export const STOCK_LABEL: Record<StockStatus, string> = {
  in_stock: 'In stock',
  low_stock: 'Low stock',
  sold_out: 'Sold out',
}

/** URL for a catalogue photo by product_id. Keep v= in step with IMAGE_VERSION in backend/main.py. */
export const productImage = (productId: string) => `/images/${productId}.jpg?v=4`

// ---------------------------------------------------------------- accounts

export interface User {
  id: number
  first_name: string
  last_name: string
  email: string
}

const jsonPost = (body: unknown): RequestInit => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

export const getMe = () => request<User | null>('/api/auth/me')
export const login = (email: string, password: string) => request<User>('/api/auth/login', jsonPost({ email, password }))
export const register = (data: { first_name: string; last_name: string; email: string; password: string }) =>
  request<User>('/api/auth/register', jsonPost(data))
export const logout = () => fetch('/api/auth/logout', { method: 'POST' })
