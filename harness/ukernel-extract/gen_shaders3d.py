#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Write the shader corpus: shaders/*.vert, shaders/*.frag and shaders3d.txt.

One small GLSL ES 1.00 shader per feature, so the closed compiler's output for each (the USSE
programs in the captured kick, capture3d.sh shaders3d.txt) can be studied alone. Fragment
shaders share shaders/common.vert, which feeds them uv, col and nrm; vertex shaders share
shaders/plain.frag. Run it here; it rewrites the files it owns.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "shaders"

COMMON_VS = """attribute vec4 pos;
varying vec2 uv;
varying vec4 col;
varying vec3 nrm;
void main() {
    gl_Position = pos;
    uv = pos.xy * 0.5 + 0.5;
    col = pos * 0.5 + 0.5;
    nrm = normalize(vec3(pos.xy, 1.0));
}
"""
PLAIN_FS = """precision mediump float;
varying vec4 col;
void main() { gl_FragColor = col; }
"""
FS_HEAD = """precision mediump float;
varying vec2 uv;
varying vec4 col;
varying vec3 nrm;
uniform vec4 u0;
uniform vec4 u1;
uniform float uf;
uniform int ui;
uniform sampler2D tex;
uniform samplerCube cub;
uniform mat2 m2;
uniform mat3 m3;
uniform mat4 m4;
"""

