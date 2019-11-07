#version 330

layout (location = 0) in vec3 vertices;

flat out vec3 start_pos;
out vec3 vert_pos;

uniform mat4 mvp;

void main()
{
    vec4 pos    = mvp * vec4(vertices, 1.0);
    gl_Position = pos;
    vert_pos     = pos.xyz / pos.w;
    start_pos    = vert_pos;
}
