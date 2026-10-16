import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="page container narrow">
      <h1>Off the trail</h1>
      <p>That page doesn't exist. Let's get you back on course.</p>
      <Link to="/" className="btn btn-primary">Back to home</Link>
    </div>
  )
}
