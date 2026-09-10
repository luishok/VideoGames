# Video Game Programming I

Repositorio oficial de las prácticas y proyectos desarrollados para la materia *Programación de Videojuegos I* (ISPPV1) de la Universidad de Los Andes (ULA), Venezuela.

Desarrollado por **Luis Ordoñez**.

Cada carpeta contiene un juego independiente construido de forma incremental para ilustrar conceptos de desarrollo de videojuegos (bucle de juego, estados, colisiones, mapas de celdas, interfaces, etc.), utilizando [Gale](https://pypi.org/project/gale-engine/), un motor de juegos en Python construido sobre [Pygame](https://www.pygame.org/).

## Proyectos (Study cases)

| # | Proyecto | Estado / Enlace | Concepto principal |
|---|---------|-----------------|---------------------|
| 01 | [`01-pong`](01-pong) | [Ver Código](01-pong) | Pong / Físicas básicas |
| 02 | [`02-flappy_bird`](02-flappy_bird) | [Ver Código](02-flappy_bird) | Flappy Bird / Gravedad y Estados |
| 03 | [`03-breakout`](03-breakout) | [Ver Código](03-breakout) | Breakout / Colisiones y Power-ups |
| 04 | [`04-match3`](04-match3) | [Ver Código](04-match3) | Match-3 / Lógica de tableros |
| 05 | [`05-super_martian`](05-super_martian) | [Ver Código](05-super_martian) | Platformer / Plataformas y animaciones |
| 06 | `06-princess` | *En desarrollo* | The Legend of the Princess (ARPG) |
| 07 | `07-ultimate_fantasy` | *En desarrollo* | Ultimate Fantasy (RPG) |
| 08 | `08-throw_a_bird` | *En desarrollo* | Throw a Bird |

Estructura general de cada proyecto:
<NN-project_name>/
├── main.py            # Punto de entrada: instancia y ejecuta el juego
├── settings.py        # Resolución, controles, fuentes y constantes
├── src/               # Código fuente (estados, entidades, mundos, etc.)
└── assets/            # Imágenes, sonidos y fuentes


## Requisitos y Configuración

- **Python 3.12+**
- **Dependencia única:** [`gale-engine`](https://pypi.org/project/gale-engine/) (incluye Pygame).

### Instalación local:

Clona el repositorio y configura el entorno virtual en la raíz:

```bash
git clone [https://github.com/luishok/VideoGames.git](https://github.com/luishok/VideoGames.git)
cd VideoGames
python3 -m venv .venv
source .venv/bin/activate       # En Windows: .venv\Scripts\activate
pip install -r requirements.txt



