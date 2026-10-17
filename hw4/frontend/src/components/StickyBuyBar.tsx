import { useEffect, useState, type RefObject } from 'react'
import { createPortal } from 'react-dom'
import { money, STOCK_LABEL, type Product } from '../api'

interface Props {
  product: Product
  selected: string | null
  onSelect: (size: string) => void
  onAdd: () => void
  watch: RefObject<HTMLElement | null> // the page's own Add to cart button
}

const sizeLabel = (size: string) => (size === 'OS' ? 'One size' : size)

/**
 * Sticky "Add to cart" bar (Problem 9, front-end improvement 2): whenever the page's own button
 * is out of view, this bar keeps the item, its price, the size and Add to cart in reach.
 */
export default function StickyBuyBar({ product, selected, onSelect, onAdd, watch }: Props) {
  const [visible, setVisible] = useState(false)

  // Show the bar whenever the page's own button is off screen: scrolled up under the sticky
  // header, or not reached yet (on a phone it sits below the photo).
  useEffect(() => {
    const check = () => {
      const target = watch.current
      if (!target) return
      // Measure against the header without the docked bar, so showing the bar doesn't flip the check.
      const bar = document.querySelector('.buy-bar')?.getBoundingClientRect().height ?? 0
      const headerBottom = (document.querySelector('.site-header')?.getBoundingClientRect().bottom ?? 0) - bar
      const rect = target.getBoundingClientRect()
      setVisible(rect.bottom < headerBottom || rect.top > window.innerHeight - 20)
    }
    check()
    window.addEventListener('scroll', check, { passive: true })
    window.addEventListener('resize', check)
    return () => {
      window.removeEventListener('scroll', check)
      window.removeEventListener('resize', check)
    }
  }, [watch])

  // Tell the page the header is taller, so sticky content moves down below the bar.
  useEffect(() => {
    document.body.classList.toggle('has-buy-bar', visible)
    const header = document.querySelector('.site-header')
    if (visible && header) document.body.style.setProperty('--sticky-top', `${header.getBoundingClientRect().height + 16}px`)
    return () => document.body.classList.remove('has-buy-bar')
  }, [visible])

  const dock = document.querySelector('.site-header')
  if (!visible || !dock) return null
  const size = product.sizes.find((s) => s.size === selected)
  const available = product.sizes.filter((s) => s.status !== 'sold_out')

  // Docked inside the sticky header: it never covers a product, a banner or the chat button.
  return createPortal(
    <div className="buy-bar" role="region" aria-label="Quick add to cart">
      <img src={product.image_url} alt="" />
      <div className="buy-bar-info">
        <strong>{product.name}</strong>
        <span className="buy-bar-price">{money(product.price)}</span>
        {size && <span className={`buy-bar-stock ${size.status}`}>{STOCK_LABEL[size.status]}{size.status === 'low_stock' ? ` · ${size.quantity} left` : ''}</span>}
      </div>
      {product.sizes.length > 1 && (
        <label className="buy-bar-size">
          <span className="sr-only">Size</span>
          <select value={selected ?? ''} onChange={(e) => onSelect(e.target.value)}>
            <option value="" disabled>Choose size</option>
            {available.map((s) => <option key={s.size} value={s.size}>{sizeLabel(s.size)}</option>)}
          </select>
        </label>
      )}
      <button className="btn btn-primary buy-bar-add" disabled={!selected} onClick={onAdd}>
        {selected ? 'Add to cart' : 'Choose a size'}
      </button>
    </div>,
    dock,
  )
}
