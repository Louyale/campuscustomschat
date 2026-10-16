import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const EMPTY = { first_name: '', last_name: '', email: '', password: '', confirm: '' }

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const set = (key: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setForm((prev) => ({ ...prev, [key]: value }))
  }
  const mismatch = form.confirm.length > 0 && form.confirm !== form.password

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('The passwords don’t match.')
      return
    }
    setBusy(true)
    try {
      const { confirm: _confirm, ...data } = form
      await register(data)
      navigate('/account', { replace: true, state: { welcome: true } })
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page container auth">
      <h1>Create account</h1>
      <p className="muted">One account safely saves your chats and information and gets you to checkout faster.</p>
      <form className="form" onSubmit={submit}>
        <div className="form-row">
          <div>
            <label htmlFor="first_name">First name</label>
            <input id="first_name" autoComplete="given-name" required maxLength={50} value={form.first_name} onChange={set('first_name')} />
          </div>
          <div>
            <label htmlFor="last_name">Last name</label>
            <input id="last_name" autoComplete="family-name" required maxLength={50} value={form.last_name} onChange={set('last_name')} />
          </div>
        </div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" autoComplete="email" required value={form.email} onChange={set('email')} />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" autoComplete="new-password" minLength={8} maxLength={128} required aria-describedby="pw-hint" value={form.password} onChange={set('password')} />
        <small id="pw-hint" className="muted">At least 8 characters, including a number. Avoid common passwords like “password”.</small>
        <label htmlFor="confirm">Confirm password</label>
        <input id="confirm" type="password" autoComplete="new-password" required aria-invalid={mismatch} aria-describedby="confirm-hint" value={form.confirm} onChange={set('confirm')} />
        {mismatch && <small id="confirm-hint" className="field-error">Passwords don’t match yet.</small>}
        {error && <p className="alert alert-error" role="alert">{error}</p>}
        <button type="submit" className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Creating account…' : 'Create account'}</button>
      </form>
      <p className="auth-switch">Already have an account? <Link to="/login">Log in</Link></p>
    </div>
  )
}
