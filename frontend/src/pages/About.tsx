import { Link } from 'react-router-dom'

export default function About() {
  return (
    <div className="page container narrow">
      <nav className="breadcrumb" aria-label="Breadcrumb"><Link to="/">Home</Link> / About Us</nav>
      <h1>About Campus Customs</h1>
      <p className="lede">
        We make Yale gear the way a good brief gets written: clear, well made, and with nothing extra
        that doesn't need to be there.
      </p>

      <section className="about-block">
        <h2>Who we are</h2>
        <p>
          Campus Customs runs Yale Bulldog Blue out of a shop at 57 Broadway in New Haven, a few blocks
          from Old Campus. Everything we sell is officially licensed by Yale. That matters to us, and it
          should matter to you: the crest is right, the colors are right, and part of every purchase
          goes back to the university.
        </p>
      </section>

      <section className="about-block">
        <h2>How we work</h2>
        <p>
          Most of what we sell is printed to order. That means less waste, a fuller range of sizes, and a
          shirt that hasn't been sitting in a warehouse since the last Harvard game. Printing takes 5–8
          business days, and shipping comes after that. We would rather give you an honest date than a
          fast promise we can't keep.
        </p>
      </section>

      <section className="about-block">
        <h2>Who it's for</h2>
        <p>
          Students running from Sterling to section. Parents who want to wear their pride to the
          grocery store back home. Grandparents, aunts and cousins (yes, there's a shirt for that).
          Grad students in Law, Medicine, Music and Forestry. Alumni who still know all the words to
          "Boola Boola." If you love this place, you belong here.
        </p>
      </section>

      <section className="about-block">
        <h2>Built for the long run</h2>
        <p>
          Good gear is like good training: it shows up in October, January and May without complaint. We
          pick blanks that hold their shape after a hundred washes and keep you warm on a windy walk up
          Science Hill. If something isn't right, you have 30 days to return unworn items with the tags
          on, and we'll make it right.
        </p>
      </section>

      <section className="about-block">
        <h2>Ask us anything</h2>
        <p>
          Our chat assistant gives straight answers on price, sizes and stock, pulled from our own
          inventory. For anything else, call <a href="tel:+14753014205">(475) 301-4205</a>, email{' '}
          <a href="mailto:orderdept@campuscustoms.com">orderdept@campuscustoms.com</a>, or just come by
          the shop.
        </p>
        <Link to="/products" className="btn btn-primary">Browse the shop</Link>
      </section>
    </div>
  )
}
