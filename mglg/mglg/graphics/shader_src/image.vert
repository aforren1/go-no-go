#version 330
uniform mat4 mvp; // depends on screen dims
in vec3 vertices;
in vec2 texcoord;
out vec2 v_texcoord;
void main()
{
    gl_Position = mvp * vec4(vertices, 1.0);
    v_texcoord = texcoord;
}