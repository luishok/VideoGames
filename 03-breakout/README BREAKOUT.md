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

## Power Up
- **Cañones** Disparas con F dos misiles que destruiran los ladrillos al tocarlos
- **MultiBolas** Genera 2 pelotas adicionales
- **Atajar** Permite atajar la/las pelotas y soltarlas con la tecla Enter
- **Aumento de tamaño** La/las pelotas aumentan al doble de su tamaño, haciendo mas facil golpear ladrillos y la misma paleta 
 

## ¿Cómo ejecutarlo?
1. Asegúrate de haber activado el entorno virtual y tener instaladas las dependencias en la raíz del repositorio.
2. Ubícate en esta carpeta desde tu terminal:
   ```bash
   cd 03-breakout
   python main.py
