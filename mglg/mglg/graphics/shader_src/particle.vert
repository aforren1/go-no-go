#version 330

uniform mat4 mvp;

in vec4 vertices_alpha;
in vec4 color_size;

out vec4 color;

void main()
{
    color = vec4(color_size.xyz, vertices_alpha.w);
    gl_Position = mvp * vec4(vertices_alpha.xyz, 1.0);
    gl_PointSize = color_size.w;
}

