import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/axiosConfig';

const GestionPacientes = () => {
    const [pacientes, setPacientes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [busqueda, setBusqueda] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetchPacientes();
    }, []);

    const fetchPacientes = async () => {
        try {
            const response = await apiClient.get('pacientes/');
            setPacientes(response.data);
        } catch (err) {
            console.error("Error al cargar pacientes", err);
        } finally {
            setLoading(false);
        }
    };

    const pacientesFiltrados = pacientes.filter(p => 
        p.nombre.toLowerCase().includes(busqueda.toLowerCase()) || 
        p.ci.includes(busqueda)
    );

    return (
        <div style={styles.container}>
            <header style={styles.header}>
                <h2 style={styles.title}>GESTIÓN DE PACIENTES (CU13)</h2>
                <button 
                    style={styles.btnPrimary}
                    onClick={() => navigate('/registro-paciente')}
                >
                    + NUEVO PACIENTE
                </button>
            </header>

            <div style={styles.searchBar}>
                <input 
                    type="text" 
                    placeholder="Buscar por nombre o CI..." 
                    style={styles.input}
                    value={busqueda}
                    onChange={(e) => setBusqueda(e.target.value)}
                />
            </div>

            {loading ? (
                <p>Cargando pacientes...</p>
            ) : (
                <div style={styles.tableCard}>
                    <table style={styles.table}>
                        <thead>
                            <tr style={styles.trHead}>
                                <th style={styles.th}>NOMBRE</th>
                                <th style={styles.th}>CI / IDENTIFICACIÓN</th>
                                <th style={styles.th}>TELÉFONO</th>
                                <th style={styles.th}>ACCIONES</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pacientesFiltrados.map(p => (
                                <tr key={p.id} style={styles.trBody}>
                                    <td style={styles.td}>{p.nombre}</td>
                                    <td style={styles.td}>{p.ci}</td>
                                    <td style={styles.td}>{p.telefono}</td>
                                    <td style={styles.td}>
                                        <button style={styles.btnAction} onClick={() => navigate(`/ia?paciente=${p.id}`)}>Diagnóstico IA</button>
                                        <button style={styles.btnActionSecondary}>Editar</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

const styles = {
    container: { padding: '40px', backgroundColor: '#f8fafc', minHeight: '100vh' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
    title: { margin: 0, color: '#0f172a', fontSize: '24px', fontWeight: 'bold' },
    btnPrimary: { padding: '12px 24px', backgroundColor: '#2563eb', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
    searchBar: { marginBottom: '20px' },
    input: { width: '100%', maxWidth: '400px', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1' },
    tableCard: { backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', overflow: 'hidden' },
    table: { width: '100%', borderCollapse: 'collapse' },
    trHead: { backgroundColor: '#f1f5f9', textAlign: 'left' },
    th: { padding: '15px', fontSize: '12px', fontWeight: 'bold', color: '#64748b' },
    trBody: { borderTop: '1px solid #f1f5f9' },
    td: { padding: '15px', fontSize: '14px', color: '#334155' },
    btnAction: { marginRight: '10px', padding: '6px 12px', backgroundColor: '#8b5cf6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
    btnActionSecondary: { padding: '6px 12px', backgroundColor: '#94a3b8', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }
};

export default GestionPacientes;
