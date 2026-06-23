import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_fonts/google_fonts.dart';
import 'services/firebase_service.dart';
import 'screens/login_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Cargamos el archivo de configuración
  await dotenv.load(fileName: ".env");
  
  // 🔥 Inicializar Firebase para Notificaciones Push (RF-09)
  await FirebaseService.initialize();
  
  runApp(const PsicoSystemApp());
}

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

class PsicoSystemApp extends StatefulWidget {
  const PsicoSystemApp({Key? key}) : super(key: key);

  @override
  _PsicoSystemAppState createState() => _PsicoSystemAppState();
}

class _PsicoSystemAppState extends State<PsicoSystemApp> {
  Timer? _inactivityTimer;
  final int _timeoutMinutes = 7;

  @override
  void initState() {
    super.initState();
    _startInactivityTimer();
  }

  void _startInactivityTimer() {
    _inactivityTimer?.cancel();
    _inactivityTimer = Timer(Duration(minutes: _timeoutMinutes), _forceLogoutDueToInactivity);
  }

  void _userInteracted() {
    _startInactivityTimer();
  }

  void _forceLogoutDueToInactivity() {
    // Navigate back to LoginScreen and clear stack
    if (navigatorKey.currentState != null && navigatorKey.currentState!.canPop()) {
      navigatorKey.currentState!.pushAndRemoveUntil(
        MaterialPageRoute(builder: (context) => const LoginScreen()),
        (route) => false,
      );
      ScaffoldMessenger.of(navigatorKey.currentContext!).showSnackBar(
        const SnackBar(
          content: Text('Tu sesión ha expirado por inactividad.'),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Listener(
      onPointerDown: (_) => _userInteracted(),
      onPointerMove: (_) => _userInteracted(),
      onPointerUp: (_) => _userInteracted(),
      behavior: HitTestBehavior.translucent,
      child: MaterialApp(
        navigatorKey: navigatorKey,
        title: 'PsicoSystem Paciente',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF2563EB),
            primary: const Color(0xFF2563EB),
            secondary: const Color(0xFF0F172A),
          ),
          textTheme: GoogleFonts.outfitTextTheme(),
        ),
        home: const LoginScreen(),
      ),
    );
  }
}