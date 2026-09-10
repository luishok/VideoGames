# 03 - Breakout

Proyecto desarrollado como parte de la materia *Programación de Videojuegos I* (ULA).

## Descripción
Implementación del clásico juego Breakout utilizando el motor **Gale** y Pygame. Este estudio de caso se centra en la gestión avanzada de colisiones (AABB), rebotes vectoriales de la pelota, destrucción de bloques en grilla y sistemas de power-ups para la paleta.

## Controles
- **Movimiento de la Paleta:** 
  - `Flecha Izquierda` / `Flecha Derecha` Mover la paleta
- **Acciones:**
  - `Enter` Lanzar la pelota
  - `F`  Disparar (según el power-up activo) 
- **General:**
  - `Barra Espaciadora`  Pausar / Continuar

## ¿Cómo ejecutarlo?
1. Asegúrate de haber activado el entorno virtual y tener instaladas las dependencias en la raíz del repositorio.
2. Ubícate en esta carpeta desde tu terminal:
   ```bash
   cd 03-breakout
   python main.py