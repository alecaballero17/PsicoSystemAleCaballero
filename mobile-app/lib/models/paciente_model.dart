class Paciente {
  final int id;
  final String nombre;
  final String ci;
  final String fechaNacimiento;
  final String telefono;

  Paciente({
    required this.id,
    required this.nombre,
    required this.ci,
    required this.fechaNacimiento,
    required this.telefono,
  });

  // 🎯 LA CLAVE: Constructor para convertir el JSON de Django a Objeto Flutter
  factory Paciente.fromJson(Map<String, dynamic> json) {
    return Paciente(
      id: json['id'] ?? 0, // Fallback por seguridad
      nombre: json['nombre'] ?? 'Sin nombre',
      // Soporta 'ci' o 'identificacion' por si tu backend varía
      ci: json['ci'] ?? json['identificacion'] ?? 'S/N', 
      fechaNacimiento: json['fecha_nacimiento'] ?? 'No registrada',
      telefono: json['telefono'] ?? 'Sin teléfono',
    );
  }
}