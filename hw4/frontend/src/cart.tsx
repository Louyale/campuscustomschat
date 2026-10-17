import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'
import { money, type ProductSummary } from './api'

export interface CartItem {
  product_id: string
  name: string
  price: number
  image_url: string
  size: string
  color: string
  quantity: number
}

interface CartState {
  items: CartItem[]
  count: number
  subtotal: number
  add: (product: ProductSummary, size: string, color: string, quantity?: number) => void
  setQuantity: (item: CartItem, quantity: number) => void
  remove: (item: CartItem) => void
  clear: () => void
}

const STORAGE_KEY = 'cc_cart'
const CartContext = createContext<CartState | null>(null)
const same = (a: CartItem, b: Pick<CartItem, 'product_id' | 'size' | 'color'>) =>
  a.product_id === b.product_id && a.size === b.size && a.color === b.color

/** The shopping bag, kept in this browser (localStorage) so it survives reloads. */
export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]')
    } catch {
      return []
    }
  })
  const [toast, setToast] = useState<CartItem | null>(null)

  useEffect(() => localStorage.setItem(STORAGE_KEY, JSON.stringify(items)), [items])
  useEffect(() => {
    if (!toast) return
    const timer = setTimeout(() => setToast(null), 3500)
    return () => clearTimeout(timer)
  }, [toast])

  const add = useCallback((product: ProductSummary, size: string, color: string, quantity = 1) => {
    const line: CartItem = { product_id: product.product_id, name: product.name, price: product.price,
      image_url: product.image_url, size, color, quantity }
    setItems((prev) => {
      const existing = prev.find((i) => same(i, line))
      return existing
        ? prev.map((i) => (same(i, line) ? { ...i, quantity: Math.min(i.quantity + quantity, 25) } : i))
        : [...prev, line]
    })
    setToast(line)
  }, [])

  const setQuantity = useCallback((item: CartItem, quantity: number) => {
    setItems((prev) => prev.map((i) => (same(i, item) ? { ...i, quantity: Math.max(1, Math.min(quantity, 25)) } : i)))
  }, [])

  const remove = useCallback((item: CartItem) => setItems((prev) => prev.filter((i) => !same(i, item))), [])
  const clear = useCallback(() => setItems([]), [])

  const value = useMemo(() => ({
    items,
    count: items.reduce((n, i) => n + i.quantity, 0),
    subtotal: items.reduce((n, i) => n + i.quantity * i.price, 0),
    add, setQuantity, remove, clear,
  }), [items, add, setQuantity, remove, clear])

  return (
    <CartContext.Provider value={value}>
      {children}
      {/* Docked under the sticky header (like the buy bar), so it never covers a product or banner. */}
      {toast && document.querySelector('.site-header') && createPortal(
        <div className="cart-toast" role="status">
          <img src={toast.image_url} alt="" />
          <div>
            <small>Added to your cart</small>
            <strong>{toast.name}</strong>
            <span>{[toast.color, toast.size === 'OS' ? 'One size' : toast.size].filter(Boolean).join(' · ')} · {money(toast.price)}</span>
          </div>
          <Link to="/cart" onClick={() => setToast(null)}>View cart</Link>
        </div>,
        document.querySelector('.site-header')!,
      )}
    </CartContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCart() {
  const value = useContext(CartContext)
  if (!value) throw new Error('useCart must be used inside <CartProvider>')
  return value
}

/** Colors a shopper can actually choose. Hats and accessories come in real colorways; for clothing
 *  the catalogue lists the design's colors (garment first, then print), so only the garment color applies. */
// eslint-disable-next-line react-refresh/only-export-components
export function colorOptions(product: Pick<ProductSummary, 'category' | 'group' | 'colors'>): string[] {
  if (product.colors.length === 0) return []
  return product.category === 'Hats' || product.group === 'Accessories' ? product.colors : [product.colors[0]]
}
