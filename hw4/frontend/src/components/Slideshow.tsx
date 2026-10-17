import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Photo } from '../photoCredits'

interface Slide extends Photo {
  shop?: { label: string; to: string } // optional "Shop the look" link
}

interface Props {
  id: string
  eyebrow: string
  title: string
  intro: string
  slides: Slide[]
  interval?: number
}

const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

/**
 * Auto-advancing photo slideshow (Problem 10). Pauses on hover or focus, has prev/next and dots,
 * and does not auto-play for shoppers who ask for reduced motion.
 */
export default function Slideshow({ id, eyebrow, title, intro, slides, interval = 5500 }: Props) {
  const [index, setIndex] = useState(0)
  const [paused, setPaused] = useState(false)
  const count = slides.length
  const go = useCallback((n: number) => setIndex((n + count) % count), [count])

  useEffect(() => {
    if (paused || count < 2 || reducedMotion()) return
    const timer = window.setTimeout(() => go(index + 1), interval)
    return () => window.clearTimeout(timer)
  }, [index, paused, count, interval, go])

  if (count === 0) return null
  const slide = slides[index]

  return (
    <section className="slideshow container" aria-labelledby={`${id}-title`}>
      <div className="slideshow-head">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2 id={`${id}-title`} className="section-title">{title}</h2>
          <p className="section-intro">{intro}</p>
        </div>
        <div className="slideshow-arrows">
          <button type="button" onClick={() => go(index - 1)} aria-label="Previous photo">‹</button>
          <button type="button" onClick={() => setPaused(!paused)} aria-label={paused ? 'Play slideshow' : 'Pause slideshow'}>
            {paused ? '▶' : '❚❚'}
          </button>
          <button type="button" onClick={() => go(index + 1)} aria-label="Next photo">›</button>
        </div>
      </div>

      <div
        className="slideshow-stage"
        role="region"
        aria-roledescription="carousel"
        aria-label={title}
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
        onFocus={() => setPaused(true)}
      >
        {slides.map((s, i) => (
          <figure key={s.src} className={`slide${i === index ? ' is-active' : ''}`} aria-hidden={i !== index}
            aria-roledescription="slide" aria-label={`${i + 1} of ${count}`}>
            <img src={s.src} alt={s.alt} loading={i === 0 ? 'eager' : 'lazy'} />
            <figcaption>
              <strong>{s.caption}</strong>
              {s.shop && <Link to={s.shop.to} className="slide-shop" tabIndex={i === index ? 0 : -1}>{s.shop.label} →</Link>}
            </figcaption>
          </figure>
        ))}
        <span className="slide-count" aria-hidden="true">{index + 1} / {count}</span>
      </div>

      <div className="slideshow-foot">
        <div className="slideshow-dots" role="tablist" aria-label="Choose a photo">
          {slides.map((s, i) => (
            <button key={s.src} type="button" role="tab" aria-selected={i === index} aria-label={s.caption}
              className={i === index ? 'is-active' : ''} onClick={() => go(i)} />
          ))}
        </div>
        <p className="photo-credit">
          Photo: <a href={slide.source} target="_blank" rel="noreferrer">{slide.credit}</a>, {slide.license}, via Wikimedia Commons
        </p>
      </div>
    </section>
  )
}
