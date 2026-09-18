#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
import pygame;

from .fontcatalog import FontSelection, filter_font_names, sort_font_names, system_font_names;
from .theme import DEFAULT_THEME;
from .widgets import CheckBox, Slider, TextInput, Widget, draw_clipped_text;


DEFAULT_SMALL_CAPS_SCALE=0.65;


class FontPicker(Widget):
    def __init__(self,rect,font,family="monospace",bold=False,italic=False,small_caps=False,small_caps_scale=DEFAULT_SMALL_CAPS_SCALE,theme=None,items=(),monospace_only=False,max_rows=8,on_change=None,tab_index=0,show_scale=False,preview=False,preview_size=22):
        super().__init__(rect,focusable=True,tab_index=tab_index);
        self.font=font; self.theme=theme or DEFAULT_THEME; self.max_rows=max(1,int(max_rows)); self.on_change=on_change;
        self.monospace_only=bool(monospace_only); self.open=False; self.offset=0; self.highlight=0; self.filter_query=""; self.scrollbar_width=16; self.drag_scrollbar=False; self.drag_scroll_y=0; self.drag_scroll_offset=0;
        self.show_scale=bool(show_scale or preview); self.preview=bool(preview); self.preview_size=max(10,int(preview_size));
        row_h=max(38,self.font.get_height()+16); style_h=max(32,self.font.get_height()+10);
        self.combo_rect=pygame.Rect(self.rect.x,self.rect.y,self.rect.width,row_h);
        self.style_rect=pygame.Rect(self.rect.x,self.combo_rect.bottom+6,self.rect.width,style_h);
        cursor=self.style_rect.bottom;
        self.scale_rect=None; self.preview_rect=None;
        if self.show_scale:
            scale_h=max(44,self.font.get_height()+24); self.scale_rect=pygame.Rect(self.rect.x,cursor+6,self.rect.width,scale_h); cursor=self.scale_rect.bottom;
        if self.preview:
            preview_h=max(84,self.font.get_height()*4+10); self.preview_rect=pygame.Rect(self.rect.x,cursor+6,self.rect.width,preview_h); cursor=self.preview_rect.bottom;
        self.rect.height=(cursor-self.rect.y);
        self.arrow_rect=pygame.Rect(self.combo_rect.right-36,self.combo_rect.y,36,self.combo_rect.height);
        input_rect=pygame.Rect(self.combo_rect.x,self.combo_rect.y,max(1,self.combo_rect.width-36),self.combo_rect.height);
        self.input=TextInput(input_rect,self.font,text=str(family or "monospace"),placeholder="type to filter fonts",max_length=128,theme=self.theme,clear_on_first_edit=True);
        self.selected_family=str(family or "monospace");
        source=tuple(items or ());
        if not source: source=system_font_names(pygame.font,current=self.selected_family,monospace_only=self.monospace_only);
        self.items=sort_font_names(source,current=self.selected_family);
        self.bold_box=CheckBox(self._style_box_rect(0),"Bold",self.font,checked=bold,theme=self.theme,on_change=lambda *_unused:self._notify());
        self.italic_box=CheckBox(self._style_box_rect(1),"Italic",self.font,checked=italic,theme=self.theme,on_change=lambda *_unused:self._notify());
        self.small_caps_box=CheckBox(self._style_box_rect(2),"Small Caps",self.font,checked=small_caps,theme=self.theme,on_change=lambda *_unused:self._notify());
        percent=max(50.0,min(85.0,float(small_caps_scale)*100.0));
        self.scale_slider=Slider(self.scale_rect,minimum=50,maximum=85,value=percent,step=1,on_change=lambda *_unused:self._notify(),font=self.font,label="Small Caps scale (%)",theme=self.theme) if self.scale_rect is not None else None;
        self._sync_highlight();

    def _style_box_rect(self,index):
        gap=6; widths=(0.26,0.27,0.47); x=self.style_rect.x;
        for pos,fraction in enumerate(widths):
            width=int(round(self.style_rect.width*fraction))-gap;
            if pos==index: return pygame.Rect(x,self.style_rect.y,max(1,width),self.style_rect.height);
            x+=width+gap;
        return pygame.Rect(self.style_rect);

    @property
    def overlay_active(self):
        return bool(self.open);

    def set_focus(self,focused=True):
        super().set_focus(focused); self.input.set_focus(focused);
        if not focused: self.close_popup(restore=False);

    def filtered_items(self):
        return filter_font_names(self.items,self.filter_query);

    def popup_rect(self):
        rows=min(self.max_rows,len(self.filtered_items()));
        return pygame.Rect(self.combo_rect.x,self.combo_rect.bottom+2,self.combo_rect.width,max(0,rows*30+4 if rows else 0));

    def get_rect(self):
        popup=self.popup_rect();
        return self.rect.union(popup) if self.open and popup.height>0 else self.rect;

    def small_caps_scale(self):
        return float(self.scale_slider.value)/100.0 if self.scale_slider is not None else DEFAULT_SMALL_CAPS_SCALE;

    def selection(self):
        return FontSelection(self.selected_family,bool(self.bold_box.checked),bool(self.italic_box.checked),bool(self.small_caps_box.checked),self.small_caps_scale());

    def value(self):
        return self.selected_family;

    def set_selection(self,family=None,bold=None,italic=None,small_caps=None,small_caps_scale=None,notify=False):
        if family is not None:
            self.selected_family=str(family or "monospace").strip() or "monospace";
            if self.selected_family.casefold() not in {item.casefold() for item in self.items}: self.items=sort_font_names(self.items,current=self.selected_family);
            self.input.set_value(self.selected_family);
        if bold is not None: self.bold_box.checked=bool(bold);
        if italic is not None: self.italic_box.checked=bool(italic);
        if small_caps is not None: self.small_caps_box.checked=bool(small_caps);
        if small_caps_scale is not None and self.scale_slider is not None: self.scale_slider.set_value(float(small_caps_scale)*100.0,notify=False);
        self.filter_query=""; self._sync_highlight();
        if notify: self._notify();
        return self.selection();

    def _notify(self):
        if self.on_change is not None: self.on_change(self,self.selection());
        return self.selection();

    def _sync_highlight(self):
        visible=self.filtered_items(); probe=self.selected_family.casefold();
        self.highlight=next((index for index,item in enumerate(visible) if item.casefold()==probe),0);
        self._ensure_highlight_visible();

    def _ensure_highlight_visible(self):
        visible=self.filtered_items();
        if not visible: self.highlight=0; self.offset=0; return;
        self.highlight=max(0,min(len(visible)-1,self.highlight));
        if self.highlight<self.offset: self.offset=self.highlight;
        if self.highlight>=self.offset+self.max_rows: self.offset=self.highlight-self.max_rows+1;
        self.offset=max(0,min(self.offset,max(0,len(visible)-self.max_rows)));

    def open_popup(self,filter_query=""):
        self.open=True; self.filter_query=str(filter_query or ""); self.offset=0; self._sync_highlight();
        return True;

    def close_popup(self,restore=False):
        if restore: self.input.set_value(self.selected_family);
        self.open=False; self.filter_query=""; self.offset=0; self.drag_scrollbar=False; self._sync_highlight();
        return True;

    def cancel_pointer(self):
        self.drag_scrollbar=False;
        if self.scale_slider is not None: self.scale_slider.dragging=False;
        for box in (self.bold_box,self.italic_box,self.small_caps_box): box.cancel_pointer();
        return True;

    def _commit(self,index=None):
        visible=self.filtered_items();
        if visible:
            index=self.highlight if index is None else int(index); index=max(0,min(len(visible)-1,index)); self.selected_family=visible[index];
        else:
            typed=str(self.input.value() or "").strip();
            if typed: self.selected_family=typed;
        self.input.set_value(self.selected_family); self.close_popup(restore=False); self._notify();
        return True;

    def _update_filter_from_input(self):
        self.filter_query=str(self.input.value() or ""); self.open=True; self.offset=0; self.highlight=0; self._ensure_highlight_visible();
        return True;

    def popup_list_rect(self):
        popup=self.popup_rect();
        if popup.height<=0: return popup;
        return pygame.Rect(popup.x+2,popup.y+2,max(1,popup.width-self.scrollbar_width-4),max(1,popup.height-4));

    def scrollbar_rect(self):
        popup=self.popup_rect();
        return pygame.Rect(max(popup.x,popup.right-self.scrollbar_width),popup.y+2,max(1,self.scrollbar_width-2),max(1,popup.height-4));

    def scrollbar_thumb_rect(self):
        bar=self.scrollbar_rect(); visible=self.filtered_items(); total=len(visible);
        if total<=0: return pygame.Rect(bar.x,bar.y,bar.width,bar.height);
        shown=min(self.max_rows,total); thumb_h=max(18,int(round(bar.height*(shown/max(1,total))))); thumb_h=min(bar.height,thumb_h);
        limit=max(0,total-self.max_rows);
        if limit<=0: thumb_y=bar.y;
        else: thumb_y=bar.y+int(round((bar.height-thumb_h)*(self.offset/limit)));
        return pygame.Rect(bar.x,thumb_y,bar.width,thumb_h);

    def _scroll_to_offset(self,value):
        limit=max(0,len(self.filtered_items())-self.max_rows); self.offset=max(0,min(limit,int(value)));
        return self.offset;

    def _scroll_by(self,rows):
        return self._scroll_to_offset(self.offset+int(rows));

    def _scrollbar_drag_to(self,y):
        bar=self.scrollbar_rect(); thumb=self.scrollbar_thumb_rect(); limit=max(0,len(self.filtered_items())-self.max_rows);
        travel=max(1,bar.height-thumb.height);
        if limit<=0: return self._scroll_to_offset(0);
        delta=int(y)-self.drag_scroll_y; return self._scroll_to_offset(self.drag_scroll_offset+round((delta/travel)*limit));

    def _row_at(self,pos):
        area=self.popup_list_rect();
        if not area.collidepoint(pos): return None;
        row=max(0,(int(pos[1])-area.y)//30); index=self.offset+row;
        return index if index<len(self.filtered_items()) and row<self.max_rows else None;

    def _preview_family(self):
        visible=self.filtered_items();
        if self.open and visible and 0<=self.highlight<len(visible): return str(visible[self.highlight]);
        return str(self.selected_family or "monospace");

    def _preview_font(self,size=None):
        size=max(8,int(size or self.preview_size)); family=self._preview_family(); bold=bool(self.bold_box.checked); italic=bool(self.italic_box.checked);
        try: return pygame.font.SysFont(family,size,bold=bold,italic=italic);
        except TypeError: return pygame.font.SysFont(family,size,bold=bold);
        except Exception: return pygame.font.Font(None,size);

    @staticmethod
    def _ink_center_offset(rendered,cell_width):
        try:
            bounds=rendered.get_bounding_rect(min_alpha=1);
            if int(bounds.width)>0: return int(round((int(cell_width)-int(bounds.width))/2.0))-int(bounds.x);
        except Exception: pass;
        try: width=int(rendered.get_width());
        except Exception: width=int(cell_width);
        return int(round((int(cell_width)-width)/2.0));

    def _draw_preview_line(self,screen,text,y):
        if self.preview_rect is None: return;
        normal=self._preview_font(self.preview_size); scale=self.small_caps_scale(); small=self._preview_font(max(6,int(round(self.preview_size*scale))));
        try: normal_ascent=max(1,int(normal.get_ascent()));
        except Exception: normal_ascent=max(1,int(normal.get_height()));
        try: small_ascent=max(1,int(small.get_ascent()));
        except Exception: small_ascent=max(1,int(small.get_height()));
        baseline=int(y)+normal_ascent; x=self.preview_rect.x+10; right=self.preview_rect.right-8;
        fixed_width=None;
        if self.monospace_only:
            try: fixed_width=max(normal.size(char)[0] for char in "iMW0@#_");
            except Exception: fixed_width=None;
        for char in str(text):
            use_small=bool(self.small_caps_box.checked and char.islower()); glyph=char;
            renderer=normal;
            if use_small:
                upper=char.upper();
                if len(upper)==1: glyph=upper; renderer=small;
                else: use_small=False;
            rendered=renderer.render(glyph,True,self.theme.text);
            if fixed_width is not None:
                advance=fixed_width; xoff=self._ink_center_offset(rendered,advance) if use_small else max(0,(advance-rendered.get_width())//2);
            else:
                advance=max(1,normal.size(char.upper() if use_small else char)[0]); xoff=max(0,(advance-rendered.get_width())//2);
            yoff=baseline-(small_ascent if use_small else normal_ascent);
            if x+advance>right: break;
            screen.blit(rendered,(x+xoff,yoff)); x+=advance;

    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            if self.arrow_rect.collidepoint(event.pos):
                if self.open: return self.close_popup(restore=True);
                self.input.set_value(self.selected_family); return self.open_popup("");
            if self.input.rect.collidepoint(event.pos):
                if not self.open: self.open_popup("");
                return self.input.handle_event(event) or True;
            if self.open and self.scrollbar_rect().collidepoint(event.pos):
                if getattr(event,"button",1)==1:
                    thumb=self.scrollbar_thumb_rect();
                    if thumb.collidepoint(event.pos):
                        self.drag_scrollbar=True; self.drag_scroll_y=int(event.pos[1]); self.drag_scroll_offset=self.offset;
                    elif event.pos[1]<thumb.y: self._scroll_by(-self.max_rows);
                    else: self._scroll_by(self.max_rows);
                return True;
            if self.open and getattr(event,"button",1) in (4,5) and self.popup_rect().collidepoint(event.pos):
                self._scroll_by(-3 if event.button==4 else 3); return True;
            if self.open:
                index=self._row_at(event.pos);
                if index is not None and getattr(event,"button",1)==1: self.highlight=index; return self._commit(index);
            for box in (self.bold_box,self.italic_box,self.small_caps_box):
                if box.rect.collidepoint(event.pos): return box.handle_event(event);
            if self.scale_slider is not None and self.scale_slider.rect.collidepoint(event.pos): return self.scale_slider.handle_event(event);
            if self.open: self.close_popup(restore=True);
            return self.rect.collidepoint(event.pos);
        if event.type==pygame.MOUSEMOTION:
            if self.drag_scrollbar: self._scrollbar_drag_to(event.pos[1]); return True;
            if self.scale_slider is not None and self.scale_slider.dragging: return self.scale_slider.handle_event(event);
        if event.type==pygame.MOUSEBUTTONUP:
            if self.drag_scrollbar:
                self.drag_scrollbar=False; return True;
            if self.scale_slider is not None and self.scale_slider.dragging: return self.scale_slider.handle_event(event);
            for box in (self.bold_box,self.italic_box,self.small_caps_box):
                if box.handle_event(event): return True;
            return False;
        if event.type==pygame.MOUSEWHEEL and self.open:
            try: pointer=pygame.mouse.get_pos(); over=self.popup_rect().collidepoint(pointer) or self.combo_rect.collidepoint(pointer);
            except Exception: over=True;
            if over: self._scroll_by(-int(event.y)*3); return True;
            return False;
        if event.type==pygame.KEYDOWN and self.has_focus:
            if event.key==pygame.K_F4:
                return self.close_popup(restore=True) if self.open else self.open_popup("");
            if event.key==pygame.K_ESCAPE and self.open: return self.close_popup(restore=True);
            if event.key in (pygame.K_UP,pygame.K_DOWN):
                if not self.open: self.open_popup("");
                visible=self.filtered_items();
                if visible:
                    self.highlight=max(0,min(len(visible)-1,self.highlight+(-1 if event.key==pygame.K_UP else 1))); self._ensure_highlight_visible();
                return True;
            if self.open and event.key in (pygame.K_PAGEUP,pygame.K_PAGEDOWN,pygame.K_HOME,pygame.K_END):
                visible=self.filtered_items();
                if visible:
                    if event.key==pygame.K_HOME: self.highlight=0;
                    elif event.key==pygame.K_END: self.highlight=len(visible)-1;
                    else: self.highlight=max(0,min(len(visible)-1,self.highlight+(-self.max_rows if event.key==pygame.K_PAGEUP else self.max_rows)));
                    self._ensure_highlight_visible();
                return True;
            if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                if self.open: return self._commit();
            before=self.input.value(); handled=self.input.handle_event(event);
            if handled and self.input.value()!=before: self._update_filter_from_input();
            return handled;
        if event.type==pygame.TEXTINPUT and self.has_focus:
            before=self.input.value(); handled=self.input.handle_event(event);
            if handled and self.input.value()!=before: self._update_filter_from_input();
            return handled;
        return False;

    def update(self,dt):
        self.input.update(dt);

    def draw(self,screen):
        self.input.draw(screen);
        pygame.draw.rect(screen,self.theme.button,self.arrow_rect,border_radius=6); pygame.draw.rect(screen,self.theme.line,self.arrow_rect,1,border_radius=6);
        draw_clipped_text(screen,self.font,"▼",self.theme.button_text,self.arrow_rect,align="center",valign="middle");
        self.bold_box.draw(screen); self.italic_box.draw(screen); self.small_caps_box.draw(screen);
        if self.scale_slider is not None:
            self.scale_slider.label="Small Caps scale (%)"; self.scale_slider.draw(screen);
        if self.preview_rect is not None:
            pygame.draw.rect(screen,self.theme.panel,self.preview_rect,border_radius=6); pygame.draw.rect(screen,self.theme.line,self.preview_rect,1,border_radius=6);
            title_rect=pygame.Rect(self.preview_rect.x+8,self.preview_rect.y+4,self.preview_rect.width-16,max(16,self.font.get_height())); draw_clipped_text(screen,self.font,"Preview — {}".format(self._preview_family()),self.theme.muted,title_rect,valign="middle");
            y=self.preview_rect.y+max(22,self.font.get_height()+8); self._draw_preview_line(screen,"ABCDEF abcdef  Σσ Ωω Ññ",y); self._draw_preview_line(screen,"The quick brown fox — 0123456789",y+max(24,self.preview_size+6));
        if not self.open: return;
        visible=self.filtered_items(); popup=self.popup_rect();
        if popup.height<=0: return;
        pygame.draw.rect(screen,self.theme.panel,popup); pygame.draw.rect(screen,self.theme.line,popup,2);
        area=self.popup_list_rect();
        for row,item in enumerate(visible[self.offset:self.offset+self.max_rows]):
            index=self.offset+row; rect=pygame.Rect(area.x,area.y+row*30,area.width,30);
            if index==self.highlight: pygame.draw.rect(screen,self.theme.button_alt,rect);
            draw_clipped_text(screen,self.font,item,self.theme.text,rect.inflate(-8,-2),valign="middle");
        bar=self.scrollbar_rect(); thumb=self.scrollbar_thumb_rect();
        pygame.draw.rect(screen,self.theme.line,bar); pygame.draw.rect(screen,self.theme.button,thumb,border_radius=3);
