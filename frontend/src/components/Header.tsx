import { useState, type FormEvent } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

type NavItem = { to: string; label: string; end?: boolean }

const NAV: NavItem[] = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]
const GUEST_NAV: NavItem[] = [
  { to: '/login', label: 'Log in' },
  { to: '/register', label: 'Create account' },
]

export default function Header() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const links: NavItem[] = user ? [...NAV, { to: '/account', label: `Hi, ${user.first_name}` }] : [...NAV, ...GUEST_NAV]

  function search(event: FormEvent) {
    event.preventDefault()
    const q = query.trim()
    navigate(q ? `/products?q=${encodeURIComponent(q)}` : '/products')
    setOpen(false)
  }

  return (
    <header className="site-header">
      <div className="announcement">Officially Licensed Yale Merchandise · 57 Broadway, New Haven</div>
      <div className="header-main container">
        <button
          className="menu-toggle"
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
          onClick={() => setOpen(!open)}
        >
          <span />
          <span />
          <span />
        </button>
        <Link to="/" className="logo" onClick={() => setOpen(false)}>
          <span className="logo-mark">Y</span>
          <span className="logo-text">
            <strong>Campus Customs</strong>
            <small>Yale Bulldog Blue</small>
          </span>
        </Link>
        <form className="header-search" role="search" onSubmit={search}>
          <label htmlFor="site-search" className="sr-only">Search products</label>
          <input
            id="site-search"
            type="search"
            placeholder="Search hoodies, colleges, sports…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" aria-label="Search">
            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
              <circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" strokeWidth="2" />
              <path d="M15.5 15.5 21 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </form>
      </div>
      <nav className={`site-nav ${open ? 'open' : ''}`} aria-label="Main">
        <ul className="container">
          {links.map((item) => (
            <li key={item.to}>
              <NavLink to={item.to} end={item.end} onClick={() => setOpen(false)}>
                {item.label}
              </NavLink>
            </li>
          ))}
          {user && (
            <li>
              <button
                className="nav-button"
                onClick={async () => {
                  await logout()
                  setOpen(false)
                  navigate('/')
                }}
              >
                Log out
              </button>
            </li>
          )}
        </ul>
      </nav>
    </header>
  )
}
