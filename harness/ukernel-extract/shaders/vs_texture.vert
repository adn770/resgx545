attribute vec4 pos;
uniform sampler2D tex;
varying vec4 col;
void main() { gl_Position = pos; col = texture2DLod(tex, pos.xy, 0.0); }
