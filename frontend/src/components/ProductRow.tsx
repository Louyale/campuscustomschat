import { Link } from 'react-router-dom'
import { getProducts, type ProductQuery } from '../api'
import { useFetch } from '../useFetch'
import ProductCard from './ProductCard'

interface Props {
  title: string
  intro?: string
  query: ProductQuery
  shopLink: string
  shopLabel?: string
}

/** A home-page section: heading, short intro, and a scrolling row of product cards. */
export default function ProductRow({ title, intro, query, shopLink, shopLabel = 'Shop all' }: Props) {
  const { data, error, loading } = useFetch(() => getProducts(query), [JSON.stringify(query)])

  return (
    <section className="home-section container">
      <div className="section-head">
        <div>
          <h2 className="section-title">{title}</h2>
          {intro && <p className="section-intro">{intro}</p>}
        </div>
        <Link to={shopLink} className="text-link">{shopLabel} →</Link>
      </div>
      {loading && <div className="row-skeleton" aria-label="Loading products" />}
      {error && <p className="alert alert-error">Couldn't load products: {error}</p>}
      {data && (
        <div className="product-row">
          {data.map((p) => (
            <ProductCard key={p.product_id} product={p} showDescription={false} />
          ))}
        </div>
      )}
    </section>
  )
}
