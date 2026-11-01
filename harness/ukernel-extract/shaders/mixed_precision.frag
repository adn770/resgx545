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
void main() { lowp vec4 a = col; highp vec4 b = u0; gl_FragColor = a * b; }
