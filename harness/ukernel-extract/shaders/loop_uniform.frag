precision mediump float;
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
void main() { vec4 a = col; for (int i = 0; i < 64; i++) { if (i >= ui) break; a = a * u0; } gl_FragColor = a; }
