import os

# Definición de la ruta
folder_path = "C:/Users/Mateo/Documents/UCE/2024 - 2025/mineria/7200 fichiers MIDI accords piano - Ressource/training"

# Recorrer los archivos en la carpeta
for file_name in os.listdir(folder_path):
    if "Mod-" in file_name or "Aug-" in file_name and file_name.endswith(".mid"):
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)
        print(f"Archivo eliminado: {file_name}")

print("Eliminación de archivos completada.")
