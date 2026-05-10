// [SPRINT 0 - T002] Stack Tecnológico: Flutter + flutter_dotenv.
// [SPRINT 0 - T008] Conectividad Base: Configuración centralizada de la URL del API.
// [SPRINT 0 - T004] Entorno de Desarrollo: IP configurable vía .env.
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  // [SPRINT 0 - T008] Base URL con salvavidas (fallback a IP local)
  static String get baseUrl => dotenv.env['API_URL'] ?? 'http://192.168.0.196:8000/api';

  // 2. Endpoints Dinámicos (Esto te ahorra errores de dedo al escribir URLs)
  static String get login => '$baseUrl/auth/login/';
  static String get pacientes => '$baseUrl/pacientes/';
  static String get pacientesRegistrar => '$baseUrl/pacientes/registrar/';
  static String get dashboard => '$baseUrl/dashboard/';
  static String get me => '$baseUrl/auth/me/';
  
  // [SPRINT 1 - T015] Endpoints Públicos de Autogestión
  static String get clinicas => '$baseUrl/clinicas/publicas/';
  static String get pacientesRegistroPublico => '$baseUrl/pacientes/registro-publico/';
  static String get associateClinic => '$baseUrl/pacientes/me/associate_clinic/';
}