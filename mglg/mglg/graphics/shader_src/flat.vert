#version 330
uniform mat4 mvp;
in vec3 vertices;
void main()
{
    gl_Position = mvp * vec4(vertices, 1.0);
}