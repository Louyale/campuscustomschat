// A slow-scrolling band of Yale cheers between home sections (Problem 10 motion). Pauses on hover;
// shoppers who ask for reduced motion see it standing still.
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
  const row = CHEERS.map((c) => <span key={c}>{c}<i aria-hidden="true">✦</i></span>)
  return (
    <div className="ticker" aria-label={CHEERS.join(', ')} role="marquee">
      <div className="ticker-track" aria-hidden="true">
        {row}
        {row}
      </div>
    </div>
  )
}
