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
                name: localStorage.getItem('userName'),
                clinica_id: localStorage.getItem('clinica_id')
            };
        }
        return null;
    });

    const [tenant, setTenant] = useState({ nombre: 'PsicoSystem', logo: '' });

    useEffect(() => {
        const verifySession = async () => {
            if (user?.token) {
                // Verificación Real en Segundo Plano (Anti-huérfano)
                const validUser = await authService.getCurrentUser();
                
                if (!validUser) {
                    await authService.logout(); 
                    setUser(null);
                } else {
                    // [ALINEACIÓN RF-29] Carga inicial de metadatos del Tenant
                    try {
                        const response = await authService.apiClient.get('clinica/me/');
                        setTenant({
                            nombre: response.data.nombre,
                            logo: response.data.logo_url
                        });
                    } catch (e) {
                        console.error("Error cargando identidad del Tenant:", e);
                    }
                }
            }
        };

        verifySession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const updateTenant = (newInfo) => {
        setTenant({
            nombre: newInfo.nombre,
            logo: newInfo.logo_url || newInfo.logo
        });
    };

    const login = (userData) => {
        setUser(userData); 
    };

    const logout = async () => {
        await authService.logout(); 
        setUser(null); 
    };

    return (
        <AuthContext.Provider value={{ user, tenant, updateTenant, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);