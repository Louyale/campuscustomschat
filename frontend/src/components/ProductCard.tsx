import { useState } from 'react'
import { Link } from 'react-router-dom'
import { money, type ProductSummary } from '../api'
import { colorOptions, useCart } from '../cart'
import OptionsDialog from './OptionsDialog'

interface Props {
  product: ProductSummary
  showDescription?: boolean
  showActions?: boolean
}

export default function ProductCard({ product, showDescription = true, showActions = false }: Props) {
  const top = product.best_seller_rank !== null && product.best_seller_rank <= 12
  const { add } = useCart()
  const [choosing, setChoosing] = useState(false)
  const colors = colorOptions(product)

  // One-size hats in a single color go straight in; everything else needs a size first.
  function addToCart() {
    if (product.category === 'Hats' && colors.length <= 1) add(product, 'OS', colors[0] ?? '')
    else setChoosing(true)
  }

  return (
    <div className="product-card">
      <Link to={`/products/${product.product_id}`} className="product-card-link">
        <div className="product-card-image">
          <img src={product.image_url} alt={product.name} loading="lazy" />
          {top && <span className="badge badge-best">Best seller</span>}
          {!product.in_stock && <span className="badge badge-sold">Sold out</span>}
        </div>
        <div className="product-card-body">
          <h3>{product.name}</h3>
          <p className="price">{money(product.price)}</p>
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
