flat_frag = """
#version 330
uniform vec4 color;
out vec4 f_color;
void main()
{
    f_color = color;
}"""

flat_vert = """
#version 330
uniform mat4 mvp;
in vec3 vertices;
void main()
{
    gl_Position = mvp * vec4(vertices, 1.0);
}
"""

image_frag = """
#version 330
uniform sampler2D texture;
uniform float alpha;
in vec2 v_texcoord;
out vec4 f_color;
void main()
{
    f_color = texture2D(texture, v_texcoord) * alpha;
}

"""

image_vert = """
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
"""

particle_transform_vert = """
#version 330

in vec4 in_pos_alpha;
in vec4 in_prev_pos_alpha;
in vec4 accel;
out vec4 out_pos_alpha;
out vec4 out_prev_pos_alpha;

float accel_to_alpha(vec2 accel)
{
    vec2 abs_accel = abs(accel);
    float mag = abs_accel.x + abs_accel.y;
    return mag + 0.02;
}

void main()
{
    out_pos_alpha.xy = in_pos_alpha.xy * 2.0 - in_prev_pos_alpha.xy + accel.xy;
    out_pos_alpha.z = 0; // fix this axis
    out_pos_alpha.w = in_pos_alpha.w - accel_to_alpha(accel.xy); // fade out particle
    out_prev_pos_alpha = in_pos_alpha;
}


"""

particle_frag = """
#version 330
in vec4 color;
out vec4 f_color;

void main()
{
    f_color = color;
}

"""

particle_vert = """
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



"""

stipple_frag = """
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


"""

stipple_vert = """

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

"""

text_frag = """
#version 330
uniform sampler2D atlas_data;
uniform vec4 color;
uniform vec2 viewport;

in float v_offset;
in vec2 v_texcoord;

out vec4 f_color;

void main()
{
    vec4 current = texture2D(atlas_data, v_texcoord);
    vec4 previous = texture2D(atlas_data, v_texcoord+vec2(-1.0, 0.0)/viewport);
    vec4 next = texture2D(atlas_data, v_texcoord + vec2(1.0, 0.0)/viewport);

    float r = current.r;
    float g = current.g;
    float b = current.b;

    if( v_offset < 1.0 )
    {
        float z = v_offset;
        r = mix(current.r, previous.b, z);
        g = mix(current.g, current.r,  z);
        b = mix(current.b, current.g,  z);
    }
    else if( v_offset < 2.0 )
    {
        float z = v_offset - 1.0;
        r = mix(previous.b, previous.g, z);
        g = mix(current.r,  previous.b, z);
        b = mix(current.g,  current.r,  z);
    }
   else //if( v_offset <= 1.0 )
    {
        float z = v_offset - 2.0;
        r = mix(previous.g, previous.r, z);
        g = mix(previous.b, previous.g, z);
        b = mix(current.r,  previous.b, z);
    }

    float t = max(max(r, g), b);
    vec4 v_color = vec4(color.rgb, (r + g + b)/3.0);
    v_color = t * v_color + (1.0 - t) * vec4(r, g, b, min(min(r, g), b));
    f_color = vec4(v_color.rgb, color.a * v_color.a);
}

"""

text_vert = """
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
"""

vertex_color_frag = """
#version 330
in vec4 f_color;
out vec4 o_color;
void main()
{
    o_color = f_color;
}

"""

vertex_color_vert = """
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
"""
