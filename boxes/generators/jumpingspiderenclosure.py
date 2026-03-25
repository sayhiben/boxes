# Copyright (C) 2026
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

# mypy: disable-error-code="attr-defined,union-attr"

from __future__ import annotations

from dataclasses import dataclass
import math

from boxes import *


@dataclass(frozen=True)
class _DoorLayout:
    opening_x: float
    opening_y: float
    opening_w: float
    opening_h: float
    panel_w: float
    panel_h: float
    panel_left: float
    panel_bottom: float
    rail_length: float
    rail_mount_margin: float
    top_lip_y: float
    bottom_lip_y: float
    magnet_inset: float
    handle_slot_x: float
    handle_mount_bottom: float
    handle_tab_size: float
    handle_tab_centers: tuple[float, ...]


class JumpingSpiderEnclosure(Boxes):
    """Two-part acrylic jumping spider enclosure with a removable sliding front door."""

    ui_group = "Box"

    description = """
Default sizing is approximately 3" x 3" x 6" outside using a taller magnetic top shell and a shorter base shell.

Features:

* coarser finger-jointed acrylic walls
* abutted split between the top and bottom shells
* rounded magnetic corner brackets at the split
* centered circular side vents in the top shell
* removable left-sliding front door that rides in front of the front panel
* front-mounted rail lips with backings that create a flush external sliding channel
* separate pull handle that mounts directly into the sliding door
"""

    def __init__(self) -> None:
        super().__init__()
        self.addSettingsArgs(
            edges.FingerJointSettings,
            finger=3.0,
            space=3.0,
            surroundingspaces=1.0,
        )
        self.buildArgParser(x=76.2, y=76.2, h=152.4, outside=True)
        self.argparser.add_argument(
            "--split_ratio",
            action="store",
            type=float,
            default=2.0 / 3.0,
            help="fraction of the total height used by the top shell",
        )
        self.argparser.add_argument(
            "--vent_diameter",
            action="store",
            type=float,
            default=47.5,
            help="diameter of the round side vents in mm",
        )
        self.argparser.add_argument(
            "--magnet_diameter",
            action="store",
            type=float,
            default=6.0,
            help="nominal magnet diameter in mm",
        )
        self.argparser.add_argument(
            "--door_magnet_margin",
            action="store",
            type=float,
            default=1.5,
            help="minimum material left between each door magnet hole and the nearest door edge in mm",
        )
        self.argparser.add_argument(
            "--door_overlap",
            action="store",
            type=float,
            default=9.0,
            help="how much the sliding door overlaps the opening on each side in mm",
        )
        self.argparser.add_argument(
            "--door_clearance",
            action="store",
            type=float,
            default=0.15,
            help="extra clearance around the sliding door in mm",
        )
        self.argparser.add_argument(
            "--door_top_margin",
            action="store",
            type=float,
            default=25.4,
            help="clear unobstructed space above the door opening in mm",
        )
        self.argparser.add_argument(
            "--rail_width",
            action="store",
            type=float,
            default=10.0,
            help="visible width of each sliding rail lip in mm",
        )
        self.argparser.add_argument(
            "--corner_bracket",
            action="store",
            type=float,
            default=14.0,
            help="outer radius of the rounded magnetic corner brackets in mm",
        )
        self.argparser.add_argument(
            "--handle_depth",
            action="store",
            type=float,
            default=8.0,
            help="projection depth of the removable door handle in mm",
        )
        self.argparser.add_argument(
            "--handle_x",
            action="store",
            type=float,
            default=10.0,
            help="center position of the handle tabs from the left edge of the door in mm",
        )
        self.argparser.add_argument(
            "--handle_height",
            action="store",
            type=float,
            default=24.0,
            help="height of the door pull handle in mm",
        )

    def _prepare_dimensions(self) -> None:
        t = self.thickness

        self.slot_clearance = max(0.15, 0.05 * t)
        self.magnet_hole = self.magnet_diameter
        self.rail_depth = max(t + self.door_clearance, t + 0.05)
        self.bracket_border = max(1.5, 0.5 * t)
        self.bracket_hole_offset = 0.5 * self.magnet_hole + self.bracket_border
        min_bracket_size = (
            math.sqrt(2.0) * self.bracket_hole_offset
            + 0.5 * self.magnet_hole
            + self.bracket_border
        )
        self.bracket_size = max(self.corner_bracket, min_bracket_size)
        self.rail_tab_width = max(8.0, 2.5 * t)
        self.bracket_tab_width = max(3.5, 1.2 * t)

        if self.outside:
            self.inner_x = self.adjustSize(self.x)
            self.inner_y = self.adjustSize(self.y)
            upper_outer = self.h * self.split_ratio
            lower_outer = self.h - upper_outer
            self.upper_h = upper_outer - t
            self.lower_h = lower_outer - t
        else:
            self.inner_x = self.x
            self.inner_y = self.y
            self.upper_h = self.h * self.split_ratio
            self.lower_h = self.h - self.upper_h

        if self.split_ratio <= 0.0 or self.split_ratio >= 1.0:
            raise ValueError("split_ratio must be between 0 and 1")
        if min(self.inner_x, self.inner_y, self.upper_h, self.lower_h) <= 0:
            raise ValueError("enclosure dimensions must stay positive after thickness adjustments")
        if self.vent_diameter >= min(self.inner_y, self.upper_h) - 2 * t:
            raise ValueError("vent_diameter is too large for the top side panels")
        if self.bracket_size >= min(self.inner_x, self.inner_y) - 2 * t:
            raise ValueError("corner_bracket is too large for the shell footprint")
        if self.lower_h <= self.bracket_size + 2 * t:
            raise ValueError("bottom shell is too short for the requested split and corner bracket")
        if self.upper_h <= self.vent_diameter + 2 * t:
            raise ValueError("top shell is too short for the requested vent diameter")

        magnet_inset = max(
            0.5 * self.magnet_hole + self.door_magnet_margin,
            0.5 * self.door_overlap,
        )
        frame_side = max(self.door_overlap + 1.0, 0.5 * self.magnet_hole + 2.0, 2.5 * t)
        frame_margin = self.door_overlap + magnet_inset + 1.0
        rail_gap = self.door_clearance
        rail_frame = self.door_overlap + t + rail_gap
        rail_slot_offset = rail_gap + 0.5 * t
        top_frame = max(self.door_top_margin, frame_margin, rail_frame)
        bottom_frame = max(frame_margin, rail_frame, 0.14 * self.upper_h)

        opening_w = self.inner_x - 2 * frame_side
        opening_h = self.upper_h - top_frame - bottom_frame
        if opening_w <= self.magnet_hole + 2 * t:
            raise ValueError("door opening is too narrow; reduce door_overlap or magnet diameter")
        if opening_h <= self.magnet_hole + 2 * t:
            raise ValueError("door opening is too short; adjust split_ratio or door parameters")

        panel_w = opening_w + 2 * self.door_overlap
        panel_h = opening_h + 2 * self.door_overlap
        panel_left = frame_side - self.door_overlap
        panel_bottom = bottom_frame - self.door_overlap
        if 2 * magnet_inset >= min(panel_w, panel_h):
            raise ValueError("door magnets do not fit inside the requested door overlap")

        rail_mount_margin = max(1.5, 0.5 * t)
        rail_mount_span = self.inner_x - 2 * rail_mount_margin
        rail_length = self.inner_x
        if 3 * self.rail_tab_width >= rail_mount_span:
            self.rail_tab_width = rail_mount_span / 4.0
        if 3 * self.bracket_tab_width >= self.bracket_size:
            self.bracket_tab_width = self.bracket_size / 4.0

        max_handle_height = panel_h - 2 * magnet_inset - 2.0
        if self.handle_height > max_handle_height:
            raise ValueError("door handle is too tall for the door and magnet layout")

        handle_tab_size = max(4.0, 1.25 * t)
        min_handle_gap = max(1.0, 0.35 * t)
        handle_tab_count = max(1, min(4, int(self.handle_height / max(8.0, 2.5 * t))))
        while handle_tab_count > 1 and (
            self.handle_height - handle_tab_count * handle_tab_size
            < (handle_tab_count + 1) * min_handle_gap
        ):
            handle_tab_count -= 1
        if self.handle_height - handle_tab_count * handle_tab_size < 2 * min_handle_gap:
            raise ValueError("door handle does not have enough room for mounting tabs")

        handle_slot_w = t + self.slot_clearance
        min_handle_x = 0.5 * handle_slot_w
        max_handle_x = panel_w - 0.5 * handle_slot_w
        handle_slot_x = self.handle_x
        if handle_slot_x <= 0 or not min_handle_x <= handle_slot_x <= max_handle_x:
            raise ValueError("handle_x must place the handle tabs inside the door")
        handle_mount_bottom = 0.5 * (panel_h - self.handle_height)
        handle_tab_centers = self._tab_centers(
            self.handle_height,
            handle_tab_size,
            handle_tab_count,
        )
        self._validate_handle_slots(
            panel_w,
            panel_h,
            magnet_inset,
            handle_slot_x,
            handle_mount_bottom,
            handle_tab_centers,
            handle_slot_w,
            handle_tab_size + self.slot_clearance,
        )

        self.door = _DoorLayout(
            opening_x=frame_side,
            opening_y=bottom_frame,
            opening_w=opening_w,
            opening_h=opening_h,
            panel_w=panel_w,
            panel_h=panel_h,
            panel_left=panel_left,
            panel_bottom=panel_bottom,
            rail_length=rail_length,
            rail_mount_margin=rail_mount_margin,
            top_lip_y=panel_bottom + panel_h + rail_slot_offset,
            bottom_lip_y=panel_bottom - rail_slot_offset,
            magnet_inset=magnet_inset,
            handle_slot_x=handle_slot_x,
            handle_mount_bottom=handle_mount_bottom,
            handle_tab_size=handle_tab_size,
            handle_tab_centers=handle_tab_centers,
        )

    def _tab_centers(self, span: float, tab_width: float, count: int) -> tuple[float, ...]:
        gap = (span - count * tab_width) / (count + 1)
        return tuple(
            gap * (index + 1) + tab_width * (index + 0.5)
            for index in range(count)
        )

    def _two_tab_centers(self, span: float, tab_width: float) -> tuple[float, float]:
        first, second = self._tab_centers(span, tab_width, 2)
        return first, second

    def _slot_intersects_circle(
        self,
        slot_x: float,
        slot_y: float,
        slot_w: float,
        slot_h: float,
        circle_x: float,
        circle_y: float,
        circle_r: float,
    ) -> bool:
        dx = max(abs(circle_x - slot_x) - 0.5 * slot_w, 0.0)
        dy = max(abs(circle_y - slot_y) - 0.5 * slot_h, 0.0)
        return dx * dx + dy * dy < circle_r * circle_r

    def _validate_handle_slots(
        self,
        panel_w: float,
        panel_h: float,
        magnet_inset: float,
        handle_slot_x: float,
        handle_mount_bottom: float,
        handle_tab_centers: tuple[float, ...],
        handle_slot_w: float,
        handle_slot_h: float,
    ) -> None:
        magnet_centers = (
            (magnet_inset, magnet_inset),
            (panel_w - magnet_inset, magnet_inset),
            (magnet_inset, panel_h - magnet_inset),
            (panel_w - magnet_inset, panel_h - magnet_inset),
        )
        magnet_radius = 0.5 * self.magnet_hole

        for center in handle_tab_centers:
            slot_y = handle_mount_bottom + center
            for magnet_x, magnet_y in magnet_centers:
                if self._slot_intersects_circle(
                    handle_slot_x,
                    slot_y,
                    handle_slot_w,
                    handle_slot_h,
                    magnet_x,
                    magnet_y,
                    magnet_radius,
                ):
                    raise ValueError("handle_x places a handle tab into a door magnet hole")

    def _slots_for_span(self, origin_x: float, span: float, y: float, tab_width: float) -> None:
        for center in self._two_tab_centers(span, tab_width):
            self.rectangularHole(
                origin_x + center,
                y,
                tab_width + self.slot_clearance,
                self.thickness + self.slot_clearance,
            )

    def _corner_slots(self, width: float, y: float) -> None:
        self._slots_for_span(0, self.bracket_size, y, self.bracket_tab_width)
        self._slots_for_span(width - self.bracket_size, self.bracket_size, y, self.bracket_tab_width)

    def _rail_tab_centers(self) -> tuple[float, float]:
        span = self.inner_x - 2 * self.door.rail_mount_margin
        first, second = self._two_tab_centers(span, self.rail_tab_width)
        return (
            self.door.rail_mount_margin + first,
            self.door.rail_mount_margin + second,
        )

    def _rail_slots(self, y: float) -> None:
        for center in self._rail_tab_centers():
            self.rectangularHole(
                center,
                y,
                self.rail_tab_width + self.slot_clearance,
                self.thickness + self.slot_clearance,
            )

    def _lower_front_back_callback(self) -> None:
        self._corner_slots(self.inner_x, self.lower_h - 0.5 * self.thickness)

    def _lower_side_callback(self) -> None:
        self._corner_slots(self.inner_y, self.lower_h - 0.5 * self.thickness)

    def _upper_back_callback(self) -> None:
        self._corner_slots(self.inner_x, 0.5 * self.thickness)

    def _upper_side_callback(self) -> None:
        self.hole(self.inner_y / 2.0, self.upper_h / 2.0, d=self.vent_diameter)
        self._corner_slots(self.inner_y, 0.5 * self.thickness)

    def _upper_front_callback(self) -> None:
        door = self.door
        self.rectangularHole(
            door.opening_x + 0.5 * door.opening_w,
            door.opening_y + 0.5 * door.opening_h,
            door.opening_w,
            door.opening_h,
            r=min(self.thickness, 0.25 * self.door_overlap),
        )
        self._rail_slots(door.top_lip_y)
        self._rail_slots(door.bottom_lip_y)
        self._corner_slots(self.inner_x, 0.5 * self.thickness)

        for x in (
            door.panel_left + door.magnet_inset,
            door.panel_left + door.panel_w - door.magnet_inset,
        ):
            for y in (
                door.panel_bottom + door.magnet_inset,
                door.panel_bottom + door.panel_h - door.magnet_inset,
            ):
                self.hole(x, y, d=self.magnet_hole)

    def _tabbed_strip(
        self,
        length: float,
        width: float,
        tab_width: float,
        tab_centers: tuple[float, float] | None = None,
        move=None,
        label="",
    ) -> None:
        total_h = width + self.thickness
        if self.move(length, total_h, move, True):
            return

        centers = tab_centers if tab_centers is not None else self._two_tab_centers(length, tab_width)

        self.ctx.move_to(0, 0)
        self.ctx.line_to(length, 0)
        self.ctx.line_to(length, width)

        for center in reversed(centers):
            right = center + 0.5 * tab_width
            left = center - 0.5 * tab_width
            self.ctx.line_to(right, width)
            self.ctx.line_to(right, total_h)
            self.ctx.line_to(left, total_h)
            self.ctx.line_to(left, width)

        self.ctx.line_to(0, width)
        self.ctx.line_to(0, 0)

        self.move(length, total_h, move, label=label)

    def _rail_lip(
        self,
        length: float,
        width: float,
        tab_width: float,
        tab_centers: tuple[float, float] | None = None,
        move=None,
        label="rail lip",
    ) -> None:
        total_h = width + self.thickness
        if self.move(length, total_h, move, True):
            return

        centers = tab_centers if tab_centers is not None else self._two_tab_centers(length, tab_width)
        t = self.thickness

        self.ctx.move_to(0, t)
        for center in centers:
            left = center - 0.5 * tab_width
            right = center + 0.5 * tab_width
            self.ctx.line_to(left, t)
            self.ctx.line_to(left, 0)
            self.ctx.line_to(right, 0)
            self.ctx.line_to(right, t)
        self.ctx.line_to(length, t)
        self.ctx.line_to(length, total_h)
        self.ctx.line_to(0, total_h)
        self.ctx.line_to(0, t)

        for center in centers:
            self.rectangularHole(
                center,
                total_h - 0.5 * t,
                tab_width + self.slot_clearance,
                t + self.slot_clearance,
            )

        self.move(length, total_h, move, label=label)

    def _corner_bracket(self, move=None, label="corner bracket") -> None:
        size = self.bracket_size
        total = size + self.thickness
        if self.move(total, total, move, True):
            return

        centers = self._two_tab_centers(size, self.bracket_tab_width)
        t = self.thickness

        self.ctx.move_to(t, t + size)
        self.ctx.arc(t, t, size, math.pi / 2.0, 0.0)

        for center in reversed(centers):
            right = t + center + 0.5 * self.bracket_tab_width
            left = t + center - 0.5 * self.bracket_tab_width
            self.ctx.line_to(right, t)
            self.ctx.line_to(right, 0)
            self.ctx.line_to(left, 0)
            self.ctx.line_to(left, t)

        self.ctx.line_to(t, t)

        for center in centers:
            lower = t + center - 0.5 * self.bracket_tab_width
            upper = t + center + 0.5 * self.bracket_tab_width
            self.ctx.line_to(t, lower)
            self.ctx.line_to(0, lower)
            self.ctx.line_to(0, upper)
            self.ctx.line_to(t, upper)

        self.ctx.line_to(t, t + size)

        self.hole(
            t + self.bracket_hole_offset,
            t + self.bracket_hole_offset,
            d=self.magnet_hole,
        )

        self.move(total, total, move, label=label)

    def _door_panel_callback(self) -> None:
        door = self.door
        for x in (
            door.magnet_inset,
            door.panel_w - door.magnet_inset,
        ):
            for y in (
                door.magnet_inset,
                door.panel_h - door.magnet_inset,
            ):
                self.hole(x, y, d=self.magnet_hole)

        for center in door.handle_tab_centers:
            self.rectangularHole(
                door.handle_slot_x,
                door.handle_mount_bottom + center,
                self.thickness + self.slot_clearance,
                door.handle_tab_size + self.slot_clearance,
            )

    def _door_handle(self, move=None, label="door handle") -> None:
        t = self.thickness
        total_w = max(self.handle_depth, 2.5 * t) + t
        total_h = self.handle_height
        if self.move(total_w, total_h, move, True):
            return

        body_w = total_w - t

        self.ctx.move_to(0, 0)
        self.ctx.line_to(body_w, 0)

        for center in self.door.handle_tab_centers:
            tab_bottom = center - 0.5 * self.door.handle_tab_size
            tab_top = center + 0.5 * self.door.handle_tab_size
            self.ctx.line_to(body_w, tab_bottom)
            self.ctx.line_to(total_w, tab_bottom)
            self.ctx.line_to(total_w, tab_top)
            self.ctx.line_to(body_w, tab_top)

        self.ctx.line_to(body_w, total_h)
        self.ctx.line_to(0, total_h)
        self.ctx.line_to(0, 0)

        self.move(total_w, total_h, move, label=label)

    def render(self):
        self._prepare_dimensions()

        # Bottom shell
        self.rectangularWall(
            self.inner_x,
            self.lower_h,
            "FFeF",
            callback=[self._lower_front_back_callback],
            move="right",
            label="bottom front",
        )
        self.rectangularWall(
            self.inner_y,
            self.lower_h,
            "Ffef",
            callback=[self._lower_side_callback],
            move="up",
            label="bottom left",
        )
        self.rectangularWall(
            self.inner_y,
            self.lower_h,
            "Ffef",
            callback=[self._lower_side_callback],
            label="bottom right",
        )
        self.rectangularWall(
            self.inner_x,
            self.lower_h,
            "FFeF",
            callback=[self._lower_front_back_callback],
            move="left up",
            label="bottom back",
        )
        self.rectangularWall(
            self.inner_x,
            self.inner_y,
            "ffff",
            move="right",
            label="floor",
        )

        # Top shell
        self.rectangularWall(
            self.inner_x,
            self.upper_h,
            "eFFF",
            callback=[self._upper_front_callback],
            move="right",
            label="top front",
        )
        self.rectangularWall(
            self.inner_y,
            self.upper_h,
            "efFf",
            callback=[self._upper_side_callback],
            move="up",
            label="top left",
        )
        self.rectangularWall(
            self.inner_y,
            self.upper_h,
            "efFf",
            callback=[self._upper_side_callback],
            label="top right",
        )
        self.rectangularWall(
            self.inner_x,
            self.upper_h,
            "eFFF",
            callback=[self._upper_back_callback],
            move="left up",
            label="top back",
        )
        self.rectangularWall(
            self.inner_x,
            self.inner_y,
            "ffff",
            move="right",
            label="roof",
        )

        # Sliding door and rail assemblies
        self.rectangularWall(
            self.door.panel_w,
            self.door.panel_h,
            "eeee",
            callback=[self._door_panel_callback],
            move="right",
            label="door",
        )
        self._door_handle(move="up", label="door handle")
        self.partsMatrix(
            2,
            2,
            "up",
            self._tabbed_strip,
            self.door.rail_length,
            self.rail_depth,
            self.rail_tab_width,
            self._rail_tab_centers(),
            label="rail backing",
        )
        self.partsMatrix(
            2,
            2,
            "up",
            self._rail_lip,
            self.door.rail_length,
            self.rail_width,
            self.rail_tab_width,
            self._rail_tab_centers(),
            label="rail lip",
        )

        # Four brackets for the top shell and four for the bottom shell
        self.partsMatrix(
            8,
            4,
            "up",
            self._corner_bracket,
            label="corner bracket",
        )
