"""Create the portable release ZIP, notices, and SHA-256 checksums."""
from importlib.metadata import distribution
from pathlib import Path
import hashlib
import shutil
import sys
import tomllib
from zipfile import ZipFile, ZIP_DEFLATED


def package(root: Path):
    version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    folder = root / "dist" / f"Turno-v{version}-Windows-x64"
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "dist" / "Turno.exe", folder / "Turno.exe")
    shutil.copy2(root / "LICENSE", folder / "LICENSE.txt")
    (folder / "LEEME.txt").write_text(
        f"TURNO {version} - WINDOWS 10/11 (64 BITS)\n\n"
        "Extrae toda la carpeta y abre Turno.exe. No necesitas instalar Python.\n"
        "El programa abre los controles del operador y la pantalla del proyector.\n"
        "F11: pantalla completa del proyector. Esc: salir de pantalla completa.\n"
        "Los robos son controlados por el operador. No se necesitan dispositivos para los equipos.\n"
        "Clic derecho en el proyector: ajustar el tamaño de cada elemento.\n"
        "Exporta tu configuración para guardar tiempos, nombres y tamaños.\n\n"
        "Código fuente y documentación: https://github.com/windowsbitlocker/turno\n"
        "Licencia MIT. Primera versión sin firma digital de editor.\n", encoding="utf-8")
    licenses = folder / "licenses"
    licenses.mkdir(exist_ok=True)
    runtime_license = Path(sys.base_prefix) / "LICENSE.txt"
    if runtime_license.exists():
        shutil.copy2(runtime_license, licenses / "Python-LICENSE.txt")
    for name in ("Pillow", "PyInstaller"):
        package_distribution = distribution(name)
        candidates = [file for file in package_distribution.files or []
                      if any(word in file.name.lower() for word in ("license", "copying"))
                      and str(file).lower().endswith((".txt", "/license", "/copying"))]
        for index, file in enumerate(candidates):
            source = Path(package_distribution.locate_file(file))
            if source.is_file():
                shutil.copy2(source, licenses / f"{name}-{index}-{file.name}")
    for library in ("tcl8.6", "tk8.6"):
        source = Path(sys.base_prefix) / "tcl" / library / "license.terms"
        if source.exists():
            shutil.copy2(source, licenses / f"{library}-license.terms")
    for source in (root / "packaging" / "licenses").glob("*"):
        if source.is_file():
            shutil.copy2(source, licenses / source.name)
    (folder / "THIRD_PARTY_NOTICES.txt").write_text(
        "Turno bundles Python, Tcl/Tk, and Pillow, and uses the PyInstaller bootloader.\n"
        "See licenses/ for the applicable third-party license notices.\n"
        "Python: https://www.python.org/\nTcl/Tk: https://www.tcl.tk/\n"
        "Pillow: https://python-pillow.org/\nPyInstaller: https://pyinstaller.org/\n"
        "The PyInstaller license includes an exception for distribution of bundled applications.\n",
        encoding="utf-8")
    archive = root / "dist" / f"{folder.name}.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as output:
        for file in sorted(folder.rglob("*")):
            if file.is_file():
                output.write(file, folder.name + "/" + str(file.relative_to(folder)).replace("\\", "/"))
    checksum = root / "dist" / f"Turno-v{version}-SHA256.txt"
    checksum.write_text(
        hashlib.sha256(archive.read_bytes()).hexdigest() + "  " + archive.name + "\n" +
        hashlib.sha256((folder / "Turno.exe").read_bytes()).hexdigest() + "  Turno.exe\n", encoding="utf-8")
    print(archive)
    print(checksum)


if __name__ == "__main__":
    package(Path(__file__).resolve().parents[1])
