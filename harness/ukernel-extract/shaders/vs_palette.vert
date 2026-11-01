attribute vec4 pos;
uniform mat4 pal[8];
varying vec4 col;
void main() { int k = int(clamp(pos.x * 4.0 + 4.0, 0.0, 7.0)); gl_Position = pal[k] * pos; col = pos; }
