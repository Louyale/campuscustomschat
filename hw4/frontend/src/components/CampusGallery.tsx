import { useEffect, useState } from 'react'
import type { Photo } from '../photoCredits'

interface Props {
  photos: Photo[]
}

/**
 * "Postcards from campus" (Problem 10): a mosaic of Yale campus photos. Click one to open it
 * large; Esc or the arrows move through them.
 */
export default function CampusGallery({ photos }: Props) {
  const [open, setOpen] = useState<number | null>(null)

  useEffect(() => {
    if (open === null) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(null)
      if (e.key === 'ArrowRight') setOpen((open + 1) % photos.length)
      if (e.key === 'ArrowLeft') setOpen((open - 1 + photos.length) % photos.length)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, photos.length])

  if (photos.length === 0) return null
  const big = open === null ? null : photos[open]

  return (
    <section className="campus container" aria-labelledby="campus-title">
      <p className="eyebrow">New Haven, CT · since 1701</p>
      <h2 id="campus-title" className="section-title">Postcards from campus</h2>
      <p className="section-intro">The places our gear goes: under Harkness, up the steps of Sterling, out to The Bowl. Tap a postcard to see it big.</p>
      <div className="campus-grid">
        {photos.map((p, i) => (
          <button key={p.src} type="button" className="postcard" onClick={() => setOpen(i)} aria-label={`Open photo: ${p.caption}`}>
            <img src={p.src} alt={p.alt} loading="lazy" />
            <span className="postcard-caption">{p.caption}</span>
          </button>
        ))}
      </div>
      <p className="photo-credit">
        Campus photos from Wikimedia Commons under open licenses; photographers are credited on each photo.
      </p>

      {big && (
        <div className="lightbox" role="dialog" aria-modal="true" aria-label={big.caption} onClick={() => setOpen(null)}>
          <figure onClick={(e) => e.stopPropagation()}>
            <img src={big.src} alt={big.alt} />
            <figcaption>
              <strong>{big.caption}</strong>
              <span>Photo: <a href={big.source} target="_blank" rel="noreferrer">{big.credit}</a>, {big.license}</span>
            </figcaption>
            <button type="button" className="lightbox-close" onClick={() => setOpen(null)} aria-label="Close photo" autoFocus>×</button>
            <button type="button" className="lightbox-prev" onClick={() => setOpen((open! - 1 + photos.length) % photos.length)} aria-label="Previous photo">‹</button>
            <button type="button" className="lightbox-next" onClick={() => setOpen((open! + 1) % photos.length)} aria-label="Next photo">›</button>
          </figure>
        </div>
      )}
    </section>
  )
}
