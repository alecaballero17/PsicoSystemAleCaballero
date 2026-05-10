import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import GlobalSidebar from './GlobalSidebar';

const Navbar = ({ onToggleSidebar }) => {
    const { user, logout, tenant } = useAuth(); 

    return (
        <nav style={{ 
            padding: '10px 20px', 
            background: '#1a2233', 
            color: 'white', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            zIndex: 1100, 
            position: 'sticky',
            top: 0,
            boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {user && (
                    <button 
                        onClick={onToggleSidebar}
                        style={{ 
                            background: '#2563eb', 
                            border: 'none', 
                            color: 'white', 
                            fontSize: '20px', 
                            cursor: 'pointer', 
                            borderRadius: '8px',
                            width: '40px',
                            height: '40px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        ☰
                    </button>
                )}
                
                <a href="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none', color: 'white' }}>
                    <div style={{ width: '32px', height: '32px', background: '#2563eb', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '900', fontSize: '14px' }}>
                        PS
                    </div>
                    <h2 style={{ margin: 0, fontSize: '18px', letterSpacing: '1px', fontWeight: '800' }}>PSICOSYSTEM</h2>
                </a>
            </div>
            
            {user && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center' }}>
                        <span style={{ color: '#e2e8f0', fontSize: '14px', fontWeight: 'bold' }}>
                            🏥 {tenant?.nombre || "PsicoSystem"}
                        </span>
                        <span style={{ color: '#94a3b8', fontSize: '12px' }}>
                            👤 {user.name}
                        </span>
                    </div>
                    <button onClick={() => {
                        if (window.confirm('¿Está seguro que desea cerrar sesión?')) {
                            logout();
                        }
                    }} style={{ padding: '8px 16px', background: '#dc2626', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}>
                        Cerrar Sesión
                    </button>
                </div>
            )}
        </nav>
    );
};

export default Navbar;