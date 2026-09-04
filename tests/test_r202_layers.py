import pytest;
pygame=pytest.importorskip("pygame");
from sumgui.graphics import GraphicsSurface;
from sumui import modern_mode;


def test_layer_order_and_border_pattern_headless():
    pygame.init();
    surface=GraphicsSurface(modern_mode(64,48));
    surface.set_paper((10,20,30));
    surface.plot(3,3,(255,255,255));
    assert surface.point(3,3)[:3] == (255,255,255);
    surface.sort_layers(("GRAPHICS","BACKGROUND"));
    assert surface.point(3,3)[:3] == (10,20,30);
    surface.sort_layers(("BACKGROUND","GRAPHICS"));
    assert surface.point(3,3)[:3] == (255,255,255);
    surface.set_border_ink((255,0,0)); surface.set_border_paper((0,0,255));
    surface.set_border_pattern((0xAA,)*8); surface.set_border_offset(1,0); surface.scroll_border(1,0);
    assert surface.border_pattern is not None;
    pygame.quit();
