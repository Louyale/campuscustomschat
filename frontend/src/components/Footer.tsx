import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <p className="footer-brand">Campus Customs</p>
          <p>Officially licensed Yale gear, printed to order and built to go the distance.</p>
        </div>
        <div>
          <h2>Shop</h2>
          <ul>
            <li><Link to="/products?category=Hoodies">Hoodies</Link></li>
            <li><Link to="/products?category=Hats">Hats</Link></li>
            <li><Link to="/products?collection=Residential%20Colleges">Residential Colleges</Link></li>
            <li><Link to="/products?collection=Low-Key%20Yale%20Gear">Low-Key Yale Gear</Link></li>
            <li><Link to="/products?collection=Family">Family</Link></li>
            <li><Link to="/products?sort=best-selling">Best sellers</Link></li>
          </ul>
        </div>
        <div>
          <h2>Visit</h2>
          <address>
            57 Broadway<br />New Haven, CT 06511<br />
            <a href="tel:+14753014205">(475) 301-4205</a><br />
            <a href="mailto:orderdept@campuscustoms.com">orderdept@campuscustoms.com</a>
          </address>
        </div>
        <div>
          <h2>Good to know</h2>
          <ul>
            <li>Made to order: 5–8 business days to print</li>
            <li>30-day returns on unworn items</li>
            <li><Link to="/about">About Campus Customs</Link></li>
          </ul>
        </div>
      </div>
      <p className="copyright container">
        © {new Date().getFullYear()} Yale Bulldog Blue by Campus Customs. Boola Boola.
        <span className="photo-credit">
          Handsome Dan photo:{' '}
          <a href="https://commons.wikimedia.org/wiki/File:Handsome_Dan_Kingman.jpg" target="_blank" rel="noreferrer">Joeshmonobody</a>,{' '}
          <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noreferrer">CC BY-SA 4.0</a>, via Wikimedia Commons (cropped).
        </span>
      </p>
    </footer>
  )
}
