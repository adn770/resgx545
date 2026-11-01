attribute vec4 pos;
uniform vec4 u0;
varying vec4 col;
void main() { vec4 a = pos; for (int i = 0; i < 8; i++) a = a * u0 + pos; gl_Position = pos; col = a; }
