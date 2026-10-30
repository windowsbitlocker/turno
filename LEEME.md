# Temporizador de debate

Aplicación local para el operador, con controles y una pantalla para el proyector.
Los participantes siguen el reloj del proyector; no necesitan dispositivos.

## Abrir

Para usar la versión de Windows sin instalar Python, descarga el ZIP de
https://github.com/windowsbitlocker/turno/releases, extráelo y abre **Turno.exe**.
Incluye soporte de logos. Disponible para Windows 10/11 de 64 bits.

Haz doble clic en **Iniciar temporizador.cmd**, o usa el acceso directo
**Temporizador de debate** del Escritorio. Se necesita Python con Tkinter.
Se requiere Python 3.10 o posterior. Pillow es opcional para mostrar logos.
También puedes iniciar con `python -m debate_timer` o `python main.py`.

## Organización del código

El código está separado en el paquete **debate_timer/**: temporización, robos,
construcción de turnos, configuración, lectura de JSON, atajos y componentes de interfaz.
La carpeta **ui/** contiene el panel del operador, proyector, estilos, logos y editor
de tamaños. Consulta **README.md** para ver el mapa completo de módulos.

Conserva la carpeta **debate_timer/** junto a los lanzadores. El archivo antiguo
**temporizador_debate_v13.py** sigue funcionando como entrada de compatibilidad.

## Uso

- **Iniciar / Pausar** controla el turno actual.
- **Anterior / Siguiente** cambia de turno.
- **−10 s / +10 s** ajusta el tiempo; **Reiniciar turno** repone su duración.
- Durante las conclusiones, el operador usa **Iniciar robo / Terminar robo**.
  Solo se descuenta el tiempo utilizado. La conclusión queda en pausa al terminar.
- **Configuración** permite cambiar título, equipos, logos, tiempos y avisos,
  y exportar o importar la configuración en JSON.
- **F11** activa la pantalla completa del proyector; **Esc** sale de ella.
- En los controles: **Espacio** inicia/pausa; **← / →** cambia de turno; **Esc** pausa.

## Ajustar tamaños durante el uso

Haz **clic derecho sobre un elemento de la pantalla del proyector** para abrir su editor.
También puedes abrir **Configuración → Ajustar tamaños del proyector…**. Puedes ajustar
el título, etapa, equipo, reloj, avisos y logos; el panel del operador conserva sus tamaños.

Los cambios se ven al instante y no pausan ni reinician el reloj. Puedes modificar
el tamaño de texto, ancho en caracteres, alto en líneas, ajuste de línea y márgenes,
según el elemento. Los logos tienen un control de tamaño en píxeles. La distribución
y los colores originales se conservan; un tamaño muy grande puede necesitar más espacio.
**Restaurar este elemento** recupera sus tamaños originales.

Los tamaños manuales del proyector se mantienen al redimensionar su ventana. Los ajustes
antiguos del panel del operador se ignoran al importar una configuración. Para guardarlos para
otro uso, **exporta la configuración** y vuelve a importarla cuando corresponda.

Se han retirado Bluetooth, el servidor web, los códigos de equipo y las aplicaciones
para participantes. El temporizador funciona sin conexiones de red.

## Comprobaciones

`python -m unittest discover -s tests -v`

Las pruebas verifican controles del operador, orden de los 20 turnos, configuración,
precisión del reloj y descuento del robo. Requieren un escritorio con Tkinter.
