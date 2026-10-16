import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'

export default function Register() {
  const [notice, setNotice] = useState('')

  function submit(event: FormEvent) {
    event.preventDefault()
    // Accounts are wired to the backend in a later problem.
    setNotice('Account creation is being connected to the shop. Check back soon!')
  }

  return (
    <div className="page container auth">
      <h1>Create account</h1>
      <p className="muted">One account saves your chats and gets you to checkout faster.</p>
      <form className="form" onSubmit={submit}>
        <div className="form-row">
          <div>
            <label htmlFor="first_name">First name</label>
            <input id="first_name" autoComplete="given-name" required />
          </div>
          <div>
            <label htmlFor="last_name">Last name</label>
            <input id="last_name" autoComplete="family-name" required />
          </div>
        </div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" autoComplete="email" required />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" autoComplete="new-password" minLength={8} required aria-describedby="pw-hint" />
        <small id="pw-hint" className="muted">At least 8 characters.</small>
        <button type="submit" className="btn btn-primary btn-block">Create account</button>
        {notice && <p className="alert alert-info" role="status">{notice}</p>}
      </form>
      <p className="auth-switch">Already have an account? <Link to="/login">Log in</Link></p>
    </div>
  )
}
