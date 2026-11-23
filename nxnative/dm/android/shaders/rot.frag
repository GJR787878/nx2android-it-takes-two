#version 450
layout(location = 0) in vec2 uv;
layout(location = 0) out vec4 color;
layout(set = 0, binding = 0) uniform sampler2D tex;
// mode 0: copy the bytes as they are (the image and the target have the same sRGB-ness). 1: the source is UNORM and the
// target is sRGB: decode before writing, so the target's encode stores the source's bytes unchanged. 2: the source is
// sRGB and the target is UNORM: encode before writing, so the target stores the source's bytes unchanged. This is the
// fallback for an Android surface that offers only one of the two formats (gfx_vk_present.c swap_make).
layout(push_constant) uniform P { vec4 m; vec2 t; int mode; } p;
vec3 srgb_to_linear(vec3 c) {
    c = clamp(c, 0.0, 1.0);
    vec3 lo = c / 12.92;
    vec3 hi = pow((c + 0.055) / 1.055, vec3(2.4));
    return mix(lo, hi, step(vec3(0.04045), c));
}
vec3 linear_to_srgb(vec3 c) {
    c = clamp(c, 0.0, 1.0);
    vec3 lo = c * 12.92;
    vec3 hi = 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055;
    return mix(lo, hi, step(vec3(0.0031308), c));
}
void main() {
    vec4 c = texture(tex, uv);
    if (p.mode == 1) c.rgb = srgb_to_linear(c.rgb);
    else if (p.mode == 2) c.rgb = linear_to_srgb(c.rgb);
    color = c;
}
