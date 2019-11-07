#version 330
uniform mat4 mvp;

in vec3 vertices;
in vec2 texcoord;
in float offset;

out vec2 v_texcoord;
out float v_offset;

void main()
{
    gl_Position = mvp * vec4(vertices, 1.0);
    v_texcoord = texcoord;
    v_offset = offset;
}