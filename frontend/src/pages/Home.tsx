import { Link } from 'react-router-dom'
import ProductRow from '../components/ProductRow'
import { openChat } from '../components/ChatWidget'
import { getProduct, money, productImage } from '../api'
import { useFetch } from '../useFetch'

const COLLECTIONS = [
  { name: 'Residential Colleges', blurb: 'Rep your college, from Benjamin Franklin to Trumbull.', image: productImage('pierson-college-crewneck') },
  { name: 'Sports', blurb: 'Gear for the varsity athlete and the bleacher regular.', image: productImage('yale-sports-hoodie-hockey') },
  { name: 'Family', blurb: 'Mom, Dad, Grandpa, Aunt: everyone gets a jersey.', image: productImage('yale-mom-crewneck') },
  { name: 'Graduate & Professional Schools', blurb: 'Law, Medicine, Music, Forestry and more.', image: productImage('yale-law-school-1-4-zip') },
]

export default function Home() {
  const game = useFetch(() => getProduct('2025-yale-vs-harvard-t-shirt'), [])

  return (
    <>
      <section className="hero">
        <div className="container hero-inner">
          <div className="hero-copy">
            <p className="eyebrow">New Haven · Est. on Broadway</p>
            <h1>Yale gear built for the long haul.</h1>
            <p>
              Lecture halls, late-night problem sets, a muddy loop around East Rock: good gear should
              keep up with all of it. Ours is officially licensed, printed to order, and made to be
              worn hard for years, not just for one Saturday in November.
            </p>
            <div className="hero-actions">
              <Link to="/products?sort=best-selling" className="btn btn-primary">Shop best sellers</Link>
              <Link to="/products?category=Hoodies" className="btn btn-outline-light">Find your hoodie</Link>
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
        <li><strong>Officially licensed</strong><span>The real Yale marks, done right</span></li>
        <li><strong>Printed to order</strong><span>Ready to ship in 5–8 business days</span></li>
        <li><strong>30-day returns</strong><span>Unworn, tags on, no drama</span></li>
        <li><strong>Honest answers</strong><span>Live price and stock in our chat</span></li>
      </ul>

      <ProductRow
        title="Best sellers"
        intro="The pieces Bulldogs keep coming back for. Proven on campus, tested by the weather."
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
          <p className="eyebrow">The Game · Yale vs. Harvard</p>
          <h2>One rivalry. One right answer.</h2>
          <p>
            Every November, Yale and Harvard meet on the field, and every November the facts are on
            our side: better colors, a better mascot, and a better fight song. Wear the 2025 edition
            of The Game tee to the tailgate, to class, or to your next family dinner with that one
            cousin who went to Cambridge.
          </p>
          {game.data && (
            <p className="feature-price">
              {game.data.name} · <strong>{money(game.data.price)}</strong>
            </p>
          )}
          <div className="hero-actions">
            <Link to="/products/2025-yale-vs-harvard-t-shirt" className="btn btn-primary">Shop The Game tee</Link>
          </div>
        </div>
      </section>

      <ProductRow
        title="Hoodie season is every season"
        intro="From a crisp October run to a February all-nighter in Sterling, a good hoodie is standard equipment."
        query={{ category: 'Hoodies', sort: 'best-selling', limit: '10' }}
        shopLink="/products?category=Hoodies"
        shopLabel="All hoodies"
      />

      <section className="dan container">
        <div className="dan-copy">
          <p className="eyebrow">Meet the boss</p>
          <h2>Handsome Dan approves.</h2>
          <p>
            Yale was the first school in America to adopt a live mascot, and Handsome Dan has been
            on the sidelines since 1889. He is undefeated at looking unimpressed, and he sets the
            standard for this shop: loyal, tough, a little stubborn, and always ready for a walk.
            Our vintage bulldog collection is our tribute to him.
          </p>
          <Link to="/products?collection=Bulldogs" className="btn btn-primary">Shop the bulldog collection</Link>
        </div>
        <div className="dan-images">
          <img src={productImage('district-vit-hoodie-vintage-bulldog')} alt="Vintage bulldog hoodie" />
          <img src={productImage('district-vit-hoodie-vintage-sailor-bulldog')} alt="Vintage sailor bulldog hoodie" />
        </div>
      </section>

      <section className="home-section container">
        <h2 className="section-title">Find your crew</h2>
        <p className="section-intro">Every Yalie belongs to a few teams. Start with yours.</p>
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

      <section className="hats container">
        <div>
          <p className="eyebrow">Hats off</p>
          <h2>Caps and beanies live at the shop.</h2>
          <p>
            Our hats aren't in the online catalog yet. Stop by 57 Broadway to try one on, or ask our
            chat what pairs best with the hoodie you're eyeing.
          </p>
        </div>
        <button className="btn btn-outline" onClick={() => openChat('What would pair well with a navy Yale hoodie?')}>
          Ask the chat
        </button>
      </section>

      <section className="visit container">
        <div>
          <h2 className="section-title">Come visit us</h2>
          <p>
            We're at <strong>57 Broadway, New Haven</strong>, steps from Old Campus and a short jog
            from Payne Whitney. Families on move-in weekend, alumni back for reunions, students who
            just need a warmer layer: the door is open.
          </p>
        </div>
        <address>
          57 Broadway, New Haven, CT 06511<br />
          <a href="tel:+14753014205">(475) 301-4205</a> · <a href="mailto:orderdept@campuscustoms.com">orderdept@campuscustoms.com</a>
        </address>
      </section>
    </>
  )
}
