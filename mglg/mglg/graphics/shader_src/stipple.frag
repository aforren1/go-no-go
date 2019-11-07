#version 330

flat in vec3 start_pos;
in vec3 vert_pos;

out vec4 f_color;

uniform vec2  u_resolution;
uniform uint  u_pattern;
uniform float u_factor;
uniform vec4 color;

void main()
{
    vec2  dir  = (vert_pos.xy-start_pos.xy) * u_resolution/2.0;
    float dist = length(dir);

    uint bit = uint(round(dist / u_factor)) & 15U;
    if ((u_pattern & (1U<<bit)) == 0U)
        discard;
    f_color = color;
}
