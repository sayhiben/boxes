# Copyright (C) 2024
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from dataclasses import dataclass

from boxes import *


@dataclass
class ConsoleProfile:
    y: float
    h: float
    front_height: float
    angle: float
    panel: float
    top: float
    d1: float
    d2: float
    has_top: bool
    removable_panel: bool
    glued_panel: bool


class MatrixStand(Boxes):
    """Matrix base composed of two Console2 ends and a central box"""

    ui_group = "Box"

    description = """
This generator combines two Console2-style ends with a simplified middle box.
The sides and bottom are generated as single pieces across all three sections.
"""

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=.5)

        self.buildArgParser(x=100, outside=False)

        # Front Console2 (faces forward)
        self.argparser.add_argument(
            "--front_y", action="store", type=float, default=100,
            help="depth of the front Console2 section (in mm)")
        self.argparser.add_argument(
            "--front_h", action="store", type=float, default=100,
            help="height of the front Console2 back wall (in mm)")
        self.argparser.add_argument(
            "--front_front_height", action="store", type=float, default=30,
            help="front height of the front Console2 (in mm)")
        self.argparser.add_argument(
            "--front_angle", action="store", type=float, default=50,
            help="panel angle of the front Console2 (90 degrees = upright)")
        self.argparser.add_argument(
            "--front_removable_panel", action="store", type=boolarg, default=True,
            help="front Console2 panel is removable")
        self.argparser.add_argument(
            "--front_glued_panel", action="store", type=boolarg, default=True,
            help="front Console2 panel is glued and not held by finger joints")

        # Back Console2 (faces backward)
        self.argparser.add_argument(
            "--back_y", action="store", type=float, default=100,
            help="depth of the back Console2 section (in mm)")
        self.argparser.add_argument(
            "--back_h", action="store", type=float, default=100,
            help="height of the back Console2 back wall (in mm)")
        self.argparser.add_argument(
            "--back_front_height", action="store", type=float, default=30,
            help="front height of the back Console2 (in mm)")
        self.argparser.add_argument(
            "--back_angle", action="store", type=float, default=50,
            help="panel angle of the back Console2 (90 degrees = upright)")
        self.argparser.add_argument(
            "--back_removable_panel", action="store", type=boolarg, default=True,
            help="back Console2 panel is removable")
        self.argparser.add_argument(
            "--back_glued_panel", action="store", type=boolarg, default=True,
            help="back Console2 panel is glued and not held by finger joints")

        # Middle box
        self.argparser.add_argument(
            "--box_y", action="store", type=float, default=60,
            help="depth of the middle box section (in mm)")
        self.argparser.add_argument(
            "--box_h", action="store", type=float, default=60,
            help="height of the middle box section (in mm)")

    def _console_profile(self, *, y: float, h: float, front_height: float, angle: float,
                         removable_panel: bool, glued_panel: bool) -> ConsoleProfile:
        if h <= front_height:
            raise ValueError("Console2 height must be larger than front_height.")

        panel = min(
            (h - front_height) / math.cos(math.radians(90 - angle)),
            y / math.cos(math.radians(angle)),
        )
        top = y - panel * math.cos(math.radians(angle))
        h = front_height + panel * math.sin(math.radians(angle))

        has_top = top > 0.1 * self.thickness
        if not has_top:
            top = 0.0

        d1 = self.thickness * math.cos(math.radians(angle))
        d2 = self.thickness * math.sin(math.radians(angle))

        return ConsoleProfile(
            y=y,
            h=h,
            front_height=front_height,
            angle=angle,
            panel=panel,
            top=top,
            d1=d1,
            d2=d2,
            has_top=has_top,
            removable_panel=removable_panel,
            glued_panel=glued_panel,
        )

    def _draw_panel_edge(self, length: float, removable_panel: bool, glued_panel: bool) -> None:
        t = self.thickness
        if removable_panel:
            self.rectangularHole(3 * t, 1.5 * t, 2.5 * t, 1.05 * t)
        if not removable_panel and not glued_panel:
            self.edges["f"](length)
        else:
            self.edge(length)
        if removable_panel:
            self.rectangularHole(-3 * t, 1.5 * t, 2.5 * t, 1.05 * t)

    def _draw_top_segment(self, profile: ConsoleProfile, *, forward: bool) -> None:
        if profile.top <= 0:
            return
        if profile.top > profile.d2:
            if forward:
                self.edge(profile.d2)
                self.edges["f"](profile.top - profile.d2)
            else:
                self.edges["f"](profile.top - profile.d2)
                self.edge(profile.d2)
        else:
            self.edge(profile.top)

    def _add_side_internal_features(
        self,
        *,
        front: ConsoleProfile,
        back: ConsoleProfile,
        box_y: float,
        box_h: float,
        bottom,
    ) -> None:
        base_y = bottom.startwidth()
        t = self.thickness

        pos_back = back.y - 0.5 * t
        pos_front = back.y + box_y + 0.5 * t

        self.fingerHolesAt(pos_back, base_y, back.h, 90)

        if box_y > 0:
            self.fingerHolesAt(pos_front, base_y, front.h, 90)

        if box_y > 0 and box_h > 0:
            clear, mid_len = self._finger_span(box_y)
            if mid_len > 0:
                self.fingerHolesAt(back.y + clear, base_y + box_h, mid_len, 0)

    def _combined_side(
        self,
        *,
        front: ConsoleProfile,
        back: ConsoleProfile,
        box_y: float,
        box_h: float,
        bottom,
        move=None,
        label: str = "",
    ) -> None:
        t = self.thickness
        total_depth = back.y + box_y + front.y

        max_h = max(front.h, back.h)
        tw = total_depth + 2 * self.edges["f"].spacing()
        th = max_h + bottom.spacing() + self.edges["f"].spacing()
        if self.move(tw, th, move, True):
            return

        self.moveTo(t, 0)
        with self.saved_context():
            # bottom
            bottom(total_depth)
            self.corner(90)

            # front vertical (outer front)
            front_vert = front.front_height + bottom.endwidth() - front.d1
            self.edges["f"](front_vert)
            if front.d1 > 0:
                self.edge(front.d1)
            self.corner(90 - front.angle)

            # front panel
            self._draw_panel_edge(front.panel, front.removable_panel, front.glued_panel)

            # box slope
            delta_h = back.h - front.h
            box_angle = math.degrees(math.atan2(delta_h, box_y)) if box_y else 0.0
            box_len = math.hypot(box_y, delta_h) if box_y else 0.0

            if front.has_top:
                self.corner(front.angle)
                self._draw_top_segment(front, forward=True)
                if box_len:
                    self.corner(-box_angle)
            else:
                if box_len:
                    self.corner(front.angle - box_angle)
                else:
                    self.corner(front.angle)

            if box_len:
                self.edge(box_len)
                self.corner(box_angle)

            # back top (reverse direction)
            if back.has_top:
                self._draw_top_segment(back, forward=False)

            # back panel
            self.corner(back.angle)
            self._draw_panel_edge(back.panel, back.removable_panel, back.glued_panel)
            self.corner(90 - back.angle)

            # back vertical (outer back)
            if back.d1 > 0:
                self.edge(back.d1)
            back_vert = back.front_height + bottom.startwidth() - back.d1
            self.edges["f"](back_vert)
            self.corner(90)

        self._add_side_internal_features(
            front=front,
            back=back,
            box_y=box_y,
            box_h=box_h,
            bottom=bottom,
        )

        self.move(tw, th, move, label=label)

    def _bottom_internal_holes(
        self, *, back: ConsoleProfile, box_y: float, width: float
    ) -> None:
        t = self.thickness
        pos_back = back.y - 0.5 * t
        clear, mid_len = self._finger_span(width)
        if mid_len > 0:
            self.fingerHolesAt(pos_back, clear, mid_len, 90)
        else:
            self.fingerHolesAt(pos_back, 0, width, 90)
        if box_y > 0:
            pos_front = back.y + box_y + 0.5 * t
            if mid_len > 0:
                self.fingerHolesAt(pos_front, clear, mid_len, 90)
            else:
                self.fingerHolesAt(pos_front, 0, width, 90)

    def panel_side(self, l, move=None):
        t = self.thickness
        s = 0.1 * t

        tw, th = l, 3 * t

        if not self.glued_panel:
            th += t

        if self.move(tw, th, move, True):
            return

        self.rectangularHole(3 * t, 1.5 * t, 3 * t, 1.05 * t)
        self.rectangularHole(l - 3 * t, 1.5 * t, 3 * t, 1.05 * t)
        self.rectangularHole(l / 2, 1.5 * t, 2 * t, t)
        if self.glued_panel:
            self.polyline(*([l, 90, t, 90, t, -90, t, -90, t, 90, t, 90] * 2))
        else:
            self.polyline(l, 90, 3 * t, 90)
            self.edges["f"](l)
            self.polyline(0, 90, 3 * t, 90)
        self.move(tw, th, move)

    def panel_lock(self, l, move=None):
        t = self.thickness

        l -= 4 * t
        tw, th = l, 2.5 * t

        if self.move(tw, th, move, True):
            return

        end = [
            l / 2 - 3 * t, -90, 1.5 * t, (90, .5 * t), t, (90, .5 * t),
            t, 90, .5 * t, -90, 0.5 * t, -90, 0, (90, .5 * t), 0, 90,
        ]

        self.moveTo(l / 2 - t, 2 * t, -90)
        self.polyline(*([t, 90, 2 * t, 90, t, -90] + end + [l] + list(reversed(end))))
        self.move(tw, th, move)

    def panel_cross_beam(self, l, move=None):
        t = self.thickness

        tw, th = l + 2 * t, 3 * t

        if self.move(tw, th, move, True):
            return

        self.moveTo(t, 0)
        self.polyline(*([l, 90, t, -90, t, 90, t, 90, t, -90, t, 90] * 2))

        self.move(tw, th, move)

    def _finger_span(self, length: float) -> tuple[float, float]:
        finger_len = self.edges["f"].settings.finger * self.thickness
        clear = min(finger_len, length / 8.0)
        mid_len = length - 2 * clear
        if mid_len <= 0:
            return 0.0, 0.0
        return clear, mid_len

    def _back_wall_bottom_edge(self, width: float):
        clear, mid_len = self._finger_span(width)
        if mid_len > 0:
            return edges.CompoundEdge(self, ("e", "F", "e"), (clear, mid_len, clear))
        return "F"

    def _panel_hardware_height(self, glued_panel: bool) -> float:
        t = self.thickness
        lock_height = 2.5 * t
        side_height = 3 * t + (0 if glued_panel else t)
        return 2 * (lock_height + self.spacing) + 2 * (side_height + self.spacing)

    def _rect_wall_size(self, x: float, y: float, edges_spec) -> tuple[float, float]:
        if isinstance(edges_spec, str):
            edges_spec = list(edges_spec)
        edges_list = [self.edges.get(e, e) for e in edges_spec]
        overallwidth = x + edges_list[-1].spacing() + edges_list[1].spacing()
        overallheight = y + edges_list[0].spacing() + edges_list[2].spacing()
        return overallwidth, overallheight

    def _console_row_height(self, profile: ConsoleProfile, x: float, bottom) -> float:
        t = self.thickness
        heights = []
        heights.append(self._rect_wall_size(
            profile.front_height - profile.d1,
            x,
            ("F", "e", "F", bottom),
        )[1])

        if profile.glued_panel:
            panel_x = x
            panel_edges = "EEEE"
        elif profile.removable_panel:
            panel_x = x - 2 * t
            panel_edges = "hEhE"
        else:
            panel_x = x
            panel_edges = "FEFE"
        heights.append(self._rect_wall_size(profile.panel, panel_x, panel_edges)[1])

        if profile.has_top:
            heights.append(self._rect_wall_size(
                profile.top - profile.d2,
                x,
                ("F", "E", "F", "F"),
            )[1])

        back_bottom_edge = self._back_wall_bottom_edge(x)
        heights.append(self._rect_wall_size(
            profile.h,
            x,
            ("F", back_bottom_edge, "F", "f"),
        )[1])

        row_height = max(heights) + self.spacing
        if profile.removable_panel:
            row_height = max(row_height, self._panel_hardware_height(profile.glued_panel))
        return row_height

    def _render_console_parts(
        self,
        profile: ConsoleProfile,
        x: float,
        bottom,
        *,
        box_y: float,
        box_h: float,
        label_prefix: str,
    ) -> None:
        t = self.thickness

        back_top_edge = "f"
        top_back_edge = "F"

        # Front wall (below panel)
        self.rectangularWall(
            profile.front_height - profile.d1,
            x,
            ("F", "e", "F", bottom),
            ignore_widths=[7, 4],
            move="right",
            label=f"{label_prefix} Front",
        )

        # Panel
        if profile.glued_panel:
            self.rectangularWall(profile.panel, x, "EEEE", move="right", label=f"{label_prefix} Panel")
        elif profile.removable_panel:
            self.rectangularWall(profile.panel, x - 2 * t, "hEhE", move="right", label=f"{label_prefix} Panel")
        else:
            self.rectangularWall(profile.panel, x, "FEFE", move="right", label=f"{label_prefix} Panel")

        # Top
        if profile.has_top:
            self.rectangularWall(
                profile.top - profile.d2,
                x,
                ("F", "E", "F", top_back_edge),
                move="right",
                label=f"{label_prefix} Top",
            )

        # Back wall (internal)
        back_bottom_edge = self._back_wall_bottom_edge(x)
        back_wall_callback = None
        if box_y > 0 and box_h > 0:
            box_top_pos = profile.h - box_h
            back_wall_callback = [lambda: self.fingerHolesAt(box_top_pos, 0, x, 90),
                                  None, None, None]
        self.rectangularWall(
            profile.h,
            x,
            ("F", back_bottom_edge, "F", back_top_edge),
            ignore_widths=[0, 3],
            callback=back_wall_callback,
            move="right",
            label=f"{label_prefix} Back Wall",
        )

        # Hardware for panel
        if profile.removable_panel:
            old_glued_panel = bool(getattr(self, "glued_panel", profile.glued_panel))
            old_removable_panel = bool(getattr(self, "removable_panel", profile.removable_panel))
            self.glued_panel = bool(profile.glued_panel)
            self.removable_panel = bool(profile.removable_panel)
            try:
                if profile.glued_panel:
                    self.panel_cross_beam(x - 2.05 * t, "rotated right")
                    self.panel_cross_beam(x - 2.05 * t, "rotated right")

                self.panel_lock(profile.panel, "up")
                self.panel_lock(profile.panel, "up")
                self.panel_side(profile.panel, "up")
                self.panel_side(profile.panel, "up")
            finally:
                self.glued_panel = old_glued_panel
                self.removable_panel = old_removable_panel

    def render(self):
        x = self.x
        front_y = self.front_y
        back_y = self.back_y
        box_y = self.box_y
        front_h = self.front_h
        back_h = self.back_h
        box_h = self.box_h

        bottom = self.edges["F"]

        if self.outside:
            x = self.adjustSize(x)
            front_y = self.adjustSize(front_y)
            back_y = self.adjustSize(back_y)
            box_y = self.adjustSize(box_y)
            front_h = self.adjustSize(front_h, bottom)
            back_h = self.adjustSize(back_h, bottom)
            box_h = self.adjustSize(box_h, bottom)

        front = self._console_profile(
            y=front_y,
            h=front_h,
            front_height=self.front_front_height,
            angle=self.front_angle,
            removable_panel=self.front_removable_panel,
            glued_panel=self.front_glued_panel,
        )
        back = self._console_profile(
            y=back_y,
            h=back_h,
            front_height=self.back_front_height,
            angle=self.back_angle,
            removable_panel=self.back_removable_panel,
            glued_panel=self.back_glued_panel,
        )

        if box_h > min(front.h, back.h):
            raise ValueError("box_h must be <= both Console2 heights so the sides cover the box.")

        total_depth = back.y + box_y + front.y

        side_th = max(front.h, back.h) + bottom.spacing() + self.edges["f"].spacing()
        row1_height = side_th + self.spacing

        bottom_height = self._rect_wall_size(total_depth, x, "ffff")[1] + self.spacing
        row2_height = bottom_height

        box_edge = None
        if box_y > 0 and box_h > 0:
            clear, mid_len = self._finger_span(box_y)
            if mid_len > 0:
                box_edge = edges.CompoundEdge(self, ("e", "f", "e"), (clear, mid_len, clear))
            else:
                box_edge = "e"
            box_top_height = self._rect_wall_size(box_y, x, (box_edge, "f", box_edge, "f"))[1] + self.spacing
            row2_height = max(row2_height, box_top_height)

        row3_height = self._console_row_height(front, x, bottom)

        row_y = 0.0
        with self.saved_context():
            self.moveTo(0, row_y)
            self._combined_side(front=front, back=back, box_y=box_y, box_h=box_h,
                                bottom=bottom, move="right", label="Left Side")
            self._combined_side(front=front, back=back, box_y=box_y, box_h=box_h,
                                bottom=bottom, move="right", label="Right Side")
        row_y += row1_height

        with self.saved_context():
            self.moveTo(0, row_y)
            self.rectangularWall(
                total_depth,
                x,
                "ffff",
                callback=[lambda: self._bottom_internal_holes(back=back, box_y=box_y, width=x),
                          None, None, None],
                move="right",
                label="Bottom",
            )
            if box_edge is not None:
                self.rectangularWall(box_y, x, (box_edge, "f", box_edge, "f"),
                                     move="right", label="Box Top")
        row_y += row2_height

        with self.saved_context():
            self.moveTo(0, row_y)
            self._render_console_parts(
                front,
                x,
                bottom,
                box_y=box_y,
                box_h=box_h,
                label_prefix="Front Console2",
            )
        row_y += row3_height

        with self.saved_context():
            self.moveTo(0, row_y)
            self._render_console_parts(
                back,
                x,
                bottom,
                box_y=box_y,
                box_h=box_h,
                label_prefix="Back Console2",
            )
