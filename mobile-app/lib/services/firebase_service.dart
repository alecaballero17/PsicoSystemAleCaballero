import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';

class FirebaseService {
  static Future<void> initialize() async {
    // 1. Inicializar Firebase
    await Firebase.initializeApp();
    
    // 2. Pedir permisos para notificaciones (iOS)
    FirebaseMessaging messaging = FirebaseMessaging.instance;
    NotificationSettings settings = await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      if (kDebugMode) {
        print('✅ Permiso concedido para notificaciones Push');
      }
    }

    // 3. Listener para mensajes en primer plano (Foreground)
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      if (kDebugMode) {
        print('🔔 Mensaje recibido en primer plano: ${message.notification?.title}');
      }
      // Aquí podrías mostrar un diálogo o snackbar custom
    });
  }

  static Future<String?> getToken() async {
    try {
      return await FirebaseMessaging.instance.getToken();
    } catch (e) {
      if (kDebugMode) {
        print('❌ Error obteniendo FCM Token: $e');
      }
      return null;
    }
  }
}
