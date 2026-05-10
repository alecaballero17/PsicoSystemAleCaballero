// ==============================================================================
// [SPRINT 1 + SPRINT 2] Enrutador Principal de PsicoSystem SI2
// [RF-28] Control de Acceso RBAC: PrivateRoute con validación de roles.
// [SPRINT 2] Nuevas rutas: Agenda, Citas, Historia Clínica, Finanzas, Reportes
// ==============================================================================
import React, { useState } from 'react';
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
import { SuscripcionInfo } from './pages/SuscripcionInfo';
import BitacoraAudit from './pages/BitacoraAudit';
import CambiarPassword from './pages/CambiarPassword';
import Landing from './pages/Landing';

// --- SPRINT 2: Nuevas páginas ---
import AgendaCitas from './pages/AgendaCitas';
import GestionCitas from './pages/GestionCitas';
import HistoriaClinica from './pages/HistoriaClinica';
import Finanzas from './pages/Finanzas';
import ReportesFinancieros from './pages/ReportesFinancieros';
import ListaEspera from './pages/ListaEspera';
import EscanerQR from './pages/EscanerQR';
import GlobalSidebar from './components/GlobalSidebar';

import MainLayout from './MainLayout';

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

                    {/* === RUTAS PROTEGIDAS (Layout unificado) === */}
                    <Route element={<MainLayout />}>
                        <Route path="/dashboard" element={<Dashboard />} />
                    </Route>

                    <Route element={<MainLayout allowedRoles={['PSICOLOGO', 'ADMIN']} />}>
                        <Route path="/registro-paciente" element={<RegistroPaciente />} />
                        <Route path="/agenda" element={<AgendaCitas />} />
                        <Route path="/gestion-citas" element={<GestionCitas />} />
                        <Route path="/historia-clinica" element={<HistoriaClinica />} />
                        <Route path="/lista-espera" element={<ListaEspera />} />
                        <Route path="/escaner-qr" element={<EscanerQR />} />
                        <Route path="/finanzas" element={<Finanzas />} />
                    </Route>

                    <Route element={<MainLayout allowedRoles={['ADMIN']} />}>
                        <Route path="/gestion-personal" element={<GestionPersonal />} />
                        <Route path="/configuracion-clinica" element={<ConfiguracionClinica />} />
                        <Route path="/suscripcion" element={<SuscripcionInfo />} />
                        <Route path="/bitacora" element={<BitacoraAudit />} />
                        <Route path="/cambiar-password" element={<CambiarPassword />} />
                        <Route path="/reportes" element={<ReportesFinancieros />} />
                    </Route>

                    {/* Catch-all */}
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;