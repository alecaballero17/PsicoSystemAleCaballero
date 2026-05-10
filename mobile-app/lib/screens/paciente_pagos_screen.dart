import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class PacientePagosScreen extends StatelessWidget {
  const PacientePagosScreen({Key? key}) : super(key: key);

  final Color primaryBlue = const Color(0xFF2563EB);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text('Historial y Pagos', style: GoogleFonts.outfit(color: Colors.black87, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)]),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [BoxShadow(color: primaryBlue.withOpacity(0.3), blurRadius: 15, offset: const Offset(0, 8))],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Saldo Pendiente', style: GoogleFonts.outfit(color: Colors.white70, fontSize: 14)),
                      const Icon(Icons.account_balance_wallet, color: Colors.white),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('\$45.00', style: GoogleFonts.outfit(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        _simularPago(context);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: primaryBlue,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: Text('Pagar Ahora', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 16)),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            Text('Historial Reciente', style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0F172A))),
            const SizedBox(height: 16),
            _buildPagoItem('Consulta Psicológica', '12 May 2026', '\$45.00', true),
            _buildPagoItem('Terapia Familiar', '01 May 2026', '\$60.00', true),
            _buildPagoItem('Sesión General', '15 Abr 2026', '\$45.00', true),
          ],
        ),
      ),
    );
  }

  Widget _buildPagoItem(String concepto, String fecha, String monto, bool pagado) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(10)),
            child: const Icon(Icons.check_circle, color: Colors.green),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(concepto, style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 16)),
                Text(fecha, style: GoogleFonts.outfit(color: Colors.grey.shade500, fontSize: 12)),
              ],
            ),
          ),
          Text(monto, style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      ),
    );
  }

  void _simularPago(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Stripe Mock', style: GoogleFonts.outfit(color: primaryBlue, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.credit_card, size: 50, color: Colors.grey),
            const SizedBox(height: 16),
            Text('Se descontarán \$45.00 de tu tarjeta vinculada.', style: GoogleFonts.outfit(), textAlign: TextAlign.center),
          ],
        ),
        actions: [
          TextButton(
            child: const Text('Cancelar'),
            onPressed: () => Navigator.of(ctx).pop(),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: primaryBlue),
            child: const Text('Confirmar Pago', style: TextStyle(color: Colors.white)),
            onPressed: () {
              Navigator.of(ctx).pop();
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Pago simulado con éxito'), backgroundColor: Colors.green));
            },
          ),
        ],
      ),
    );
  }
}
