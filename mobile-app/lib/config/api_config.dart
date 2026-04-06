import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  static String get baseUrl {
    // Leemos la IP directamente del archivo .env
    // Si por alguna razón el archivo no carga, usamos tu IP por defecto como salvavidas
    return dotenv.env['API_URL'] ?? 'http://192.168.0.196:8000/api';
  }
}