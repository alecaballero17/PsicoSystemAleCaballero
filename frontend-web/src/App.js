// ==============================================================================
// [SPRINT 1 + SPRINT 2] Enrutador Principal de PsicoSystem SI2
// [RF-28] Control de Acceso RBAC: PrivateRoute con validación de roles.
// [SPRINT 2] Nuevas rutas: Agenda, Citas, Historia Clínica, Finanzas, Reportes
// ==============================================================================
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// --- SPRINT 1: Páginas existentes ---
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import RegistroPaciente from './pages/RegistroPaciente';
import RegistroClinica from './pages/RegistroClinica';
import ConfiguracionClinica from './pages/ConfiguracionClinica';
import Navbar from './components/Navbar';
import RecuperarContrasena from './pages/RecuperarContrasena';
import GestionPersonal from './pages/GestionPersonal';
import SuscripcionInfo from './pages/SuscripcionInfo';
import Landing from './pages/Landing';

// --- SPRINT 2: Nuevas páginas ---
import AgendaCitas from './pages/AgendaCitas';
import GestionCitas from './pages/GestionCitas';
import HistoriaClinica from './pages/HistoriaClinica';
import Finanzas from './pages/Finanzas';
import ReportesFinancieros from './pages/ReportesFinancieros';
import ListaEspera from './pages/ListaEspera';
import EscanerQR from './pages/EscanerQR';

// ==============================================================================
// RUTAS PROTEGIDAS (RNF-03: Seguridad de Acceso)
// ==============================================================================
const PrivateRoute = ({ children, allowedRoles }) => {
    const { user } = useAuth();

    if (!user) {
        return <Navigate to="/" />;
    }

    // [RF-29] Bypass Global: Admin sin clínica solo puede registrar clínica
    if (user && (!user.clinica_id || user.clinica_id === "null" || user.clinica_id === "undefined") && user.role !== 'PACIENTE') {
        return <Navigate to="/registro-clinica" />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to="/dashboard" />;
    }

    return (
        <div className="app-layout">
            <Navbar />
            <div className="app-content-wrapper">
                {children}
            </div>
        </div>
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
                    {/* === RUTAS PÚBLICAS === */}
                    <Route path="/" element={<Landing />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/recuperar" element={<RecuperarContrasena />} />
                    <Route path="/registro-clinica" element={<RegistroClinica />} />

                    {/* === SPRINT 1: Rutas protegidas === */}
                    <Route path="/dashboard" element={
                        <PrivateRoute>
                            <Dashboard />
                        </PrivateRoute>
                    } />

                    <Route path="/registro-paciente" element={
                        <PrivateRoute allowedRoles={['PSICOLOGO', 'ADMIN']}>
                            <RegistroPaciente />
                        </PrivateRoute>
                    } />

                    <Route path="/gestion-personal" element={
                        <PrivateRoute allowedRoles={['ADMIN']}>
                            <GestionPersonal />
                        </PrivateRoute>
                    } />

                    <Route path="/configuracion-clinica" element={
                        <PrivateRoute allowedRoles={['ADMIN']}>
                            <ConfiguracionClinica />
                        </PrivateRoute>
                    } />

                    <Route path="/suscripcion" element={
                        <PrivateRoute allowedRoles={['ADMIN']}>
                            <SuscripcionInfo />
                        </PrivateRoute>
                    } />

                    {/* === SPRINT 2: Nuevas rutas protegidas === */}

                    {/* RF-08 / CU14: Agenda Dinámica — Calendario Interactivo */}
                    <Route path="/agenda" element={
                        <PrivateRoute allowedRoles={['PSICOLOGO', 'ADMIN']}>
                            <AgendaCitas />
                        </PrivateRoute>
                    } />

                    {/* RF-06/RF-07 / CU11/CU12/CU13: Gestión de Citas */}
                    <Route path="/gestion-citas" element={
                        <PrivateRoute allowedRoles={['PSICOLOGO', 'ADMIN']}>
                            <GestionCitas />
                        </PrivateRoute>
                    } />

                    {/* T026 / IA-01: Historia Clínica + Análisis IA */}
                    <Route path="/historia-clinica" element={
                        <PrivateRoute allowedRoles={['PSICOLOGO', 'ADMIN']}>
                            <HistoriaClinica />
                        </PrivateRoute>
                    } />

                    {/* RF-25/RF-26 / T058/T059 / CU26: Finanzas */}
                    <Route path="/finanzas" element={
                        <PrivateRoute allowedRoles={['PSICOLOGO', 'ADMIN']}>
                            <Finanzas />
                        </PrivateRoute>
                    } />

                    {/* RF-27: Reportes Económicos */}
                    <Route path="/reportes" element={
                        <PrivateRoute allowedRoles={['ADMIN']}>
                            <ReportesFinancieros />
                        </PrivateRoute>
                    } />

                    {/* T031: Lista de Espera */}
                    <Route path="/lista-espera" element={
                        <PrivateRoute allowedRoles={['PSICOLOGO', 'ADMIN']}>
                            <ListaEspera />
                        </PrivateRoute>
                    } />

                    {/* Escáner QR de Asistencia */}
                    <Route path="/escaner-qr" element={
                        <PrivateRoute allowedRoles={['PSICOLOGO', 'ADMIN']}>
                            <EscanerQR />
                        </PrivateRoute>
                    } />

                    {/* Catch-all */}
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;