# name -> fragment body (sets gl_FragColor), or (head override, body)
FS = {
    # arithmetic
    "add": "gl_FragColor = col + u0;", "sub": "gl_FragColor = col - u0;",
    "mul": "gl_FragColor = col * u0;", "mad": "gl_FragColor = col * u0 + u1;",
    "div": "gl_FragColor = col / u0;", "neg": "gl_FragColor = -col;",
    "scalar_mul": "gl_FragColor = col * uf;", "rcp": "gl_FragColor = vec4(1.0 / uf);",
    "abs": "gl_FragColor = abs(col - 0.5);", "sign": "gl_FragColor = sign(col - 0.5);",
    "floor": "gl_FragColor = floor(col * 4.0);", "ceil": "gl_FragColor = ceil(col * 4.0);",
    "fract": "gl_FragColor = fract(col * 4.0);", "mod": "gl_FragColor = mod(col, u0);",
    "min": "gl_FragColor = min(col, u0);", "max": "gl_FragColor = max(col, u0);",
    "clamp": "gl_FragColor = clamp(col, u0, u1);", "mix": "gl_FragColor = mix(col, u0, uv.x);",
    "step": "gl_FragColor = step(u0, col);",
    "smoothstep": "gl_FragColor = smoothstep(u0, u1, col);",
    # transcendentals
    "sin": "gl_FragColor = sin(col);", "cos": "gl_FragColor = cos(col);",
    "tan": "gl_FragColor = tan(col);", "asin": "gl_FragColor = asin(col);",
    "acos": "gl_FragColor = acos(col);", "atan": "gl_FragColor = atan(col);",
    "atan2": "gl_FragColor = atan(col, u0);", "exp": "gl_FragColor = exp(col);",
    "exp2": "gl_FragColor = exp2(col);", "log": "gl_FragColor = log(col);",
    "log2": "gl_FragColor = log2(col);", "pow": "gl_FragColor = pow(col, u0);",
    "sqrt": "gl_FragColor = sqrt(col);", "rsqrt": "gl_FragColor = inversesqrt(col);",
    "radians": "gl_FragColor = radians(col) + degrees(u0);",
    # vectors
    "dot": "gl_FragColor = vec4(dot(col, u0));",
    "dot3": "gl_FragColor = vec4(dot(nrm, u0.xyz));",
    "cross": "gl_FragColor = vec4(cross(nrm, u0.xyz), 1.0);",
    "length": "gl_FragColor = vec4(length(col));",
    "distance": "gl_FragColor = vec4(distance(col, u0));",
    "normalize": "gl_FragColor = normalize(col);",
    "reflect": "gl_FragColor = vec4(reflect(nrm, u0.xyz), 1.0);",
    "refract": "gl_FragColor = vec4(refract(nrm, u0.xyz, uf), 1.0);",
    "faceforward": "gl_FragColor = vec4(faceforward(nrm, u0.xyz, u1.xyz), 1.0);",
    "swizzle": "gl_FragColor = col.wzyx + u0.xxyy;",
    "construct": "gl_FragColor = vec4(uv, col.zw) + vec4(uf);",
    # precision
    "lowp": ("precision lowp float;\nvarying vec4 col;\nuniform vec4 u0;\n",
             "gl_FragColor = col * u0 + col;"),
    "highp": ("precision highp float;\nvarying vec4 col;\nuniform vec4 u0;\n",
              "gl_FragColor = col * u0 + col;"),
    "mixed_precision": "lowp vec4 a = col; highp vec4 b = u0; gl_FragColor = a * b;",
    # control flow
    "if_uniform": "if (uf > 0.5) gl_FragColor = col; else gl_FragColor = u0;",
    "if_varying": "if (uv.x > 0.5) gl_FragColor = col; else gl_FragColor = u0;",
    "ternary": "gl_FragColor = uv.x > uv.y ? col : u0;",
    "loop4": "vec4 a = col; for (int i = 0; i < 4; i++) a = a * u0 + u1; gl_FragColor = a;",
    "loop16": "vec4 a = col; for (int i = 0; i < 16; i++) a = a * u0 + u1; gl_FragColor = a;",
    "loop_uniform": "vec4 a = col; for (int i = 0; i < 64; i++) { if (i >= ui) break; "
                    "a = a * u0; } gl_FragColor = a;",
    "nested_if": "vec4 a = col; if (uv.x > 0.5) { if (uv.y > 0.5) a = u0; else a = u1; } "
                 "gl_FragColor = a;",
    "discard": "if (uv.x > 0.5) discard; gl_FragColor = col;",
    "discard_alpha": "vec4 c = col * u0; if (c.a < 0.5) discard; gl_FragColor = c;",
    "any_all": "gl_FragColor = vec4(any(greaterThan(col, u0)), all(lessThan(col, u1)), 0.0, 1.0);",
    "compare": "gl_FragColor = vec4(lessThan(col, u0));",
    "equal": "gl_FragColor = vec4(equal(col, u0));",
    # integers
    "int_ops": "int i = int(col.x * 8.0); gl_FragColor = vec4(float(i * 3 + ui));",
    "int_div": "int i = int(col.x * 64.0); gl_FragColor = vec4(float(i / (ui + 1)));",
    "ivec": "ivec2 i = ivec2(uv * 16.0); gl_FragColor = vec4(vec2(i), 0.0, 1.0);",
    # matrices
    "mat4": "gl_FragColor = m4 * col;", "mat3": "gl_FragColor = vec4(m3 * nrm, 1.0);",
    "mat2": "gl_FragColor = vec4(m2 * uv, 0.0, 1.0);",
    "mat4_mat4": "gl_FragColor = (m4 * m4) * col;",
    # textures
    "tex2d": "gl_FragColor = texture2D(tex, uv);",
    "tex2d_bias": "gl_FragColor = texture2D(tex, uv, 1.0);",
    "tex2d_proj": "gl_FragColor = texture2DProj(tex, vec3(uv, 2.0));",
    "tex2d_proj4": "gl_FragColor = texture2DProj(tex, vec4(uv, 0.0, 2.0));",
    "texcube": "gl_FragColor = textureCube(cub, nrm);",
    "tex_dependent": "gl_FragColor = texture2D(tex, texture2D(tex, uv).xy);",
    "tex_modulate": "gl_FragColor = texture2D(tex, uv) * col;",
    "tex_two": "gl_FragColor = texture2D(tex, uv) + texture2D(tex, uv * 2.0);",
    "tex_offset": "gl_FragColor = texture2D(tex, uv + u0.xy);",
    # built-ins
    "fragcoord": "gl_FragColor = vec4(gl_FragCoord.xy / 64.0, gl_FragCoord.z, 1.0);",
    "fragcoord_w": "gl_FragColor = vec4(gl_FragCoord.w);",
    "frontfacing": "gl_FragColor = gl_FrontFacing ? col : u0;",
    "pointcoord": "gl_FragColor = vec4(gl_PointCoord, 0.0, 1.0);",
    "fragdata": "gl_FragData[0] = col;",
    "derivatives": ("#extension GL_OES_standard_derivatives : enable\n" + FS_HEAD,
                    "gl_FragColor = vec4(dFdx(uv), dFdy(uv)) + vec4(fwidth(uv.x));"),
}

