import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import { roleLabel } from '../format'

export default function AccessDenied() {
  const { user } = useAuth()
  return (
    <div className="card" role="alert">
      <h1>Access denied</h1>
      <p>
        Your role{user ? ` (${roleLabel(user.role)})` : ''} is not allowed to open this page. Ask the owner if you
        need access.
      </p>
      <Link className="button" to="/">
        Back to the dashboard
      </Link>
    </div>
  )
}
