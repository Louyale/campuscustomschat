import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { money } from '../api'
import { useCart } from '../cart'

// Order math. Connecticut taxes clothing and the delivery charge at 6.35%.
// Shipping is a flat UPS Ground estimate until real carrier rates are connected.
const TAX_RATE = 0.0635
const SHIPPING_ESTIMATE = 9.95

/** Luhn checksum: catches mistyped card numbers before submitting. */
function validCardNumber(digits: string): boolean {
  if (!/^\d{13,19}$/.test(digits)) return false
  let sum = 0
  for (let i = 0; i < digits.length; i++) {
    let d = Number(digits[digits.length - 1 - i])
    if (i % 2 === 1) {
      d *= 2
      if (d > 9) d -= 9
    }
    sum += d
  }
  return sum % 10 === 0
}

function validExpiry(value: string): boolean {
  const match = /^(\d{2})\s*\/\s*(\d{2})$/.exec(value)
  if (!match) return false
  const month = Number(match[1])
  const year = 2000 + Number(match[2])
  const now = new Date()
  return month >= 1 && month <= 12 && (year > now.getFullYear() || (year === now.getFullYear() && month >= now.getMonth() + 1))
}

export default function Cart() {
  const { items, subtotal, setQuantity, remove, clear } = useCart()
  const [error, setError] = useState('')
  const [placed, setPlaced] = useState<{ total: number; last4: string } | null>(null)

  const shipping = items.length ? SHIPPING_ESTIMATE : 0
  const tax = Math.round((subtotal + shipping) * TAX_RATE * 100) / 100
  const total = subtotal + shipping + tax

  // Card details stay in this form only: they are never sent to our server or saved anywhere.
  function placeOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const number = String(form.get('cc-number') ?? '').replace(/\D/g, '')
    if (!String(form.get('cc-name') ?? '').trim()) return setError('Enter the name on the card.')
    if (!validCardNumber(number)) return setError('Check the card number.')
    if (!validExpiry(String(form.get('cc-exp') ?? ''))) return setError('Check the expiration date (MM/YY).')
    if (!/^\d{3,4}$/.test(String(form.get('cc-csc') ?? ''))) return setError('Check the security code.')
    if (!/^\d{5}$/.test(String(form.get('postal') ?? ''))) return setError('Enter a 5-digit ZIP code.')
    setError('')
    event.currentTarget.reset()
    setPlaced({ total, last4: number.slice(-4) })
    clear()
  }

  if (placed) {
    return (
      <div className="page container narrow">
        <h1>Order received</h1>
        <p className="alert alert-info" role="status">
          Thank you. This is a demonstration checkout: no payment was taken and your card ending in {placed.last4} was
          not stored. Order total: {money(placed.total)}.
        </p>
        <Link to="/products" className="btn btn-primary">Continue shopping</Link>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="page container narrow">
        <h1>Your cart</h1>
        <p className="muted">Your cart is empty.</p>
        <Link to="/products" className="btn btn-primary">Continue shopping</Link>
      </div>
    )
  }

  return (
    <div className="page container">
      <h1>Your cart</h1>
      <div className="checkout">
        <ul className="cart-lines">
          {items.map((item) => (
            <li key={`${item.product_id}-${item.size}-${item.color}`} className="cart-line">
              <img src={item.image_url} alt="" />
              <div className="cart-line-info">
                <Link to={`/products/${item.product_id}`}>{item.name}</Link>
                <span className="muted">{[item.color, item.size === 'OS' ? 'One size' : item.size].filter(Boolean).join(' · ')}</span>
                <button className="link-button" onClick={() => remove(item)}>Remove</button>
              </div>
              <div className="qty">
                <button type="button" aria-label="Fewer" onClick={() => setQuantity(item, item.quantity - 1)}>−</button>
                <input value={item.quantity} readOnly aria-label="Quantity" />
                <button type="button" aria-label="More" onClick={() => setQuantity(item, item.quantity + 1)}>+</button>
              </div>
              <strong>{money(item.price * item.quantity)}</strong>
            </li>
          ))}
        </ul>

        <aside className="order-panel">
          <h2>Order summary</h2>
          <dl className="tally">
            <div><dt>Subtotal</dt><dd>{money(subtotal)}</dd></div>
            <div><dt>Shipping <small>(UPS Ground, estimated)</small></dt><dd>{money(shipping)}</dd></div>
            <div><dt>CT sales tax <small>(6.35%)</small></dt><dd>{money(tax)}</dd></div>
            <div className="tally-total"><dt>Total</dt><dd>{money(total)}</dd></div>
          </dl>
          <p className="muted small">Most pieces are printed to order and ship in 5–8 business days.</p>

          <form className="form card-form" onSubmit={placeOrder} autoComplete="on" noValidate>
            <h3>Payment</h3>
            <label htmlFor="cc-name">Name on card</label>
            <input id="cc-name" name="cc-name" autoComplete="cc-name" />
            <label htmlFor="cc-number">Card number</label>
            <input id="cc-number" name="cc-number" autoComplete="cc-number" inputMode="numeric" placeholder="1234 5678 9012 3456" maxLength={23} />
            <div className="form-row form-row-3">
              <div>
                <label htmlFor="cc-exp">Expires</label>
                <input id="cc-exp" name="cc-exp" autoComplete="cc-exp" placeholder="MM/YY" maxLength={7} />
              </div>
              <div>
                <label htmlFor="cc-csc">Security code</label>
                <input id="cc-csc" name="cc-csc" autoComplete="cc-csc" inputMode="numeric" maxLength={4} type="password" />
              </div>
              <div>
                <label htmlFor="postal">ZIP</label>
                <input id="postal" name="postal" autoComplete="postal-code" inputMode="numeric" maxLength={5} />
              </div>
            </div>
            {error && <p className="alert alert-error" role="alert">{error}</p>}
            <button type="submit" className="btn btn-primary btn-block">Place order · {money(total)}</button>
            <p className="secure-note">
              Demonstration checkout: no charge is made, and card details never leave this page or get saved.
            </p>
          </form>
        </aside>
      </div>
    </div>
  )
}
