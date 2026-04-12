import React from 'react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout, tenant } = useAuth(); 

    return (
        <nav style={{ padding: '10px 20px', background: '#1a2233', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {/* [ALINEACIÓN RNF-05] - Identidad de marca unificada: Diferenciación visual entre el Proveedor SaaS (PsicoSystem) y el Tenant activo (RF-29). */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '32px', height: '32px', background: '#2563eb', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '900', fontSize: '14px' }}>
                    PS
                </div>
                <h2 style={{ margin: 0, fontSize: '18px', letterSpacing: '1px', fontWeight: '800' }}>PSICOSYSTEM</h2>
            </div>
            {user && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center' }}>
                        <span style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 'bold' }}>
                            🏥 {tenant?.nombre || "Cargando Clínica..."}
                        </span>
                        <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                            👤 {user.name} ({user.role})
                        </span>
                    </div>
                    <button onClick={logout} style={{ padding: '8px 16px', background: '#dc2626', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold', transition: 'background 0.2s' }} onMouseOver={e => e.target.style.background = '#b91c1c'} onMouseOut={e => e.target.style.background = '#dc2626'}>
                        Cerrar Sesión
                    </button>
                </div>
            )}
        </nav>
    );
};

export default Navbar;