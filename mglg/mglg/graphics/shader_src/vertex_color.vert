#version 330
uniform mat4 mvp;
in vec3 vertices;
in vec4 color;
out vec4 f_color;
void main()
{
    gl_Position = mvp * vec4(vertices, 1.0);
    f_color = color;
}