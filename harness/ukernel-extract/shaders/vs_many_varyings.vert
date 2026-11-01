attribute vec4 pos;
varying vec4 v0;
varying vec4 v1;
varying vec4 v2;
varying vec4 v3;
varying vec4 v4;
varying vec4 v5;
varying vec4 v6;
varying vec4 v7;
void main() { gl_Position = pos; v0 = pos; v1 = pos * 2.0; v2 = pos + 1.0; v3 = pos.yxwz; v4 = -pos; v5 = pos * pos; v6 = vec4(pos.x); v7 = vec4(pos.y); }
