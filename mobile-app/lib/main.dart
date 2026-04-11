// [SPRINT 0 - T002] Stack Tecnológico: Flutter como framework móvil.
// [SPRINT 0 - T001] Arquitectura desacoplada: App móvil independiente del Backend.
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart'; // [SPRINT 0 - T004] [RNF-03] Variables de entorno
import 'screens/login_screen.dart'; // Importamos la primera pantalla

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Cargamos el archivo de configuración (Trazabilidad RNF-03)
  await dotenv.load(fileName: ".env");
  
  runApp(const PsicoSystemApp());
}

class PsicoSystemApp extends StatelessWidget {
  const PsicoSystemApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PsicoSystem Paciente',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFF1a2233), 
        scaffoldBackgroundColor: const Color(0xFFF0F4F8),
        colorScheme: ColorScheme.fromSwatch().copyWith(
          secondary: const Color(0xFF2563eb), 
        ),
        fontFamily: 'Roboto',
      ),
      home: const LoginScreen(), // Arrancamos directo en el Login
    );
  }
}