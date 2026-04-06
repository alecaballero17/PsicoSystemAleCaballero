import React from 'react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useAuth(); // Usamos el contexto global que armaste

    return (
        <nav style={{ padding: '15px', background: '#1a2233', color: 'white', display: 'flex', justifyContent: 'space-between' }}>
            <h2>PsicoSystem SI2</h2>
            {user && (
                <div>
                    <span style={{ marginRight: '15px' }}>👤 {user.name} ({user.role})</span>
                    <button onClick={logout} style={{ padding: '5px 10px', background: '#dc2626', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
                        Cerrar Sesión
                    </button>
                </div>
            )}
        </nav>
    );
};

export default Navbar;