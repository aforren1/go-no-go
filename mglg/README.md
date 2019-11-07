Magnum-esque scenegraph stuff via moderngl

Notes as I go:

 - Object*D gives an object a model matrix
 - Drawable gives you a pre-allocated model-view-projection matrix
 - The few things that want to know the window dims in pixels don't bother checking
   later on (i.e. set the uniform in `__init__` and that's it), but we'll always have
   a fullscreen window?