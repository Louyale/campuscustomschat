import { useSearchParams, Link } from 'react-router-dom'
import { getFacets, getProducts } from '../api'
import { useFetch } from '../useFetch'
import ProductCard from '../components/ProductCard'

const SORTS = [
  { value: 'featured', label: 'Featured' },
  { value: 'best-selling', label: 'Best selling' },
  { value: 'price-asc', label: 'Price, low to high' },
  { value: 'price-desc', label: 'Price, high to low' },
  { value: 'name-asc', label: 'Alphabetically, A–Z' },
  { value: 'name-desc', label: 'Alphabetically, Z–A' },
]

const FILTER_KEYS = ['q', 'category', 'collection', 'in_stock', 'min_price', 'max_price', 'sort'] as const

export default function Products() {
  const [params, setParams] = useSearchParams()
  const query = Object.fromEntries(FILTER_KEYS.map((k) => [k, params.get(k) ?? ''])) as Record<(typeof FILTER_KEYS)[number], string>
  const facets = useFetch(getFacets, [])
  const products = useFetch(() => getProducts(query), [params.toString()])

  function update(key: string, value: string) {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else next.delete(key)
    setParams(next, { replace: true })
  }

  const heading = query.q ? `Search results for “${query.q}”` : query.collection || query.category || 'All products'
  const active = FILTER_KEYS.filter((k) => k !== 'sort' && query[k])

  return (
    <div className="page container">
      <nav className="breadcrumb" aria-label="Breadcrumb"><Link to="/">Home</Link> / Products</nav>
      <div className="products-head">
        <h1>{heading}</h1>
        <div className="sort">
          <label htmlFor="sort">Sort by</label>
          <select id="sort" value={query.sort || 'featured'} onChange={(e) => update('sort', e.target.value)}>
            {SORTS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>
      </div>

      <div className="products-layout">
        <aside className="filters" aria-label="Filters">
          <h2>Filters</h2>

          <fieldset>
            <legend>Category</legend>
            <FilterOption label="All" checked={!query.category} onChange={() => update('category', '')} name="category" />
            {facets.data?.categories.map((c) => (
              <FilterOption key={c.name} label={`${c.name} (${c.count})`} checked={query.category === c.name} onChange={() => update('category', c.name)} name="category" />
            ))}
          </fieldset>

          <fieldset>
            <legend>Collection</legend>
            <FilterOption label="All" checked={!query.collection} onChange={() => update('collection', '')} name="collection" />
            {facets.data?.collections.map((c) => (
              <FilterOption key={c.name} label={`${c.name} (${c.count})`} checked={query.collection === c.name} onChange={() => update('collection', c.name)} name="collection" />
            ))}
          </fieldset>

          <fieldset>
            <legend>Availability</legend>
            <label className="check">
              <input type="checkbox" checked={query.in_stock === 'true'} onChange={(e) => update('in_stock', e.target.checked ? 'true' : '')} />
              In stock only
            </label>
          </fieldset>

          <fieldset>
            <legend>Price</legend>
            <div className="price-range">
              <label>From $<input type="number" min="0" inputMode="decimal" value={query.min_price} onChange={(e) => update('min_price', e.target.value)} aria-label="Minimum price" /></label>
              <label>To $<input type="number" min="0" inputMode="decimal" value={query.max_price} onChange={(e) => update('max_price', e.target.value)} aria-label="Maximum price" /></label>
            </div>
          </fieldset>

          {active.length > 0 && (
            <button className="btn btn-outline btn-small" onClick={() => setParams(query.sort ? { sort: query.sort } : {})}>Clear filters</button>
          )}
        </aside>

        <section aria-live="polite">
          {products.loading && <p className="muted">Loading products…</p>}
          {products.error && <p className="alert alert-error">Couldn't load products: {products.error}</p>}
          {products.data && (
            <>
              <p className="muted result-count">{products.data.length} {products.data.length === 1 ? 'product' : 'products'}</p>
              {products.data.length === 0 ? (
                <p className="empty">Nothing matches that yet. Try a broader search, or ask the chat for a suggestion.</p>
              ) : (
                <div className="product-grid">
                  {products.data.map((p) => <ProductCard key={p.product_id} product={p} />)}
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  )
}

function FilterOption({ label, checked, onChange, name }: { label: string; checked: boolean; onChange: () => void; name: string }) {
  return (
    <label className="check">
      <input type="radio" name={name} checked={checked} onChange={onChange} />
      {label}
    </label>
  )
}
