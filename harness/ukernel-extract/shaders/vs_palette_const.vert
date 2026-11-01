attribute vec4 pos;
uniform mat4 pal[8];
varying vec4 col;
void main() { gl_Position = (pal[1] * pos + pal[6] * pos) * 0.5; col = pos; }
