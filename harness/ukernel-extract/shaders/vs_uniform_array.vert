attribute vec4 pos;
uniform vec4 c[16];
varying vec4 col;
void main() { int k = int(clamp(pos.y * 8.0 + 8.0, 0.0, 15.0)); gl_Position = pos; col = c[k] + c[3]; }
