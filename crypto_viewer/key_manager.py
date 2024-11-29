import os

class APIKeyManager:
    def __init__(self, directory: str, filename: str):
        """
        Initialisiert den APIKeyManager mit dem Verzeichnis und Dateinamen.

        :param directory: Verzeichnis, in dem sich die Schlüsseldatei befindet
        :param filename: Name der Datei, die die API-Schlüssel enthält
        """
        self.directory = directory
        self.filename = filename
        self.api_key = None
        self.api_secret = None
        self.keys_loaded = False  # Flag, um den Ladezustand zu verfolgen

    def load_keys(self):
        """
        Lädt die API-Schlüssel aus der Datei und extrahiert die benötigten Informationen.
        """
        # Plattformunabhängigen Pfad erstellen
        file_path = os.path.join(self.directory, self.filename)

        # Datei öffnen und lesen
        with open(file_path, "r") as file:
            content = file.read()

        # Inhalt zeilenweise aufteilen
        lines = content.splitlines()

        # Daten extrahieren
        self.api_key = lines[0].split(": ")[1]
        api_secret2 = lines[1].split(": ")[1]
        api_secret_parts = [api_secret2] + lines[2:-1]

        # Konvertiere die Liste in einen zusammenhängenden String
        self.api_secret = '\n'.join(api_secret_parts)

        self.keys_loaded = True  # Setze das Flag auf True, wenn die Schlüssel erfolgreich geladen wurden

    def get_api_key(self) -> str:
        """Gibt den API-Schlüssel zurück, wenn die Schlüssel geladen wurden."""
        if not self.keys_loaded:
            raise RuntimeError("API-Schlüssel wurden noch nicht geladen. Bitte zuerst load_keys aufrufen.")
        return self.api_key

    def get_api_secret(self) -> str:
        """Gibt das API-Secret zurück, wenn die Schlüssel geladen wurden."""
        if not self.keys_loaded:
            raise RuntimeError("API-Schlüssel wurden noch nicht geladen. Bitte zuerst load_keys aufrufen.")
        return self.api_secret


# Beispielverwendung der APIKeyManager-Klasse
def main():
    # Definiere den Pfad zur Datei
    file_dir = "/home/wolff/keys"  # Ordnername
    file_name = "coinbase_key.txt"

    # APIKeyManager-Instanz erstellen
    key_manager = APIKeyManager(file_dir, file_name)

    # Lade die API-Schlüssel
    key_manager.load_keys()

    # Ausgabe der API-Schlüssel
    print("API Key:", key_manager.get_api_key())
    print("API Secret:", key_manager.get_api_secret())


if __name__ == "__main__":
    main()
