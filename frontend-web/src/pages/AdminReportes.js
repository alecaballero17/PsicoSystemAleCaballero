import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import { dashboardStyles as styles } from '../styles/dashboardStyles';
import { useAuth } from '../context/AuthContext';

const AdminReportes = () => {
    const navigate = useNavigate();
    const { user, tenant } = useAuth();
    
    // Estados para el formulario de reportes
    const [tipoReporte, setTipoReporte] = useState('citas');
    const [fechaInicio, setFechaInicio] = useState(new Date().toISOString().split('T')[0]);
    const [fechaFin, setFechaFin] = useState(new Date().toISOString().split('T')[0]);
    const [loading, setLoading] = useState(false);

    // Función para descargar el Backup
    const handleDownloadBackup = async () => {
        try {
            const token = localStorage.getItem('userToken');
            const response = await fetch(`${authService.apiClient.defaults.baseURL}ia/backup/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Backup_${tenant.nombre}_${new Date().toLocaleDateString()}.json`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (error) {
            alert("Error al generar el backup.");
        }
    };

    // Función para generar el PDF de forma segura
    const handleGeneratePDF = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('userToken');
            const response = await fetch(`${authService.apiClient.defaults.baseURL}ia/reporte-pdf/?tipo=${tipoReporte}&start=${fechaInicio}&end=${fechaFin}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) throw new Error("Error en el servidor");

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        } catch (error) {
            console.error("Error:", error);
            alert("⚠️ No se pudo generar el PDF. Verifique su conexión o permisos.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.layout}>
            {/* Sidebar Reutilizado (Simplificado para brevedad) */}
            <aside style={styles.sidebar}>
                <div style={styles.brandContainer}>
                    <span style={styles.brandText}>PSICOSYSTEM ADMIN</span>
                </div>
                <nav style={styles.navSection}>
                    <div style={styles.navItem} onClick={() => navigate('/dashboard')}>⬅️ Volver al Dashboard</div>
                </nav>
            </aside>

            <main style={styles.main}>
                <header style={styles.header}>
                    <div style={styles.headerPath}>Administración / Reportes y Auditoría</div>
                </header>

                <div style={styles.content}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px' }}>
                        
                        {/* SECCIÓN 1: REPORTES PDF */}
                        <div style={styles.panelSection}>
                            <h3 style={styles.panelTitle}>📊 Generador de Reportes (PDF)</h3>
                            <p style={{ color: '#64748b', fontSize: '13px', marginBottom: '20px' }}>
                                Filtre la información por fechas para generar documentos oficiales.
                            </p>
                            
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                                <div>
                                    <label style={{ fontSize: '12px', fontWeight: 'bold', display: 'block', marginBottom: '5px' }}>TIPO DE REPORTE</label>
                                    <select 
                                        value={tipoReporte} 
                                        onChange={(e) => setTipoReporte(e.target.value)}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                                    >
                                        <option value="citas">Reporte de Citas Programadas</option>
                                        <option value="finanzas">Reporte de Ingresos (Módulo Financiero)</option>
                                    </select>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                                    <div>
                                        <label style={{ fontSize: '12px', fontWeight: 'bold' }}>FECHA INICIO</label>
                                        <input 
                                            type="date" 
                                            value={fechaInicio} 
                                            onChange={(e) => setFechaInicio(e.target.value)}
                                            style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                                        />
                                    </div>
                                    <div>
                                        <label style={{ fontSize: '12px', fontWeight: 'bold' }}>FECHA FIN</label>
                                        <input 
                                            type="date" 
                                            value={fechaFin} 
                                            onChange={(e) => setFechaFin(e.target.value)}
                                            style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                                        />
                                    </div>
                                </div>

                                <button 
                                    onClick={handleGeneratePDF}
                                    disabled={loading}
                                    style={{ ...styles.mainActionBtn, width: '100%', marginTop: '10px', padding: '15px', opacity: loading ? 0.7 : 1 }}
                                >
                                    {loading ? '⏳ GENERANDO DOCUMENTO...' : '📄 GENERAR REPORTE PDF'}
                                </button>
                            </div>
                        </div>

                        {/* SECCIÓN 2: BACKUPS Y AUDITORÍA */}
                        <div style={styles.panelSection}>
                            <h3 style={styles.panelTitle}>🛡️ Seguridad y Portabilidad</h3>
                            <p style={{ color: '#64748b', fontSize: '13px', marginBottom: '20px' }}>
                                Herramientas críticas para el cumplimiento de normativas de datos.
                            </p>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                <div style={{ padding: '15px', backgroundColor: '#f0fdf4', borderRadius: '12px', border: '1px solid #bbf7d0' }}>
                                    <h4 style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#166534' }}>📥 Importar / Restaurar Backup</h4>
                                    <p style={{ fontSize: '12px', color: '#166534', marginBottom: '15px' }}>
                                        Suba un archivo JSON para restaurar los datos de pacientes y configuración.
                                    </p>
                                    <input 
                                        type="file" 
                                        accept=".json"
                                        id="restore-file"
                                        style={{ display: 'none' }}
                                        onChange={async (e) => {
                                            const file = e.target.files[0];
                                            if (!file) return;
                                            
                                            const formData = new FormData();
                                            formData.append('file', file);
                                            
                                            try {
                                                const token = localStorage.getItem('userToken');
                                                const response = await fetch(`${authService.apiClient.defaults.baseURL}ia/restore/`, {
                                                    method: 'POST',
                                                    headers: { 'Authorization': `Bearer ${token}` },
                                                    body: formData
                                                });
                                                const result = await response.json();
                                                if (response.ok) alert("✅ Éxito: " + result.message);
                                                else alert("❌ Error: " + result.error);
                                            } catch (error) {
                                                alert("Error de conexión.");
                                            }
                                        }}
                                    />
                                    <button 
                                        onClick={() => document.getElementById('restore-file').click()}
                                        style={{ backgroundColor: '#22c55e', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
                                    >
                                        SELECCIONAR Y RESTAURAR
                                    </button>
                                </div>

                                <div style={{ padding: '15px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                                    <h4 style={{ margin: '0 0 5px 0', fontSize: '14px' }}>📦 Descargar Backup (JSON)</h4>
                                    <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '15px' }}>
                                        Descargue un volcado completo de pacientes, citas y finanzas para respaldo externo.
                                    </p>
                                    <button 
                                        onClick={handleDownloadBackup}
                                        style={{ backgroundColor: '#1e293b', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
                                    >
                                        DESCARGAR BACKUP
                                    </button>
                                </div>

                                <div style={{ padding: '15px', backgroundColor: '#fff7ed', borderRadius: '12px', border: '1px solid #fed7aa' }}>
                                    <h4 style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#9a3412' }}>📜 Bitácora de Auditoría</h4>
                                    <p style={{ fontSize: '12px', color: '#9a3412', marginBottom: '15px' }}>
                                        Revise quién ha modificado datos o accedido a información sensible.
                                    </p>
                                    <button 
                                        onClick={() => navigate('/admin/auditoria')}
                                        style={{ backgroundColor: '#f97316', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
                                    >
                                        VER LOGS DE ACCESO
                                    </button>
                                </div>

                                <div style={{ padding: '15px', backgroundColor: '#fef2f2', borderRadius: '12px', border: '1px solid #fee2e2', marginTop: '10px' }}>
                                    <h4 style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#991b1b' }}>💥 Simulación de Desastre</h4>
                                    <p style={{ fontSize: '12px', color: '#991b1b', marginBottom: '15px' }}>
                                        BORRA todos los datos de la clínica para probar la restauración.
                                    </p>
                                    <button 
                                        onClick={async () => {
                                            if (window.confirm("⚠️ ¿ESTÁS SEGURO? Esto borrará todos los pacientes y citas de esta clínica para la demo.")) {
                                                if (window.confirm("❗ ÚLTIMA ADVERTENCIA: ¿Tienes tu Backup descargado?")) {
                                                    try {
                                                        const token = localStorage.getItem('userToken');
                                                        const response = await fetch(`${authService.apiClient.defaults.baseURL}ia/panic-button/`, {
                                                            method: 'DELETE',
                                                            headers: { 'Authorization': `Bearer ${token}` }
                                                        });
                                                        if (response.ok) {
                                                            alert("💥 Desastre completado. La clínica está VACÍA.");
                                                            window.location.reload();
                                                        }
                                                    } catch (error) {
                                                        alert("Error al ejecutar la purga.");
                                                    }
                                                }
                                            }
                                        }}
                                        style={{ backgroundColor: '#dc2626', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
                                    >
                                        SIMULAR PÉRDIDA DE DATOS
                                    </button>
                                </div>
                            </div>
                        </div>

                    </div>

                    <p style={{ ...styles.technicalNote, textAlign: 'center', marginTop: '30px' }}>
                        * Todas las acciones de generación de reportes y backups son registradas automáticamente en la bitácora institucional.
                    </p>
                </div>
            </main>
        </div>
    );
};

export default AdminReportes;
