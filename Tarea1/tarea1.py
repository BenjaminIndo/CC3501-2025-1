import pyglet
import numpy as np
from pyglet.gl import *
WIDTH = 800
HEIGHT = 700
DEFINITION = 100
window = pyglet.window.Window(WIDTH,HEIGHT,"Tarea1")

#Circle movements variables
xCircle, yCircle = 0.0, 0.0
xSpeed, ySpeed = 0.02, 0.015

xImage, yImage = 0.0, 0.0
xImageSpeed, yImageSpeed= 0.02, 0.015

image = pyglet.image.load('Tarea1/cachorro.jpeg')
image_width, image_height = image.width, image.height

sprite = pyglet.sprite.Sprite(image)

def create_circle(x, y, radius):
    # Discretizamos un circulo en DEFINITION pasos
    # Cada punto tiene 3 coordenadas y 3 componentes de color
    # Consideramos tambien el centro del circulo
    positions = np.zeros((DEFINITION + 1)*3, dtype=np.float32) 
    colors = np.zeros((DEFINITION + 1) * 3, dtype=np.float32)
    dtheta = 2*np.pi / DEFINITION

    for i in range(DEFINITION):
        theta = i*dtheta
        positions[i*3:(i+1)*3] = [x + np.cos(theta)*radius, y + np.sin(theta)*radius, 0.0]
        colors[i * 3:(i + 1) * 3] = [0.0, 1.0, 1.0]

    # Finalmente agregamos el centro
    positions[3*DEFINITION:] = [x, y, 0.0]
    colors[3 * DEFINITION:] = [0.0, 1.0, 1.0]  # El centro también será celeste
    return positions, colors

def create_circle_indices():
    # Ahora calculamos los indices
    indices = np.zeros(3*( DEFINITION + 1 ), dtype=np.int32)
    for i in range(DEFINITION):
        # Cada triangulo se forma por el centro, el punto actual y el siguiente
        indices[3*i: 3*(i+1)] = [DEFINITION, i, i+1]
   
    # Completamos el circulo (pueden borrar esta linea y ver que pasa)
    indices[3*DEFINITION:] = [DEFINITION, DEFINITION - 1, 0]
    return indices

if __name__ == "__main__":
    # Creamos nuestros shaders
    vertex_source = """
#version 330

in vec3 position;
in vec3 color;

out vec3 fragColor;

void main() {
    fragColor = color;
    gl_Position = vec4(position, 1.0f);
}
    """

    fragment_source = """
#version 330

in vec3 fragColor;
out vec4 outColor;

void main()
{
    outColor = vec4(fragColor, 1.0f);
}
    """
    @window.event
    def on_draw():

        # Esta linea limpia la pantalla entre frames
        window.clear()
        glClearColor(0.6, 0.6, 0.6, 1)

        # Acá dibujamos el círculo
        pipeline.use()
        circle_gpu.draw(GL_TRIANGLES)

        # Dibujamos el perrito
        sprite.draw()

    def update(dt):
        global xCircle, yCircle, xSpeed, ySpeed
        global xImage, yImage, xImageSpeed, yImageSpeed

        xCircle += xSpeed
        yCircle += ySpeed

        if xCircle - 0.2 <= -1 or xCircle + 0.2 >=1:
            xSpeed=-xSpeed
        if yCircle - 0.2 <= -1 or yCircle + 0.2 >=1:
            ySpeed=-ySpeed

        xImage += xImageSpeed
        yImage += yImageSpeed

        if xImage<= 0 or xImage>= 1:
            xImageSpeed = -xImageSpeed
        if yImage<= 0 or yImage>= 1:
            yImageSpeed = -yImageSpeed

        circle_pos, circle_color = create_circle(xCircle, yCircle, 0.2)
        circle_gpu.position[:]=circle_pos
        circle_gpu.color[:]=circle_color

        sprite.x = xImage * (WIDTH- image_width)
        sprite.y = yImage*(HEIGHT - image_height)


    # Compilamos los shaders
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")

    # Creamos nuestro pipeline de rendering
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # Creamos el circulo
    circle_pos, circle_color = create_circle(-0.2, 0.0, 0.2)

    # Creamos el circulo en la gpu, ahora con menos vertices en total
    # y le tenemos que pasar los indices
    circle_gpu = pipeline.vertex_list_indexed(DEFINITION+1, GL_TRIANGLES, create_circle_indices())

    # Copiamos los datos, añadimos el color
    circle_gpu.position[:] = circle_pos
    circle_gpu.color[:]=circle_color
    
    pyglet.clock.schedule_interval(update, 1/60.0)


    pyglet.app.run()