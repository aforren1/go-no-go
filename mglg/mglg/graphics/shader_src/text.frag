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