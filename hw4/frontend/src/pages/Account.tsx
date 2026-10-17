import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Account() {
  const { user, ready, logout } = useAuth()
  const navigate = useNavigate()
  const welcome = (useLocation().state as { welcome?: boolean } | null)?.welcome

  if (!ready) return <div className="page container"><p className="muted">Loading…</p></div>
  if (!user) return <Navigate to="/login" replace />

  return (
    <div className="page container auth">
      <h1>My account</h1>
      <p className="alert alert-info" role="status">
        {welcome ? `Welcome to Campus Customs, ${user.first_name}! Your account is ready.` : `Welcome back, ${user.first_name}!`}
      </p>
      <p className="muted">Your chats and account information are safely saved with Campus Customs.</p>
      <dl className="item-facts">
        <div><dt>Name</dt><dd>{user.first_name} {user.last_name}</dd></div>
        <div><dt>Email</dt><dd style={{ textTransform: 'none' }}>{user.email}</dd></div>
      </dl>
      <Link to="/products" className="btn btn-primary btn-block">Start shopping</Link>
      <button
        className="btn btn-outline btn-block"
        style={{ marginTop: 12 }}
        onClick={async () => {
          await logout()
          navigate('/')
        }}
      >
        Log out
      </button>
    </div>
  )
}
