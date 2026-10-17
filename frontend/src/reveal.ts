// Scroll-in motion (Problem 10): sections fade up as they come into view. Content is visible by
// default; only sections still below the fold are hidden and then revealed, with a timed fallback
// so nothing can stay hidden if the browser never reports the scroll.
export function startReveal(root: ParentNode = document): () => void {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return () => {}
  const targets = [...root.querySelectorAll<HTMLElement>('[data-reveal]')]
    .filter((el) => el.getBoundingClientRect().top > window.innerHeight)
  targets.forEach((el) => el.classList.add('reveal-wait'))
  const show = (el: Element) => el.classList.remove('reveal-wait')
  const check = () => targets.forEach((el) => {
    if (el.getBoundingClientRect().top < window.innerHeight * 0.92) show(el)
  })
  window.addEventListener('scroll', check, { passive: true })
  const fallback = window.setTimeout(() => targets.forEach(show), 4000)
  return () => {
    window.removeEventListener('scroll', check)
    window.clearTimeout(fallback)
    targets.forEach(show)
  }
}
