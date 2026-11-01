attribute vec4 pos;
uniform float uf;
varying vec4 col;
void main() { gl_Position = pos; gl_PointSize = 4.0 + uf; col = pos; }
