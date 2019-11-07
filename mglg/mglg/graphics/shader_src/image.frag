#version 330
uniform sampler2D texture;
uniform float alpha;
in vec2 v_texcoord;
out vec4 f_color;
void main()
{
    f_color = texture2D(texture, v_texcoord) * alpha;
}