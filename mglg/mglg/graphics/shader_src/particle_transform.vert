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
