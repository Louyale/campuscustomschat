import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(email, password)
      navigate('/account', { replace: true })
    } catch (err) {
      setError((err as Error).message)
      setPassword('')
    } finally {
      setBusy(false)
    }
  }

  if (user) {
    return (
      <div className="page container auth">
        <h1>Log in</h1>
        <p className="alert alert-info">You're already logged in as {user.email}. Your chats and information are safely saved.</p>
        <Link to="/account" className="btn btn-primary btn-block">Go to my account</Link>
      </div>
    )
  }

  return (
    <div className="page container auth">
      <h1>Log in</h1>
      <p className="muted">Welcome back. Your chats and information are safely saved, so you can pick up where you left off.</p>
      <form className="form" onSubmit={submit} noValidate={false}>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        <button type="submit" className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
      </form>
      <p className="auth-switch">New here? <Link to="/register">Create an account</Link></p>
    </div>
  )
}
