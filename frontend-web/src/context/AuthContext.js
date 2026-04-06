import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    // 🔥 EL TRUCO PRO: Carga síncrona inicial para evitar el "parpadeo" al dar F5
    const [user, setUser] = useState(() => {
        const token = localStorage.getItem('userToken');
        if (token) {
            return {
                token,
                role: localStorage.getItem('userRole'),
                name: localStorage.getItem('userName')
            };
        }
        return null;
    });

    useEffect(() => {
        const verifySession = async () => {
            if (user?.token) {
                // Verificación Real en Segundo Plano (Anti-huérfano)
                const validUser = await authService.getCurrentUser();
                
                if (!validUser) {
                    // ¡Peligro! Token falso o expirado en el backend
                    await authService.logout(); 
                    setUser(null);
                }
            }
        };

        verifySession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const login = (userData) => {
        setUser(userData); 
    };

    const logout = async () => {
        await authService.logout(); 
        setUser(null); 
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);