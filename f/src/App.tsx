
import "./App.css"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import Register from "./pages/Register"
import { AuthProvider } from "./context/AuthContext"
import ImageUpload from "./pages/ImageUpload"

export default function App() {
  return (
    <>
        <ImageUpload />
        
        <BrowserRouter>
      <AuthProvider>
        <Routes>
      
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>

    </>
  )
    
}