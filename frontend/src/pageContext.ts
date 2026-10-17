// Page context sent with every chat message (Problem 8), so the agent knows what "this" means.
import type { CartItem } from './cart'

/** What the shopper picked on a single-item page. ProductPage keeps this up to date. */
export const itemSelection: { productId: string | null; size: string | null; color: string | null } = {
  productId: null,
  size: null,
  color: null,
}

export interface PageContext {
  path: string
  page_type: 'home' | 'products' | 'product' | 'cart' | 'account' | 'about' | 'other'
  product_id: string | null
  selected_size: string | null
  selected_color: string | null
  filters: Record<string, string>
  cart: { product_id: string; name: string; size: string; color: string; quantity: number }[]
}

export function buildPageContext(pathname: string, search: string, cart: CartItem[]): PageContext {
  const item = /^\/products\/([^/]+)$/.exec(pathname)
  const productId = item ? decodeURIComponent(item[1]) : null
  const selected = productId && itemSelection.productId === productId ? itemSelection : null
  const pageType: PageContext['page_type'] =
    pathname === '/' ? 'home'
      : productId ? 'product'
        : pathname.startsWith('/products') ? 'products'
          : pathname.startsWith('/cart') ? 'cart'
            : ['/account', '/login', '/register'].some((p) => pathname.startsWith(p)) ? 'account'
              : pathname.startsWith('/about') ? 'about' : 'other'
  const filters = Object.fromEntries(
    [...new URLSearchParams(search)].filter(([k, v]) => v && ['q', 'group', 'category', 'collection', 'max_price', 'min_price', 'in_stock'].includes(k)),
  )
  return {
    path: pathname,
    page_type: pageType,
    product_id: productId,
    selected_size: selected?.size ?? null,
    selected_color: selected?.color ?? null,
    filters,
    cart: cart.slice(0, 20).map(({ product_id, name, size, color, quantity }) => ({ product_id, name, size, color, quantity })),
  }
}
