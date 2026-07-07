import { useState } from "react"
import { useAuth } from "../context/AuthContext"

export default function Register() {
  const { register } = useAuth()
  const [name,setName] = useState<string>("")
  const [email, setEmail] = useState<string>("")
  const [password, setPassword] = useState<string>("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    register(name,email, password)
  }

  return (
    <div className="h-screen flex items-center justify-center bg-gray-100">
      <div className="w-96 bg-white p-6 rounded shadow">
        <h2 className="text-xl font-bold mb-4">Register</h2>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input type="text" placeholder="username"
          className="w-full border p-2 rounded"
            value={name}
            onChange={(e) => setName(e.target.value)} />
          <input
            className="w-full border p-2 rounded"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            className="w-full border p-2 rounded"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="w-full bg-green-500 text-white p-2 rounded">
            Register
          </button>
          <a href="/login">Login</a>
        </form>
      </div>
    </div>
  )
}