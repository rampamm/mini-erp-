import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="card">
      <h1>Page not found</h1>
      <p>That page does not exist.</p>
      <Link className="button" to="/">
        Back to the dashboard
      </Link>
    </div>
  )
}
