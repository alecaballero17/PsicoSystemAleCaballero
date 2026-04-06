import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext'; // <-- Importamos useAuth también

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import RegistroPaciente from './pages/RegistroPaciente';
import RegistroClinica from './pages/RegistroClinica';
import Navbar from './components/Navbar'; // Importa el Navbar

// ==============================================================================
// RUTAS PROTEGIDAS (RNF-03: Seguridad de Acceso)
// ==============================================================================
const PrivateRoute = ({ children, allowedRoles }) => {
    const { user } = useAuth(); // 👈 El guardia ahora escucha la radio oficial

    // Si no hay usuario en la RAM, patada al Login
    if (!user) {
        return <Navigate to="/" />;
    }

    // Si la ruta exige rol (ej. ADMIN) y el usuario no lo tiene, patada al Dashboard
    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to="/dashboard" />;
    }
    // 👇 AQUÍ ESTÁ LA MAGIA: Renderizamos el Navbar globalmente para rutas seguras
    return (
        <>
            <Navbar /> 
            {children}
        </>
    );
};    


// ==============================================================================
// ENRUTADOR PRINCIPAL
// ==============================================================================
function App() {
    return (
        <AuthProvider> 
            <Router>
                <Routes>
                    <Route path="/" element={<Login />} />
                    
                    <Route path="/dashboard" element={
                        <PrivateRoute>
                            <Dashboard />
                        </PrivateRoute>
                    } />

                    <Route path="/registro-paciente" element={
                        <PrivateRoute allowedRoles={['ADMIN', 'PSICOLOGO']}>
                            <RegistroPaciente />
                        </PrivateRoute>
                    } />

                    <Route path="/registro-clinica" element={
                        <PrivateRoute allowedRoles={['ADMIN']}>
                            <RegistroClinica />
                        </PrivateRoute>
                    } />

                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;