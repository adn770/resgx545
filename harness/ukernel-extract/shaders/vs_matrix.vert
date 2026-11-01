attribute vec4 pos;
uniform mat4 mvp;
varying vec4 col;
void main() { gl_Position = mvp * pos; col = pos; }
