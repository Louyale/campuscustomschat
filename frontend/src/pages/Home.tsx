import { Link } from 'react-router-dom'
import ProductRow from '../components/ProductRow'
import { getProduct, money, productImage } from '../api'
import { useFetch } from '../useFetch'
import { HOME } from '../content'

const COLLECTIONS = [
  { name: 'Residential Colleges', blurb: HOME.findYourCrew.residentialColleges, image: productImage('pierson-college-crewneck') },
  { name: 'Bulldog Athletics', blurb: HOME.findYourCrew.sports, image: productImage('yale-sports-hoodie-hockey') },
  { name: 'Family', blurb: HOME.findYourCrew.family, image: productImage('yale-mom-crewneck') },
  { name: 'Graduate & Professional Schools', blurb: HOME.findYourCrew.gradSchools, image: productImage('school-of-management-crest-t-shirt') },
]

export default function Home() {
  const game = useFetch(() => getProduct('2025-yale-vs-harvard-t-shirt'), [])

  return (
    <>
      <section className="hero">
        <div className="container hero-inner">
          <div className="hero-copy">
            <p className="eyebrow">{HOME.hero.eyebrow}</p>
            <h1>{HOME.hero.title}</h1>
            <p className="hero-lede">{HOME.hero.lede}</p>
            <p>{HOME.hero.body}</p>
            <div className="hero-actions">
              <Link to="/products?sort=best-selling" className="btn btn-primary">{HOME.hero.primaryButton}</Link>
              <Link to="/products?category=Hoodies" className="btn btn-outline-light">{HOME.hero.secondaryButton}</Link>
            </div>
          </div>
          <div className="hero-images" aria-hidden="true">
            <img src={productImage('basic-hoodie-big-yale')} alt="" />
            <img src={productImage('district-vit-crewneck-vintage-standing-bulldog')} alt="" />
            <img src={productImage('poly-twill-crewneck-arched-yale')} alt="" />
          </div>
        </div>
      </section>

      <ul className="trust-bar container" aria-label="Why shop with us">
        {HOME.trustBar.map((item) => (
          <li key={item.title}><strong>{item.title}</strong><span>{item.text}</span></li>
        ))}
      </ul>

      <ProductRow
        title={HOME.bestSellers.title}
        intro={HOME.bestSellers.intro}
        query={{ sort: 'best-selling', limit: '10' }}
        shopLink="/products?sort=best-selling"
      />

      <section className="feature container">
        {game.data && (
          <Link to={`/products/${game.data.product_id}`} className="feature-image">
            <img src={game.data.image_url} alt={game.data.name} />
          </Link>
        )}
        <div className="feature-copy">
          <p className="eyebrow">{HOME.theGame.eyebrow}</p>
          <h2>{HOME.theGame.title}</h2>
          <p>{HOME.theGame.body}</p>
          {game.data && (
            <p className="feature-price">
              {game.data.name} · <strong>{money(game.data.price)}</strong>
            </p>
          )}
          <div className="hero-actions">
            <Link to="/products/2025-yale-vs-harvard-t-shirt" className="btn btn-primary">{HOME.theGame.button}</Link>
          </div>
        </div>
      </section>

      <ProductRow
        title={HOME.hoodies.title}
        intro={HOME.hoodies.intro}
        query={{ category: 'Hoodies', sort: 'best-selling', limit: '10' }}
        shopLink="/products?category=Hoodies"
        shopLabel="All hoodies"
      />

      <section className="dan container">
        <div className="dan-copy">
          <p className="eyebrow">{HOME.handsomeDan.eyebrow}</p>
          <h2>{HOME.handsomeDan.title}</h2>
          <p>{HOME.handsomeDan.body}</p>
          <Link to="/products?collection=Bulldogs" className="btn btn-primary">{HOME.handsomeDan.button}</Link>
        </div>
        <div className="dan-images">
          <img src={productImage('district-vit-hoodie-vintage-bulldog')} alt="Vintage bulldog hoodie" />
          <img src={productImage('district-vit-hoodie-vintage-sailor-bulldog')} alt="Vintage sailor bulldog hoodie" />
        </div>
      </section>

      <section className="home-section container">
        <h2 className="section-title">{HOME.findYourCrew.title}</h2>
        <p className="section-intro">{HOME.findYourCrew.intro}</p>
        <div className="collection-grid">
          {COLLECTIONS.map((c) => (
            <Link key={c.name} to={`/products?collection=${encodeURIComponent(c.name)}`} className="collection-tile">
              <img src={c.image} alt="" loading="lazy" />
              <div>
                <h3>{c.name}</h3>
                <p>{c.blurb}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <ProductRow
        title={HOME.hats.title}
        intro={HOME.hats.intro}
        query={{ category: 'Hats', sort: 'best-selling' }}
        shopLink="/products?category=Hats"
        shopLabel="All hats"
      />

      <section className="visit container">
        <div>
          <h2 className="section-title">{HOME.visit.title}</h2>
          <p>{HOME.visit.body}</p>
        </div>
        <address>
          57 Broadway, New Haven, CT 06511<br />
          <a href="tel:+14753014205">(475) 301-4205</a> · <a href="mailto:orderdept@campuscustoms.com">orderdept@campuscustoms.com</a>
        </address>
      </section>
    </>
  )
}