# name -> vertex shader text (with shaders/plain.frag)
VS = {
    "vs_matrix": "attribute vec4 pos;\nuniform mat4 mvp;\nvarying vec4 col;\n"
                 "void main() { gl_Position = mvp * pos; col = pos; }\n",
    "vs_ops": "attribute vec4 pos;\nuniform vec4 u0;\nvarying vec4 col;\n"
              "void main() { gl_Position = pos; col = sin(pos * u0) + normalize(pos); }\n",
    "vs_loop": "attribute vec4 pos;\nuniform vec4 u0;\nvarying vec4 col;\nvoid main() { "
               "vec4 a = pos; for (int i = 0; i < 8; i++) a = a * u0 + pos; "
               "gl_Position = pos; col = a; }\n",
    "vs_branch": "attribute vec4 pos;\nuniform float uf;\nvarying vec4 col;\nvoid main() { "
                 "gl_Position = pos; if (pos.x > uf) col = pos; else col = -pos; }\n",
    "vs_pointsize": "attribute vec4 pos;\nuniform float uf;\nvarying vec4 col;\nvoid main() { "
                    "gl_Position = pos; gl_PointSize = 4.0 + uf; col = pos; }\n",
    "vs_attr2": "attribute vec4 pos;\nattribute vec4 extra;\nvarying vec4 col;\n"
                "void main() { gl_Position = pos + extra * 0.0; col = extra; }\n",
    "vs_texture": "attribute vec4 pos;\nuniform sampler2D tex;\nvarying vec4 col;\nvoid main() "
                  "{ gl_Position = pos; col = texture2DLod(tex, pos.xy, 0.0); }\n",
    "vs_palette": "attribute vec4 pos;\nuniform mat4 pal[8];\nvarying vec4 col;\nvoid main() { "
                  "int k = int(clamp(pos.x * 4.0 + 4.0, 0.0, 7.0)); gl_Position = pal[k] * pos; "
                  "col = pos; }\n",
    "vs_palette_const": "attribute vec4 pos;\nuniform mat4 pal[8];\nvarying vec4 col;\n"
                        "void main() { gl_Position = (pal[1] * pos + pal[6] * pos) * 0.5; "
                        "col = pos; }\n",
    "vs_skin4": "attribute vec4 pos;\nattribute vec4 weights;\nattribute vec4 bones;\n"
                "uniform mat4 pal[16];\nvarying vec4 col;\nvoid main() { vec4 p = vec4(0.0); "
                "for (int i = 0; i < 4; i++) p += pal[int(bones[i])] * pos * weights[i]; "
                "gl_Position = p; col = weights; }\n",
    "vs_many_attrs": "attribute vec4 pos;\nattribute vec4 a1;\nattribute vec4 a2;\n"
                     "attribute vec4 a3;\nattribute vec4 a4;\nattribute vec4 a5;\n"
                     "attribute vec4 a6;\nattribute vec4 a7;\nvarying vec4 col;\nvoid main() { "
                     "gl_Position = pos; col = a1 + a2 * a3 + a4 * a5 + a6 * a7; }\n",
    "vs_many_varyings": "attribute vec4 pos;\nvarying vec4 v0;\nvarying vec4 v1;\n"
                        "varying vec4 v2;\nvarying vec4 v3;\nvarying vec4 v4;\nvarying vec4 v5;\n"
                        "varying vec4 v6;\nvarying vec4 v7;\nvoid main() { gl_Position = pos; "
                        "v0 = pos; v1 = pos * 2.0; v2 = pos + 1.0; v3 = pos.yxwz; v4 = -pos; "
                        "v5 = pos * pos; v6 = vec4(pos.x); v7 = vec4(pos.y); }\n",
    "vs_varying_types": "attribute vec4 pos;\nvarying float f;\nvarying vec2 t2;\n"
                        "varying vec3 t3;\nvarying mat2 m;\nvoid main() { gl_Position = pos; "
                        "f = pos.x; t2 = pos.xy; t3 = pos.xyz; m = mat2(pos.x, pos.y, pos.z, "
                        "pos.w); }\n",
    "vs_lighting": "attribute vec4 pos;\nattribute vec3 normal;\nuniform mat4 mvp;\n"
                   "uniform mat3 nmat;\nuniform vec3 ldir;\nuniform vec4 diffuse;\n"
                   "varying vec4 col;\nvoid main() { gl_Position = mvp * pos; "
                   "vec3 n = normalize(nmat * normal); "
                   "col = diffuse * max(dot(n, ldir), 0.0); }\n",
    "vs_uniform_array": "attribute vec4 pos;\nuniform vec4 c[16];\nvarying vec4 col;\n"
                        "void main() { int k = int(clamp(pos.y * 8.0 + 8.0, 0.0, 15.0)); "
                        "gl_Position = pos; col = c[k] + c[3]; }\n",
    "vs_loop_uniform": "attribute vec4 pos;\nuniform int n;\nuniform vec4 u0;\n"
                       "varying vec4 col;\nvoid main() { vec4 a = pos; for (int i = 0; i < 32; "
                       "i++) { if (i >= n) break; a = a * u0 + pos; } gl_Position = pos; "
                       "col = a; }\n",
    "vs_fog": "attribute vec4 pos;\nuniform mat4 mv;\nuniform float density;\n"
              "varying vec4 col;\nvoid main() { vec4 e = mv * pos; gl_Position = pos; "
              "col = vec4(exp(-density * length(e.xyz))); }\n",
    "vs_texmatrix": "attribute vec4 pos;\nuniform mat4 tm;\nvarying vec4 col;\n"
                    "void main() { gl_Position = pos; col = tm * vec4(pos.xy * 0.5 + 0.5, 0.0, "
                    "1.0); }\n",
}
# vertex shaders whose varyings need their own fragment shader (shaders/<name>.frag)
VS_FS = {
    "vs_many_varyings": "precision mediump float;\nvarying vec4 v0;\nvarying vec4 v1;\n"
                        "varying vec4 v2;\nvarying vec4 v3;\nvarying vec4 v4;\nvarying vec4 v5;\n"
                        "varying vec4 v6;\nvarying vec4 v7;\nvoid main() { gl_FragColor = v0 + v1 "
                        "+ v2 + v3 + v4 + v5 + v6 + v7; }\n",
    "vs_varying_types": "precision mediump float;\nvarying float f;\nvarying vec2 t2;\n"
                        "varying vec3 t3;\nvarying mat2 m;\nvoid main() { gl_FragColor = "
                        "vec4(t3 * f, t2.x) + vec4(m[0], m[1]); }\n",
}
# the run's extra tri options, by shader name
EXTRA = {"pointcoord": "prim=points", "vs_pointsize": "prim=points", "frontfacing": "",
         "fragcoord": "depth=less"}


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "common.vert").write_text(COMMON_VS)
    (OUT / "plain.frag").write_text(PLAIN_FS)
    lines = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra", "#",
             "# The shader corpus (gen_shaders3d.py writes this list and shaders/): one small",
             "# shader per feature, each run as tri's shaders, so a capture holds the closed",
             "# compiler's USSE program for that feature alone. capture3d.sh runs it.", "base"]
    for name, body in FS.items():
        head, body = body if isinstance(body, tuple) else (FS_HEAD, body)
        (OUT / f"{name}.frag").write_text(f"{head}void main() {{ {body} }}\n")
        extra = EXTRA.get(name, "")
        lines.append(f"fs_{name:<18} vsfile=shaders/common.vert fsfile=shaders/{name}.frag"
                     + (f" {extra}" if extra else ""))
    for name, text in VS.items():
        (OUT / f"{name}.vert").write_text(text)
        fs = "plain"
        if name in VS_FS:
            fs = name
            (OUT / f"{name}.frag").write_text(VS_FS[name])
        extra = EXTRA.get(name, "")
        lines.append(f"{name:<21} vsfile=shaders/{name}.vert fsfile=shaders/{fs}.frag"
                     + (f" {extra}" if extra else ""))
    (HERE / "shaders3d.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
