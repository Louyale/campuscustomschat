import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'

export default function Login() {
  const [notice, setNotice] = useState('')

  function submit(event: FormEvent) {
    event.preventDefault()
    // Accounts are wired to the backend in a later problem.
    setNotice('Sign-in is being connected to the shop. Check back soon!')
  }

  return (
    <div className="page container auth">
      <h1>Log in</h1>
      <p className="muted">Welcome back. Pick up your chat where you left off.</p>
      <form className="form" onSubmit={submit}>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" autoComplete="email" required />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" autoComplete="current-password" required />
        <button type="submit" className="btn btn-primary btn-block">Log in</button>
        {notice && <p className="alert alert-info" role="status">{notice}</p>}
      </form>
      <p className="auth-switch">New here? <Link to="/register">Create an account</Link></p>
    </div>
  )
}
