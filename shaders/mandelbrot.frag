#version 330 core

out vec4 frag_color;

uniform vec2 u_center;
uniform float u_scale;
uniform vec2 u_resolution;
uniform int u_max_iterations;
uniform int u_palette_id;
uniform float u_palette_offset;
uniform float u_time;

vec2 complex_square(vec2 z) {
    return vec2(
        z.x * z.x - z.y * z.y,
        2.0 * z.x * z.y
    );
}

vec3 cosine_palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318530718 * (c * t + d));
}

vec3 palette(float t) {
    if (u_palette_id == 0) {
        return cosine_palette(
            t,
            vec3(0.50),
            vec3(0.50),
            vec3(1.00),
            vec3(0.00, 0.10, 0.20)
        );
    }

    if (u_palette_id == 1) {
        return cosine_palette(
            t,
            vec3(0.50),
            vec3(0.50),
            vec3(1.00, 0.70, 0.40),
            vec3(0.00, 0.15, 0.20)
        );
    }

    if (u_palette_id == 2) {
        return cosine_palette(
            t,
            vec3(0.45, 0.40, 0.35),
            vec3(0.55, 0.60, 0.65),
            vec3(1.00),
            vec3(0.00, 0.08, 0.18)
        );
    }

    return cosine_palette(
        t,
        vec3(0.50, 0.45, 0.40),
        vec3(0.50, 0.55, 0.60),
        vec3(1.00, 1.00, 0.80),
        vec3(0.30, 0.20, 0.20)
    );
}

void main() {
    vec2 pixel = gl_FragCoord.xy;
    vec2 uv = (2.0 * pixel - u_resolution) / u_resolution.y;
    vec2 c = u_center + uv * u_scale;
    vec2 z = vec2(0.0);

    int iteration = 0;
    float magnitude_squared = 0.0;

    for (int i = 0; i < 3000; i++) {
        if (i >= u_max_iterations) {
            break;
        }

        z = complex_square(z) + c;
        magnitude_squared = dot(z, z);

        if (magnitude_squared > 256.0) {
            iteration = i;
            break;
        }

        iteration = i + 1;
    }

    if (iteration >= u_max_iterations) {
        frag_color = vec4(0.002, 0.004, 0.010, 1.0);
        return;
    }

    float smooth_iteration =
        float(iteration) + 1.0
        - log2(log2(sqrt(magnitude_squared)));

    float t =
        smooth_iteration * 0.025
        + u_palette_offset
        + u_time * 0.015;

    vec3 color = palette(t);
    float edge = 1.0 - exp(-0.045 * smooth_iteration);
    color *= 0.25 + 0.75 * edge;
    color = pow(max(color, vec3(0.0)), vec3(0.85));

    frag_color = vec4(color, 1.0);
}
