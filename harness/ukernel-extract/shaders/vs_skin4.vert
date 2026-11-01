attribute vec4 pos;
attribute vec4 weights;
attribute vec4 bones;
uniform mat4 pal[16];
varying vec4 col;
void main() { vec4 p = vec4(0.0); for (int i = 0; i < 4; i++) p += pal[int(bones[i])] * pos * weights[i]; gl_Position = p; col = weights; }
