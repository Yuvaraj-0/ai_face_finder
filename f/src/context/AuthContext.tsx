import { createContext, useContext, useState, ReactNode } from "react"
import api from "../api/client"
import { useNavigate } from "react-router-dom"

type AuthContextType = {
  user: any
  login: (email: string, password: string) => Promise<void>
  register: (name:string,email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<any>(null)
  const navigate = useNavigate()

  // LOGIN
  const login = async (email: string, password: string) => {
    try {
      const res = await api.post("/login", { email, password })
      
      setUser(res.data.user || { email })
      navigate("/dashboard")
    } catch (err) {
      console.error(err)
      alert("Login failed")
    }
  }

  // REGISTER
  const register = async (name: string, email: string, password: string) => {
  try {
    const requestBody = {
      name,
      email,
      password,
    };

    console.log("=== Register Request ===");
    console.log(requestBody);

    const res = await api.post("/register", requestBody);

    console.log("=== Register Response ===");
    console.log(res.data);

    setUser(res.data.user || { email });
    navigate("/dashboard");

  } catch (err: any) {
    console.log("=== Register Error ===");
    console.log("Status:", err.response?.status);
    console.log("Response:", err.response?.data);
    console.log("Request Sent:", {
      name,
      email,
      password,
    });

    console.error(err);
  }
};

  const logout = () => {
    setUser(null)
    navigate("/login")
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be inside AuthProvider")
  return ctx
}