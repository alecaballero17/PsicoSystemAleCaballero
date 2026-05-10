class User {
  final int id;
  final String username;
  final String email;
  final String clinicaNombre;
  final String? firstName;
  final String? lastName;
  final String? telefono;
  final String? ci;

  User({
    required this.id, 
    required this.username, 
    required this.email,
    required this.clinicaNombre,
    this.firstName,
    this.lastName,
    this.telefono,
    this.ci,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      username: json['username'] ?? 'Usuario',
      email: json['email'] ?? 'sin@correo.com',
      clinicaNombre: json['clinica_nombre'] ?? 'Sin Clínica',
      firstName: json['first_name'],
      lastName: json['last_name'],
      telefono: json['telefono'],
      ci: json['ci'],
    );
  }
}