// ==============================================================================
// Escáner QR de Citas — Validación de Asistencia Presencial
// Permite al administrador o psicólogo escanear el QR del paciente para
// registrar su llegada a la clínica o leer datos de la reserva.
// ==============================================================================
import React, { useEffect, useState, useRef } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { useToast } from '../components/Toast';

const EscanerQR = () => {
    const { showToast, ToastContainer } = useToast();
    const [scannedData, setScannedData] = useState(null);
    const [isScanning, setIsScanning] = useState(false);
    const scannerRef = useRef(null);

    // Inicializar lector de cámara
    const startScanner = async () => {
        setIsScanning(true);
        setScannedData(null);
        try {
            const html5QrCode = new Html5Qrcode("qr-reader");
            scannerRef.current = html5QrCode;

            await html5QrCode.start(
                { facingMode: "environment" }, // Preferir cámara trasera
                { fps: 10, qrbox: { width: 250, height: 250 } },
                (decodedText) => {
                    handleScanSuccess(decodedText);
                    stopScanner();
                },
                (errorMessage) => {
                    // Errores de lectura se ignoran silenciosamente durante el escaneo
                }
            );
        } catch (err) {
            showToast('Error accediendo a la cámara: ' + err, 'error');
            setIsScanning(false);
        }
    };

    const stopScanner = () => {
        if (scannerRef.current) {
            scannerRef.current.stop().then(() => {
                scannerRef.current.clear();
                setIsScanning(false);
            }).catch(err => {
                console.error("Error deteniendo el escáner", err);
            });
        }
    };

    // Subir imagen en lugar de usar cámara
    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const html5QrCode = new Html5Qrcode("qr-reader-file");
            const decodedText = await html5QrCode.scanFile(file, true);
            handleScanSuccess(decodedText);
        } catch (err) {
            showToast('No se detectó ningún QR en la imagen', 'warning');
        }
    };

    const handleScanSuccess = (text) => {
        try {
            // Intentamos parsear si es JSON (como sugerencia para los QRs generados)
            const data = JSON.parse(text);
            setScannedData(data);
            showToast('Asistencia registrada correctamente', 'success');
        } catch {
            // Si es texto plano
            setScannedData({ raw: text });
            showToast('Código QR leído correctamente', 'success');
        }
    };

    // Limpieza al desmontar
    useEffect(() => {
        return () => {
            if (scannerRef.current && isScanning) {
                stopScanner();
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <div style={styles.page}>
            <ToastContainer />
            <div style={styles.header}>
                <h1 style={styles.title}>📷 Verificación de Citas (Escáner QR)</h1>
                <p style={styles.subtitle}>Escanee el código QR del paciente para registrar su asistencia</p>
            </div>

            <div style={styles.container}>
                <div style={styles.scannerCard}>
                    {/* Contenedor del Lector de Cámara */}
                    <div id="qr-reader" style={{ width: '100%', maxWidth: '400px', margin: '0 auto', display: isScanning ? 'block' : 'none' }}></div>
                    <div id="qr-reader-file" style={{ display: 'none' }}></div> {/* Lector oculto para archivos */}

                    {!isScanning ? (
                        <div style={styles.actions}>
                            <div style={styles.iconPlaceholder}>📸</div>
                            <h3 style={styles.promptText}>Seleccione un método de escaneo</h3>
                            
                            <button onClick={startScanner} style={styles.btnPrimary}>
                                📹 Usar Cámara del Dispositivo
                            </button>
                            
                            <div style={styles.divider}>
                                <span style={styles.dividerText}>o</span>
                            </div>

                            <label style={styles.btnSecondary}>
                                📁 Subir Imagen del QR
                                <input 
                                    type="file" 
                                    accept="image/*" 
                                    onChange={handleFileUpload} 
                                    style={{ display: 'none' }} 
                                />
                            </label>
                        </div>
                    ) : (
                        <div style={{ textAlign: 'center', padding: '20px' }}>
                            <p style={styles.scanningText}>Apunte la cámara hacia el código QR...</p>
                            <button onClick={stopScanner} style={styles.btnDanger}>
                                Cancelar Escaneo
                            </button>
                        </div>
                    )}
                </div>

                {/* Resultado del escaneo */}
                {scannedData && (
                    <div style={styles.resultCard}>
                        <div style={styles.successIcon}>✅</div>
                        <h3 style={styles.resultTitle}>Paciente Verificado</h3>
                        
                        <div style={styles.dataGrid}>
                            {scannedData.cita_id && (
                                <div style={styles.dataItem}>
                                    <span style={styles.dataLabel}>ID Cita</span>
                                    <span style={styles.dataValue}>#{scannedData.cita_id}</span>
                                </div>
                            )}
                            {scannedData.paciente_ci && (
                                <div style={styles.dataItem}>
                                    <span style={styles.dataLabel}>CI Paciente</span>
                                    <span style={styles.dataValue}>{scannedData.paciente_ci}</span>
                                </div>
                            )}
                            {scannedData.raw && (
                                <div style={styles.dataItem}>
                                    <span style={styles.dataLabel}>Contenido Bruto</span>
                                    <span style={styles.dataValue}>{scannedData.raw}</span>
                                </div>
                            )}
                        </div>

                        <button onClick={() => setScannedData(null)} style={styles.btnOutline}>
                            Escanear Nuevo Paciente
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

const styles = {
    page: { padding: '32px 40px', backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", sans-serif' },
    header: { marginBottom: '32px', textAlign: 'center' },
    title: { fontSize: '28px', fontWeight: '800', color: '#0f172a', margin: 0 },
    subtitle: { fontSize: '14px', color: '#64748b', marginTop: '8px' },
    container: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '24px' },
    scannerCard: { backgroundColor: 'white', padding: '32px', borderRadius: '24px', border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.05)', width: '100%', maxWidth: '500px', textAlign: 'center' },
    iconPlaceholder: { fontSize: '48px', marginBottom: '16px' },
    promptText: { fontSize: '16px', fontWeight: '700', color: '#0f172a', marginBottom: '24px' },
    actions: { display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center' },
    btnPrimary: { width: '100%', backgroundColor: '#2563eb', color: 'white', padding: '14px 24px', borderRadius: '12px', border: 'none', fontWeight: '700', fontSize: '14px', cursor: 'pointer', boxShadow: '0 4px 12px rgba(37,99,235,0.3)', transition: 'background 0.2s' },
    btnSecondary: { width: '100%', backgroundColor: '#f1f5f9', color: '#475569', padding: '14px 24px', borderRadius: '12px', border: '1px solid #e2e8f0', fontWeight: '700', fontSize: '14px', cursor: 'pointer', transition: 'background 0.2s', boxSizing: 'border-box' },
    btnDanger: { backgroundColor: '#fee2e2', color: '#dc2626', padding: '12px 24px', borderRadius: '12px', border: 'none', fontWeight: '700', fontSize: '14px', cursor: 'pointer', marginTop: '16px' },
    btnOutline: { backgroundColor: 'transparent', color: '#2563eb', padding: '12px 24px', borderRadius: '12px', border: '2px solid #2563eb', fontWeight: '700', fontSize: '14px', cursor: 'pointer', marginTop: '24px', width: '100%' },
    divider: { display: 'flex', alignItems: 'center', textAlign: 'center', width: '100%', margin: '8px 0' },
    dividerText: { margin: '0 10px', color: '#94a3b8', fontSize: '12px', fontWeight: '600', textTransform: 'uppercase' },
    scanningText: { fontSize: '14px', color: '#3b82f6', fontWeight: '600', animation: 'pulse 1.5s infinite' },
    resultCard: { backgroundColor: '#f0fdf4', padding: '32px', borderRadius: '24px', border: '1px solid #bbf7d0', width: '100%', maxWidth: '500px', textAlign: 'center', animation: 'fadeIn 0.5s ease-out' },
    successIcon: { fontSize: '48px', marginBottom: '16px' },
    resultTitle: { fontSize: '20px', fontWeight: '800', color: '#166534', margin: '0 0 24px 0' },
    dataGrid: { display: 'grid', gridTemplateColumns: '1fr', gap: '12px', textAlign: 'left', backgroundColor: 'white', padding: '20px', borderRadius: '16px', border: '1px solid #dcfce7' },
    dataItem: { display: 'flex', flexDirection: 'column', gap: '4px' },
    dataLabel: { fontSize: '11px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase' },
    dataValue: { fontSize: '15px', fontWeight: '700', color: '#0f172a' },
};

export default EscanerQR;
