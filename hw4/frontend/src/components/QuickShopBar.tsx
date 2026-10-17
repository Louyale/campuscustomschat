import { Link, useLocation } from 'react-router-dom'

// Bold, always-visible shortcuts to the places shoppers go most (Problem 9, front-end improvement 1).
const LINKS = [
  { label: 'Best Sellers', to: '/products?sort=best-selling', match: 'sort=best-selling' },
  { label: 'Hoodies', to: '/products?category=Hoodies', match: 'category=Hoodies' },
  { label: 'Crewnecks', to: '/products?category=Crewnecks', match: 'category=Crewnecks' },
  { label: 'Tees', to: '/products?category=T-Shirts', match: 'category=T-Shirts' },
  { label: 'Hats', to: '/products?category=Hats', match: 'category=Hats' },
  { label: 'Accessories', to: '/products?group=Accessories', match: 'group=Accessories' },
  { label: 'Bulldog Athletics', to: '/products?collection=Bulldog%20Athletics', match: 'collection=Bulldog+Athletics' },
  { label: 'Low-Key Yale', to: '/products?collection=Low-Key%20Yale%20Gear', match: 'collection=Low-Key+Yale+Gear' },
]

export default function QuickShopBar() {
  const { pathname, search } = useLocation()
  const query = new URLSearchParams(search).toString()
  return (
    <nav className="quick-shop" aria-label="Shop by category">
      <ul className="container">
        {LINKS.map((link) => {
          const active = pathname === '/products' && query.includes(link.match)
          return (
            <li key={link.label}>
              <Link to={link.to} className={active ? 'active' : ''} aria-current={active ? 'page' : undefined}>
                {link.label}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
