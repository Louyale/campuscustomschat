import { useState } from 'react'

// A slow-scrolling band of Yale cheers between home sections (Problem 10 motion). It stops while the
// mouse is over it (and on a tap, for phones), with a "Paused" label in its own slot so shoppers can read a cheer.
// Shoppers who ask for reduced motion see it standing still.
const CHEERS = [
  'Boola Boola',
  'Bulldogs, Bulldogs, Bow Wow Wow',
  'For God, for Country and for Yale',
  'Lux et Veritas',
  'Handsome Dan approved',
  'Printed to order at 57 Broadway',
  'Beat Harvard',
]

export default function SpiritTicker() {
  const [paused, setPaused] = useState(false)
  const canHover = window.matchMedia('(hover: hover)').matches // phones get "Tap to pause"
  const row = CHEERS.map((c) => <span key={c}>{c}<i aria-hidden="true">✦</i></span>)
  return (
    <div
      className={`ticker${paused ? ' is-paused' : ''}`}
      aria-label={CHEERS.join(', ')}
      role="marquee"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onPointerUp={(e) => e.pointerType === 'touch' && setPaused((p) => !p)}
    >
      {/* Its own slot at the left, so the label never sits on a cheer. */}
      <strong className="ticker-state" aria-hidden="true">{paused ? '❚❚ Paused' : canHover ? 'Hover to pause' : 'Tap to pause'}</strong>
      <div className="ticker-window">
        <div className="ticker-track" aria-hidden="true">
          {row}
          {row}
        </div>
      </div>
    </div>
  )
}
