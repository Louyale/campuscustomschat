import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getProduct, money, STOCK_LABEL } from '../api'
import { useFetch } from '../useFetch'
import { openChat } from '../components/ChatWidget'

export default function ProductPage() {
  const { productId = '' } = useParams()
  const { data: product, error, loading } = useFetch(() => getProduct(productId), [productId])
  const [selected, setSelected] = useState<string | null>(null)

  if (loading) return <div className="page container"><p className="muted">Loading product…</p></div>
  if (error || !product) {
    return (
      <div className="page container narrow">
        <h1>Product not found</h1>
        <p className="alert alert-error">{error ?? 'That product does not exist.'}</p>
        <Link to="/products" className="btn btn-primary">Back to all products</Link>
      </div>
    )
  }

  const size = product.sizes.find((s) => s.size === selected)

  return (
    <div className="page container">
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <Link to="/">Home</Link> / <Link to="/products">Products</Link> /{' '}
        <Link to={`/products?category=${encodeURIComponent(product.category)}`}>{product.category}</Link> / {product.name}
      </nav>

      <div className="item">
        <div className="item-image">
          <img src={product.image_url} alt={product.name} />
        </div>

        <div className="item-info">
          {product.best_seller_rank !== null && product.best_seller_rank <= 12 && <span className="badge badge-best static">Best seller</span>}
          <h1>{product.name}</h1>
          <p className="item-price">{money(product.price)}</p>
          <p className="item-desc">{product.description}</p>

          <dl className="item-facts">
            <div><dt>Style</dt><dd>{product.garment_type}</dd></div>
            <div><dt>Colors</dt><dd>{product.colors.join(', ')}</dd></div>
          </dl>

          <fieldset className="sizes">
            <legend>Size{size ? `: ${size.size}` : ''}</legend>
            <div className="size-pills">
              {product.sizes.map((s) => (
                <button
                  key={s.size}
                  type="button"
                  className={`size-pill ${s.status} ${selected === s.size ? 'selected' : ''}`}
                  aria-pressed={selected === s.size}
                  disabled={s.status === 'sold_out'}
                  onClick={() => setSelected(s.size)}
                  title={`${s.size}: ${STOCK_LABEL[s.status]}`}
                >
                  {s.size}
                </button>
              ))}
            </div>
          </fieldset>

          <table className="stock-table">
            <caption>Stock by size</caption>
            <thead><tr><th scope="col">Size</th><th scope="col">Available</th><th scope="col">Status</th></tr></thead>
            <tbody>
              {product.sizes.map((s) => (
                <tr key={s.size} className={selected === s.size ? 'selected' : ''}>
                  <td>{s.size}</td>
                  <td>{s.quantity}</td>
                  <td><span className={`stock-dot ${s.status}`} />{STOCK_LABEL[s.status]}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <button className="btn btn-primary btn-block" onClick={() => openChat(`Is the ${product.name} available in ${selected ?? 'my size'}?`)}>
            Ask about this item
          </button>

          <details className="item-details">
            <summary>Shipping &amp; returns</summary>
            <p>
              Printed to order: allow 5–8 business days before it ships, longer around move-in and The Game.
              Most domestic orders ship by UPS with tracking. Unworn items with tags can be returned within 30
              days of shipping; custom pieces are final sale.
            </p>
          </details>
        </div>
      </div>
    </div>
  )
}
