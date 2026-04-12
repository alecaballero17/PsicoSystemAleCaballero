export const dashboardStyles = {
    layout: { 
        display: 'flex', 
        height: '100vh', 
        backgroundColor: '#f1f5f9', 
        fontFamily: '"Inter", sans-serif' 
    },
    sidebar: { 
        width: '280px', 
        backgroundColor: '#0f172a', 
        color: 'white', 
        display: 'flex', 
        flexDirection: 'column', 
        padding: '24px' 
    },
    brandContainer: { 
        display: 'flex', 
        alignItems: 'center', 
        gap: '12px', 
        marginBottom: '40px' 
    },
    brandLogo: { 
        width: '32px', 
        height: '32px', 
        backgroundColor: '#3b82f6', 
        borderRadius: '8px' 
    },
    brandText: { 
        fontWeight: '800', 
        fontSize: '18px', 
        letterSpacing: '0.5px' 
    },
    brandVersion: { 
        fontSize: '10px', 
        color: '#64748b', 
        marginLeft: '4px' 
    },
    navSection: { 
        marginBottom: '32px' 
    },
    sectionLabel: { 
        fontSize: '11px', 
        fontWeight: '700', 
        color: '#475569', 
        marginBottom: '16px', 
        letterSpacing: '1px' 
    },
    navItem: { 
        padding: '12px 16px', 
        borderRadius: '12px', 
        color: '#94a3b8', 
        cursor: 'pointer', 
        marginBottom: '4px', 
        transition: 'all 0.2s', 
        fontSize: '14px' 
    },
    navItemActive: { 
        padding: '12px 16px', 
        borderRadius: '12px', 
        backgroundColor: '#1e293b', 
        color: '#3b82f6', 
        fontWeight: '600', 
        marginBottom: '4px', 
        fontSize: '14px' 
    },
    sidebarFooter: { 
        marginTop: 'auto', 
        paddingTop: '24px', 
        borderTop: '1px solid #1e293b' 
    },
    sessionInfo: { 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px', 
        fontSize: '12px', 
        color: '#64748b', 
        marginBottom: '16px' 
    },
    statusDot: { 
        width: '8px', 
        height: '8px', 
        backgroundColor: '#22c55e', 
        borderRadius: '50%' 
    },
    logoutBtn: { 
        width: '100%', 
        padding: '12px', 
        backgroundColor: '#ef444415', 
        color: '#ef4444', 
        border: 'none', 
        borderRadius: '12px', 
        cursor: 'pointer', 
        fontWeight: '600' 
    },
    main: { 
        flex: 1, 
        overflowY: 'auto', 
        display: 'flex', 
        flexDirection: 'column' 
    },
    header: { 
        height: '80px', 
        backgroundColor: 'white', 
        borderBottom: '1px solid #e2e8f0', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between', 
        padding: '0 40px' 
    },
    headerPath: { 
        fontSize: '13px', 
        color: '#64748b', 
        fontWeight: '500' 
    },
    headerUser: { 
        display: 'flex', 
        alignItems: 'center', 
        gap: '16px' 
    },
    userRoleTag: { 
        backgroundColor: '#f1f5f9', 
        color: '#475569', 
        padding: '4px 10px', 
        borderRadius: '6px', 
        fontSize: '11px', 
        fontWeight: '700' 
    },
    userName: { 
        fontWeight: '600', 
        color: '#1e293b' 
    },
    content: { 
        padding: '40px' 
    },
    kpiGrid: { 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: '24px', 
        marginBottom: '32px' 
    },
    kpiCard: { 
        backgroundColor: 'white', 
        padding: '24px', 
        borderRadius: '20px', 
        border: '1px solid #e2e8f0' 
    },
    kpiLabel: { 
        display: 'block', 
        fontSize: '11px', 
        fontWeight: '700', 
        color: '#64748b', 
        marginBottom: '12px' 
    },
    kpiValue: { 
        fontSize: '32px', 
        fontWeight: '800', 
        color: '#1e293b', 
        marginBottom: '4px' 
    },
    kpiSub: { 
        fontSize: '12px', 
        color: '#22c55e', 
        fontWeight: '600' 
    },
    panelSection: { 
        backgroundColor: 'white', 
        borderRadius: '24px', 
        border: '1px solid #e2e8f0', 
        padding: '32px' 
    },
    panelHeader: { 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '24px' 
    },
    panelTitle: { 
        fontSize: '16px', 
        fontWeight: '700', 
        color: '#1e293b' 
    },
    mainActionBtn: { 
        backgroundColor: '#2563eb', 
        color: 'white', 
        padding: '12px 20px', 
        borderRadius: '12px', 
        border: 'none', 
        fontWeight: '700', 
        fontSize: '13px', 
        cursor: 'pointer' 
    },
    tableContainer: { 
        overflowX: 'auto' 
    },
    table: { 
        width: '100%', 
        borderCollapse: 'collapse' 
    },
    tableHeader: { 
        borderBottom: '2px solid #f1f5f9', 
        textAlign: 'left' 
    },
    th: { 
        padding: '16px', 
        fontSize: '12px', 
        fontWeight: '700', 
        color: '#64748b', 
        textTransform: 'uppercase' 
    },
    tableRow: { 
        borderBottom: '1px solid #f1f5f9' 
    },
    td: { 
        padding: '16px', 
        fontSize: '14px', 
        color: '#64748b' 
    },
    tdBold: { 
        padding: '16px', 
        fontSize: '14px', 
        color: '#1e293b', 
        fontWeight: '700' 
    },
    statusActive: { 
        backgroundColor: '#dcfce7', 
        color: '#15803d', 
        padding: '4px 8px', 
        borderRadius: '6px', 
        fontSize: '11px', 
        fontWeight: '700' 
    },
    btnTable: { 
        padding: '6px 12px', 
        backgroundColor: '#f1f5f9', 
        border: 'none', 
        borderRadius: '6px', 
        fontSize: '12px', 
        fontWeight: '600', 
        color: '#475569', 
        cursor: 'pointer' 
    },
    btnDeleteBase: {
        padding: '8px',
        backgroundColor: '#fef2f2',
        color: '#ef4444',
        border: '1px solid #fee2e2',
        borderRadius: '8px',
        cursor: 'pointer',
        fontSize: '14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'all 0.2s',
        marginLeft: 'auto'
    },
    technicalNote: { 
        marginTop: '24px', 
        fontSize: '12px', 
        color: '#94a3b8', 
        fontStyle: 'italic' 
    }
};