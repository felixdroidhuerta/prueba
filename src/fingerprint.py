class FingerprintSensor:
    """Clase de ejemplo para interactuar con un sensor de huella dactilar."""

    def __init__(self):
        # Inicialización del hardware (placeholder)
        pass

    def enroll_user(self, user_id):
        """Registra la huella de un usuario y asocia un ID del sensor."""
        # Aquí se debería llamar a la API del sensor para registrar la huella
        # y devolver un identificador interno.
        sensor_id = user_id  # Placeholder: usar el mismo ID
        print(f"Enrolando huella para usuario {user_id} -> sensor_id {sensor_id}")
        return sensor_id

    def delete_fingerprint(self, sensor_id):
        """Elimina la huella registrada en el sensor."""
        print(f"Eliminando huella con sensor_id {sensor_id}")
        # Llamada al sensor para borrar la huella

    def scan_fingerprint(self):
        """Escanea una huella y devuelve el ID del usuario reconocido."""
        # En un entorno real se leería la huella y se obtendría un ID
        try:
            user_id = int(input("Simulacion: introduzca ID de usuario: "))
            return user_id
        except ValueError:
            return None
