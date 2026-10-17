import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProduct, money, STOCK_LABEL, type ProductSummary } from '../api'
import { colorOptions, useCart } from '../cart'
import { useFetch } from '../useFetch'

const sizeLabel = (size: string) => (size === 'OS' ? 'One size' : size)

/** "Check options": choose color, size and quantity, then add to the cart. */
export default function OptionsDialog({ product, onClose }: { product: ProductSummary; onClose: () => void }) {
  const { data: detail, error, loading } = useFetch(() => getProduct(product.product_id), [product.product_id])
  const { add } = useCart()
  const colors = colorOptions(product)
  const [color, setColor] = useState(colors[0] ?? '')
  const [size, setSize] = useState<string | null>(null)
  const [quantity, setQuantity] = useState(1)
  const dialogRef = useRef<HTMLDivElement>(null)

  // One size and in stock? Pre-select it.
  useEffect(() => {
    if (detail?.sizes.length === 1 && detail.sizes[0].status !== 'sold_out') setSize(detail.sizes[0].size)
  }, [detail])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    dialogRef.current?.focus()
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const chosen = detail?.sizes.find((s) => s.size === size)
  const maxQty = Math.min(chosen?.quantity ?? 1, 10)

  return (
    <div className="dialog-backdrop" onClick={onClose}>
      <div className="dialog" role="dialog" aria-modal="true" aria-label={`Options for ${product.name}`} tabIndex={-1}
        ref={dialogRef} onClick={(e) => e.stopPropagation()}>
        <button className="dialog-close" aria-label="Close" onClick={onClose}>×</button>
        <img className="dialog-image" src={product.image_url} alt={product.name} />
        <div className="dialog-body">
          <h2>{product.name}</h2>
          <p className="dialog-price">{money(product.price)}</p>

          {colors.length > 0 && <fieldset className="option-group">
            <legend>Color <span>{color}</span></legend>
            <div className="option-pills">
              {colors.map((c) => (
                <button key={c} type="button" className={`size-pill ${c === color ? 'selected' : ''}`} aria-pressed={c === color}
                  disabled={colors.length === 1} onClick={() => setColor(c)}>{c}</button>
              ))}
            </div>
          </fieldset>}

          <fieldset className="option-group">
            <legend>Size {chosen && <span>{sizeLabel(chosen.size)} · {STOCK_LABEL[chosen.status].toLowerCase()}</span>}</legend>
            {loading && <p className="muted">Checking stock…</p>}
            {error && <p className="alert alert-error">{error}</p>}
            <div className="option-pills">
              {detail?.sizes.map((s) => (
                <button key={s.size} type="button" className={`size-pill ${s.status} ${size === s.size ? 'selected' : ''}`}
                  aria-pressed={size === s.size} disabled={s.status === 'sold_out'} title={STOCK_LABEL[s.status]}
                  onClick={() => { setSize(s.size); setQuantity(1) }}>
                  {sizeLabel(s.size)}
                </button>
              ))}
            </div>
          </fieldset>

          <div className="option-row">
            <label htmlFor="qty">Quantity</label>
            <div className="qty">
              <button type="button" aria-label="Fewer" onClick={() => setQuantity((q) => Math.max(1, q - 1))}>−</button>
              <input id="qty" inputMode="numeric" value={quantity} readOnly />
              <button type="button" aria-label="More" onClick={() => setQuantity((q) => Math.min(maxQty, q + 1))}>+</button>
            </div>
          </div>

          <button className="btn btn-primary btn-block" disabled={!size}
            onClick={() => { if (size) { add(product, size, color, quantity); onClose() } }}>
            {size ? 'Add to cart' : 'Select a size'}
          </button>
          <Link to={`/products/${product.product_id}`} className="dialog-link" onClick={onClose}>Full details</Link>
        </div>
      </div>
    </div>
  )
}
