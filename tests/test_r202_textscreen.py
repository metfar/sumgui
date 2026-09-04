import pytest;
pytest.importorskip("pygame");
from sumui import CursorState;
from sumgui.textscreen import GuiTextScreen;


class Target:
    def __init__(self): self.states=[];
    def set_cursor_state(self,state): self.states.append(state);


def test_gui_textscreen_tracks_pixel_viewport_and_cell_metrics():
    viewport=[800,500]; cell=[10,20]; target=Target();
    screen=GuiTextScreen(lambda: tuple(viewport),lambda: tuple(cell),cursor_target=target);
    assert screen.size()==(80,25);
    viewport[:]=[390,360]; assert screen.size()==(39,18);
    cell[:]=[13,20]; assert screen.size()==(30,18);
    screen.cursor(False); screen.cursor(True); screen.cursor("block");
    assert target.states==[CursorState.HIDDEN,CursorState.NORMAL,CursorState.BLOCK];
