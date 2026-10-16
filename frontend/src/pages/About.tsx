import { Link } from 'react-router-dom'
import { ABOUT } from '../content'

export default function About() {
  return (
    <div className="page container narrow">
      <nav className="breadcrumb" aria-label="Breadcrumb"><Link to="/">Home</Link> / About Us</nav>
      <h1>{ABOUT.title}</h1>
      <p className="lede">{ABOUT.lede}</p>

      {ABOUT.sections.map((section) => (
        <section key={section.heading} className="about-block">
          <h2>{section.heading}</h2>
          <p>{section.body}</p>
        </section>
      ))}

      <section className="about-block">
        <h2>{ABOUT.contact.heading}</h2>
        <p>{ABOUT.contact.body}</p>
        <address className="about-contact">
          <a href="tel:+14753014205">(475) 301-4205</a> ·{' '}
          <a href="mailto:orderdept@campuscustoms.com">orderdept@campuscustoms.com</a> · 57 Broadway, New Haven, CT 06511
        </address>
        <Link to="/products" className="btn btn-primary">{ABOUT.contact.button}</Link>
      </section>
    </div>
  )
}
