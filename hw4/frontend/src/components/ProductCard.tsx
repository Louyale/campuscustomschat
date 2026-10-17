import { useState } from 'react'
import { Link } from 'react-router-dom'
import { money, type ProductSummary } from '../api'
import { colorOptions, useCart } from '../cart'
import OptionsDialog from './OptionsDialog'

interface Props {
  product: ProductSummary
  showDescription?: boolean
  showActions?: boolean
  featured?: boolean  // shown a little larger, e.g. the #1 best seller
}

export default function ProductCard({ product, showDescription = true, showActions = false, featured = false }: Props) {
  const top = product.best_seller_rank !== null && product.best_seller_rank <= 12
  const { add } = useCart()
  const [choosing, setChoosing] = useState(false)
  const colors = colorOptions(product)

  // One-size items with one colorway go straight in; everything else opens the options first.
  function addToCart() {
    if (product.one_size && colors.length <= 1) add(product, 'OS', colors[0] ?? '')
    else setChoosing(true)
  }

  return (
    <div className={`product-card${featured ? ' product-card-featured' : ''}`}>
      <Link to={`/products/${product.product_id}`} className="product-card-link">
        <div className="product-card-image">
          <img src={product.image_url} alt={product.name} loading="lazy" />
        </div>
        <div className="product-card-body">
          {/* Labels sit in their own row, never over the photo; the row keeps its height so names line up. */}
          <div className="card-labels">
            {top && <span className="badge badge-best">{featured && product.best_seller_rank === 1 ? '#1 Best seller' : 'Best seller'}</span>}
            {!product.in_stock && <span className="badge badge-sold">Sold out</span>}
          </div>
          <h3>{product.name}</h3>
          <p className="price">{money(product.price)}</p>
          {product.note && <p className="card-note">✓ {product.note}</p>}
          {showDescription && <p className="product-card-desc">{product.short_description}</p>}
        </div>
      </Link>
      {showActions && (
        <div className="card-actions">
          <button type="button" className="card-btn card-btn-primary" onClick={addToCart} disabled={!product.in_stock}>
            {product.in_stock ? 'Add to cart' : 'Sold out'}
          </button>
          <button type="button" className="card-btn" onClick={() => setChoosing(true)}>Check options</button>
        </div>
      )}
      {choosing && <OptionsDialog product={product} onClose={() => setChoosing(false)} />}
    </div>
  )
}
