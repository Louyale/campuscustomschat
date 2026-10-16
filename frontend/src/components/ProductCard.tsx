import { Link } from 'react-router-dom'
import { money, type ProductSummary } from '../api'

export default function ProductCard({ product, showDescription = true }: { product: ProductSummary; showDescription?: boolean }) {
  const top = product.best_seller_rank !== null && product.best_seller_rank <= 12
  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
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
  )
}
