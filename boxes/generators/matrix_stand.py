# Copyright (C) 2025-2026 Benjamin Menesini, based on the Console2 generator by Florian Festi
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

import logging
from dataclasses import dataclass

from boxes import *

logger = logging.getLogger(__name__)


@dataclass
class StandSectionProfile:
    """
    Derived geometry for one angled section of the stand.

    Args:
        depth: Section depth from front to back.
        back_wall_height: Total height at the back wall of the section.
        face_height: Height of the vertical face below the angled panel.
        panel_angle_deg: Panel angle in degrees (90 degrees is vertical).
        panel_length: Slanted length of the face panel.
        top_depth: Horizontal top depth behind the panel.
        has_top: Whether the top depth is large enough to render.
        panel_removable: Whether the face panel is removable.
        panel_mount: Panel mounting style ("springs" or "magnets").
    """

    depth: float
    back_wall_height: float
    face_height: float
    panel_angle_deg: float
    panel_length: float
    top_depth: float
    has_top: bool
    panel_removable: bool
    panel_mount: str


class MatrixStand(Boxes):
    """Stand for Matrix generator outputs with angled front and rear faces."""

    ui_group = "Misc"

    x: float
    outside: bool
    front_depth: float
    front_section_height: float
    front_face_height: float
    front_panel_angle: float
    front_panel_removable: bool
    front_panel_mount: str
    rear_depth: float
    rear_section_height: float
    rear_face_height: float
    rear_panel_angle: float
    rear_panel_removable: bool
    rear_panel_mount: str
    panel_magnet_diameter: float
    center_depth: float
    center_height: float

    description = """
Matrix stand with front and rear angled faces and a center bridge.

This generator builds a stand around the Matrix enclosure. Before you cut,
measure the Matrix you designed with the Matrix generator and your physical
panel. Set the stand width (x) and depths so the panel fits snugly with your
preferred clearance.

The stand is made from three depth segments:
- Front section with an angled face panel
- Center bridge between the sections
- Rear section with an angled face panel

The side panels and bottom are each drawn as single parts spanning all three segments.

#### Settings notes
- x: overall stand width; match the Matrix width plus any clearance.
- front_depth / rear_depth: depth of each angled section.
- front_section_height / rear_section_height: total height at each section's back wall.
- front_face_height / rear_face_height: vertical height below each face panel.
- front_panel_angle / rear_panel_angle: tilt angle in degrees (90 degrees is vertical).
- center_depth / center_height: size of the center bridge; center_height must be <= both section heights.
- *_panel_removable and *_panel_mount: choose removable face panels with spring tabs or magnets.
- panel_magnet_diameter: magnet diameter when using magnets.

#### Build guide
1. Cut all parts.
2. Glue the left and right side panels to the bottom panel.
3. Add the center bridge top (if any) between the side panels.
4. Assemble the front section: front wall, face panel, top, and back wall.
5. Assemble the rear section: front wall, face panel, top, and back wall.
6. Install the panel hardware (springs or magnets) if you chose removable panels.
7. Dry-fit your Matrix and adjust before final glue-up.

#### Customization tips
- Consider adding wiring or button holes to the rear walls and to the front/rear face panels using a vector editor.
- If you need extra cable space, increase center_depth or reduce the panel angles.
"""

    def __init__(self) -> None:
        """Configure generator settings and CLI arguments.

        Args:
            None.
        Returns:
            None.
        """
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=0.5)

        self.buildArgParser(x=100, outside=False)

        # Front section (faces forward)
        self.argparser.add_argument(
            "--front_depth",
            action="store",
            type=float,
            default=100,
            help="Depth of the front section (in mm)",
        )
        self.argparser.add_argument(
            "--front_section_height",
            action="store",
            type=float,
            default=100,
            help="Height at the back wall of the front section (in mm)",
        )
        self.argparser.add_argument(
            "--front_face_height",
            action="store",
            type=float,
            default=30,
            help="Height of the vertical face below the front panel (in mm)",
        )
        self.argparser.add_argument(
            "--front_panel_angle",
            action="store",
            type=float,
            default=50,
            help="Angle of the front face panel (90 degrees is vertical)",
        )
        self.argparser.add_argument(
            "--front_panel_removable",
            action="store",
            type=boolarg,
            default=True,
            help="Make the front face panel removable",
        )
        self.argparser.add_argument(
            "--front_panel_mount",
            action="store",
            type=str,
            default="springs",
            choices=["springs", "magnets"],
            help="Front face panel mount type (springs or magnets)",
        )

        # Rear section (faces backward)
        self.argparser.add_argument(
            "--rear_depth",
            action="store",
            type=float,
            default=100,
            help="Depth of the rear section (in mm)",
        )
        self.argparser.add_argument(
            "--rear_section_height",
            action="store",
            type=float,
            default=100,
            help="Height at the back wall of the rear section (in mm)",
        )
        self.argparser.add_argument(
            "--rear_face_height",
            action="store",
            type=float,
            default=30,
            help="Height of the vertical face below the rear panel (in mm)",
        )
        self.argparser.add_argument(
            "--rear_panel_angle",
            action="store",
            type=float,
            default=50,
            help="Angle of the rear face panel (90 degrees is vertical)",
        )
        self.argparser.add_argument(
            "--rear_panel_removable",
            action="store",
            type=boolarg,
            default=True,
            help="Make the rear face panel removable",
        )
        self.argparser.add_argument(
            "--rear_panel_mount",
            action="store",
            type=str,
            default="springs",
            choices=["springs", "magnets"],
            help="Rear face panel mount type (springs or magnets)",
        )

        self.argparser.add_argument(
            "--panel_magnet_diameter",
            action="store",
            type=float,
            default=5.0,
            help="Diameter of panel magnets when using magnets (in mm)",
        )
        self.panel_magnet_diameter: float = 5.0

        # Center bridge
        self.argparser.add_argument(
            "--center_depth",
            action="store",
            type=float,
            default=60,
            help="Depth of the center bridge section (in mm)",
        )
        self.argparser.add_argument(
            "--center_height",
            action="store",
            type=float,
            default=60,
            help="Height of the center bridge section (in mm)",
        )

    def _build_section_profile(
        self,
        *,
        depth: float,
        back_wall_height: float,
        face_height: float,
        panel_angle_deg: float,
        panel_removable: bool,
        panel_mount: str,
    ) -> StandSectionProfile:
        """Compute derived geometry for a stand section.

        Args:
            depth: Section depth from front to back.
            back_wall_height: Total height at the back wall of the section.
            face_height: Height of the vertical face below the angled panel.
            panel_angle_deg: Panel angle in degrees (90 degrees is vertical).
            panel_removable: Whether the face panel is removable.
            panel_mount: Panel mounting style ("springs" or "magnets").
        Returns:
            StandSectionProfile: Resolved geometry for the section.
        Raises:
            ValueError: If the back wall height is not larger than the face height.
        """
        if back_wall_height <= face_height:
            raise ValueError("Section back wall height must be larger than face height.")

        panel_angle_rad = math.radians(panel_angle_deg)

        # Panel length is constrained by the available rise and the available depth.
        panel_length_by_height = (back_wall_height - face_height) / math.sin(panel_angle_rad)
        panel_length_by_depth = depth / math.cos(panel_angle_rad)
        panel_length = min(panel_length_by_height, panel_length_by_depth)

        top_depth = depth - panel_length * math.cos(panel_angle_rad)
        back_wall_height = face_height + panel_length * math.sin(panel_angle_rad)

        has_top = top_depth > 0.1 * self.thickness
        if not has_top:
            top_depth = 0.0

        return StandSectionProfile(
            depth=depth,
            back_wall_height=back_wall_height,
            face_height=face_height,
            panel_angle_deg=panel_angle_deg,
            panel_length=panel_length,
            top_depth=top_depth,
            has_top=has_top,
            panel_removable=panel_removable,
            panel_mount=panel_mount,
        )

    def _draw_panel_edge_with_hardware(
        self,
        edge_length: float,
        panel_removable: bool,
        panel_mount: str,
    ) -> None:
        """Draw a panel edge, adding retention hardware cutouts if needed.

        Args:
            edge_length: Length of the panel edge in mm.
            panel_removable: Whether the panel uses removable hardware.
            panel_mount: Panel mounting style ("springs" or "magnets").
        Returns:
            None.
        """
        thickness = self.thickness
        if panel_removable:
            if panel_mount == "magnets":
                self.hole(3 * thickness, 1.5 * thickness, d=self.panel_magnet_diameter)
            else:
                self.rectangularHole(3 * thickness, 1.5 * thickness, 2.5 * thickness, 1.05 * thickness)
            self.edge(edge_length)
        else:
            self.edges["f"](edge_length)
        if panel_removable:
            if panel_mount == "magnets":
                self.hole(-3 * thickness, 1.5 * thickness, d=self.panel_magnet_diameter)
            else:
                self.rectangularHole(-3 * thickness, 1.5 * thickness, 2.5 * thickness, 1.05 * thickness)

    def _draw_top_edge_segment(self, profile: StandSectionProfile) -> None:
        """Draw the top edge segment for a section if present.

        Args:
            profile: Section geometry profile.
        Returns:
            None.
        """
        if profile.top_depth <= 0:
            return
        self.edges["f"](profile.top_depth)

    def _add_side_finger_holes(
        self,
        *,
        front_section: StandSectionProfile,
        rear_section: StandSectionProfile,
        center_depth: float,
        center_height: float,
        bottom_edge: edges.BaseEdge,
    ) -> None:
        """Add finger holes to a side panel for section walls and the center bridge.

        Args:
            front_section: Geometry for the front section.
            rear_section: Geometry for the rear section.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
            bottom_edge: Edge profile for the bottom.
        Returns:
            None.
        """
        base_offset = bottom_edge.startwidth()
        thickness = self.thickness

        rear_wall_pos = rear_section.depth - 0.5 * thickness
        front_wall_pos = rear_section.depth + center_depth + 0.5 * thickness

        self.fingerHolesAt(rear_wall_pos, base_offset, rear_section.back_wall_height, 90)

        if center_depth > 0:
            self.fingerHolesAt(front_wall_pos, base_offset, front_section.back_wall_height, 90)

        if center_depth > 0 and center_height > 0:
            clearance, span_length = self._finger_joint_span(center_depth)
            if span_length > 0:
                # Finger holes for the center bridge top in the side panel.
                self.fingerHolesAt(
                    rear_section.depth + clearance,
                    base_offset + center_height,
                    span_length,
                    0,
                )

    def _trace_side_outline(
        self,
        *,
        front_section: StandSectionProfile,
        rear_section: StandSectionProfile,
        center_depth: float,
        bottom_edge: edges.BaseEdge,
    ) -> None:
        """Trace the perimeter of a combined side panel.

        Args:
            front_section: Geometry for the front section.
            rear_section: Geometry for the rear section.
            center_depth: Depth of the center bridge section.
            bottom_edge: Edge profile for the bottom.
        Returns:
            None.
        """
        total_depth = rear_section.depth + center_depth + front_section.depth

        # Bottom edge across the full stand depth.
        bottom_edge(total_depth)
        self.corner(90)

        # Front vertical wall (outer face).
        front_vertical_height = front_section.face_height + bottom_edge.endwidth()
        self.edges["f"](front_vertical_height)
        self.corner(90 - front_section.panel_angle_deg)

        # Front angled panel.
        self._draw_panel_edge_with_hardware(
            front_section.panel_length,
            front_section.panel_removable,
            front_section.panel_mount,
        )

        # Connect the two section heights across the center bridge depth.
        height_delta = rear_section.back_wall_height - front_section.back_wall_height
        center_slope_angle_deg = math.degrees(math.atan2(height_delta, center_depth)) if center_depth else 0.0
        center_slope_length = math.hypot(center_depth, height_delta) if center_depth else 0.0

        if front_section.has_top:
            self.corner(front_section.panel_angle_deg)
            self._draw_top_edge_segment(front_section)
            if center_slope_length:
                self.corner(-center_slope_angle_deg)
        else:
            if center_slope_length:
                self.corner(front_section.panel_angle_deg - center_slope_angle_deg)
            else:
                self.corner(front_section.panel_angle_deg)

        if center_slope_length:
            self.edge(center_slope_length)
            self.corner(center_slope_angle_deg)

        # Rear top edge (reverse direction).
        if rear_section.has_top:
            self._draw_top_edge_segment(rear_section)

        # Rear angled panel.
        self.corner(rear_section.panel_angle_deg)
        self._draw_panel_edge_with_hardware(
            rear_section.panel_length,
            rear_section.panel_removable,
            rear_section.panel_mount,
        )
        self.corner(90 - rear_section.panel_angle_deg)

        # Rear vertical wall (outer face).
        rear_vertical_height = rear_section.face_height + bottom_edge.startwidth()
        self.edges["f"](rear_vertical_height)
        self.corner(90)

    def _draw_combined_side_panel(
        self,
        *,
        front_section: StandSectionProfile,
        rear_section: StandSectionProfile,
        center_depth: float,
        center_height: float,
        bottom_edge: edges.BaseEdge,
        move=None,
        label: str = "",
    ) -> None:
        """Draw a combined side panel spanning front, center, and rear sections.

        Args:
            front_section: Geometry for the front section.
            rear_section: Geometry for the rear section.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
            bottom_edge: Edge profile for the bottom.
            move: Layout movement hint.
            label: Part label for the output.
        Returns:
            None.
        """
        total_depth = rear_section.depth + center_depth + front_section.depth

        max_height = max(front_section.back_wall_height, rear_section.back_wall_height)
        required_width = total_depth + 2 * self.edges["f"].spacing()
        required_height = max_height + bottom_edge.spacing() + self.edges["f"].spacing()
        if self.move(required_width, required_height, move, True):
            return

        self.moveTo(self.thickness, 0)
        with self.saved_context():
            self._trace_side_outline(
                front_section=front_section,
                rear_section=rear_section,
                center_depth=center_depth,
                bottom_edge=bottom_edge,
            )

        self._add_side_finger_holes(
            front_section=front_section,
            rear_section=rear_section,
            center_depth=center_depth,
            center_height=center_height,
            bottom_edge=bottom_edge,
        )

        self.move(required_width, required_height, move, label=label)

    def _add_bottom_finger_holes(
        self,
        *,
        rear_section: StandSectionProfile,
        center_depth: float,
        stand_width: float,
    ) -> None:
        """Add finger holes to the bottom panel for section walls.

        Args:
            rear_section: Geometry for the rear section.
            center_depth: Depth of the center bridge section.
            stand_width: Overall stand width in mm.
        Returns:
            None.
        """
        thickness = self.thickness
        rear_wall_pos = rear_section.depth - 0.5 * thickness
        clearance, span_length = self._finger_joint_span(stand_width)
        if span_length > 0:
            self.fingerHolesAt(rear_wall_pos, clearance, span_length, 90)
        else:
            self.fingerHolesAt(rear_wall_pos, 0, stand_width, 90)
        if center_depth > 0:
            front_wall_pos = rear_section.depth + center_depth + 0.5 * thickness
            if span_length > 0:
                self.fingerHolesAt(front_wall_pos, clearance, span_length, 90)
            else:
                self.fingerHolesAt(front_wall_pos, 0, stand_width, 90)

    def _render_panel_side_clip(self, panel_length: float, move=None, *, panel_mount: str = "springs") -> None:
        """Render the side clip pieces for removable panels.

        Args:
            panel_length: Length of the panel edge in mm.
            move: Layout movement hint.
            panel_mount: Panel mounting style ("springs" or "magnets").
        Returns:
            None.
        """
        thickness = self.thickness

        total_width = panel_length
        total_height = 4 * thickness

        if self.move(total_width, total_height, move, True):
            return

        if panel_mount == "magnets":
            self.hole(3 * thickness, 1.5 * thickness, d=self.panel_magnet_diameter)
            self.hole(panel_length - 3 * thickness, 1.5 * thickness, d=self.panel_magnet_diameter)
        else:
            self.rectangularHole(3 * thickness, 1.5 * thickness, 3 * thickness, 1.05 * thickness)
            self.rectangularHole(panel_length - 3 * thickness, 1.5 * thickness, 3 * thickness, 1.05 * thickness)
            self.rectangularHole(panel_length / 2, 1.5 * thickness, 2 * thickness, thickness)

        self.polyline(panel_length, 90, 3 * thickness, 90)
        self.edges["f"](panel_length)
        self.polyline(0, 90, 3 * thickness, 90)
        self.move(total_width, total_height, move)

    def _render_panel_spring_latch(self, panel_length: float, move=None) -> None:
        """Render a spring latch used by removable panels.

        Args:
            panel_length: Length of the panel edge in mm.
            move: Layout movement hint.
        Returns:
            None.
        """
        thickness = self.thickness

        latch_length = panel_length - 4 * thickness
        total_width = latch_length
        total_height = 2.5 * thickness

        if self.move(total_width, total_height, move, True):
            return

        # One half of the latch profile; mirrored for symmetry.
        end_segment = [
            latch_length / 2 - 3 * thickness,
            -90,
            1.5 * thickness,
            (90, 0.5 * thickness),
            thickness,
            (90, 0.5 * thickness),
            thickness,
            90,
            0.5 * thickness,
            -90,
            0.5 * thickness,
            -90,
            0,
            (90, 0.5 * thickness),
            0,
            90,
        ]

        self.moveTo(latch_length / 2 - thickness, 2 * thickness, -90)
        self.polyline(*([thickness, 90, 2 * thickness, 90, thickness, -90] + end_segment + [latch_length] + list(reversed(end_segment))))
        self.move(total_width, total_height, move)

    def _finger_joint_span(self, length: float) -> tuple[float, float]:
        """Compute clearance and span for finger joints along an edge.

        Args:
            length: Total edge length.
        Returns:
            tuple[float, float]: Clearance on each side and the middle span length.
        """
        finger_length = self.edges["f"].settings.finger * self.thickness
        clearance = min(finger_length, length / 8.0)
        span_length = length - 2 * clearance
        if span_length <= 0:
            return 0.0, 0.0
        return clearance, span_length

    def _back_wall_bottom_edge(self, stand_width: float) -> edges.BaseEdge | str:
        """Return a bottom edge profile for a section back wall.

        Args:
            stand_width: Overall stand width in mm.
        Returns:
            edges.BaseEdge | str: Edge profile for the back wall bottom.
        """
        clearance, span_length = self._finger_joint_span(stand_width)
        if span_length > 0:
            return edges.CompoundEdge(self, ("e", "f", "e"), (clearance, span_length, clearance))
        return "f"

    def _flush_back_top_edge(self) -> edges.BaseEdge:
        """Return a finger joint edge with zero start width for flush tops.

        Args:
            None.
        Returns:
            edges.BaseEdge: Edge instance with zero start width.
        """
        edge = getattr(self, "_flush_back_top_edge_cache", None)
        if edge is not None:
            return edge

        class FlushFingerJointEdge(edges.FingerJointEdgeCounterPart):
            def startwidth(self) -> float:
                return 0.0

        edge = FlushFingerJointEdge(self, self.edges["F"].settings)
        self._flush_back_top_edge_cache = edge
        return edge

    def _panel_hardware_stack_height(self, panel_mount: str) -> float:
        """Compute the layout height needed for panel hardware parts.

        Args:
            panel_mount: Panel mounting style ("springs" or "magnets").
        Returns:
            float: Minimum height needed to stack panel hardware parts.
        """
        thickness = self.thickness
        side_clip_height = 4 * thickness
        total_height = 2 * (side_clip_height + self.spacing)
        if panel_mount == "springs":
            latch_height = 2.5 * thickness
            total_height += 2 * (latch_height + self.spacing)
        return total_height

    def _rect_wall_overall_size(self, width: float, height: float, edges_spec) -> tuple[float, float]:
        """Calculate the overall size of a rectangular wall including edge spacing.

        Args:
            width: Interior width of the wall in mm.
            height: Interior height of the wall in mm.
            edges_spec: Edge specification for the wall.
        Returns:
            tuple[float, float]: Overall width and height including spacing.
        """
        if isinstance(edges_spec, str):
            edges_spec = list(edges_spec)
        edges_list = [self.edges.get(edge, edge) for edge in edges_spec]
        overall_width = width + edges_list[-1].spacing() + edges_list[1].spacing()
        overall_height = height + edges_list[0].spacing() + edges_list[2].spacing()
        return overall_width, overall_height

    def _top_depth_for_profile(
        self,
        profile: StandSectionProfile,
        top_front_edge: edges.BaseEdge | str,
        top_back_edge: edges.BaseEdge | str,
    ) -> float:
        """Compute the usable top depth after accounting for edge start widths.

        Args:
            profile: Section geometry profile.
            top_front_edge: Edge profile for the front of the top.
            top_back_edge: Edge profile for the back of the top.
        Returns:
            float: Usable top depth in mm.
        """
        front_edge = self.edges.get(top_front_edge, top_front_edge)
        back_edge = self.edges.get(top_back_edge, top_back_edge)
        depth = profile.top_depth - front_edge.startwidth() - back_edge.startwidth()
        return max(0.0, depth)

    def _panel_opening_width(self, stand_width: float, panel_edges) -> float:
        """Compute the usable panel width between edge profiles.

        Args:
            stand_width: Overall stand width in mm.
            panel_edges: Edge specification for the panel.
        Returns:
            float: Usable panel width in mm.
        Raises:
            ValueError: If the panel width is too small for the edge profiles.
        """
        if isinstance(panel_edges, str):
            panel_edges = list(panel_edges)
        edges_list = [self.edges.get(edge, edge) for edge in panel_edges]
        panel_width = stand_width - edges_list[0].startwidth() - edges_list[2].startwidth()
        if panel_width <= 0:
            raise ValueError("Panel width is too small for the selected edge profile.")
        return panel_width

    def _section_row_height(
        self,
        profile: StandSectionProfile,
        stand_width: float,
        bottom_edge: edges.BaseEdge,
        *,
        top_depth_override: float | None = None,
        top_front_edge_override: edges.BaseEdge | str | None = None,
        top_back_edge_override: edges.BaseEdge | str | None = None,
    ) -> float:
        """Compute the layout row height for all parts of one section.

        Args:
            profile: Section geometry profile.
            stand_width: Overall stand width in mm.
            bottom_edge: Edge profile for the bottom.
            top_depth_override: Optional override for the top depth.
            top_front_edge_override: Optional override for the top front edge profile.
            top_back_edge_override: Optional override for the top back edge profile.
        Returns:
            float: Row height needed for this section.
        """
        height_candidates: list[float] = []

        height_candidates.append(
            self._rect_wall_overall_size(
                profile.face_height,
                stand_width,
                ("F", "e", "F", bottom_edge),
            )[1]
        )

        panel_edges = "hehe" if profile.panel_removable else "FeFe"
        panel_width = self._panel_opening_width(stand_width, panel_edges)
        height_candidates.append(self._rect_wall_overall_size(profile.panel_length, panel_width, panel_edges)[1])

        if profile.has_top:
            top_front_edge = top_front_edge_override or "E"
            top_back_edge = top_back_edge_override or "F"
            top_depth = (
                top_depth_override
                if top_depth_override is not None
                else self._top_depth_for_profile(profile, top_front_edge, top_back_edge)
            )
            if top_depth > 0:
                height_candidates.append(
                    self._rect_wall_overall_size(
                        top_depth,
                        stand_width,
                        ("F", top_front_edge, "F", top_back_edge),
                    )[1]
                )

        back_bottom_edge = self._back_wall_bottom_edge(stand_width)
        height_candidates.append(
            self._rect_wall_overall_size(
                profile.back_wall_height,
                stand_width,
                ("f", back_bottom_edge, "f", "f"),
            )[1]
        )

        row_height = max(height_candidates) + self.spacing
        if profile.panel_removable:
            row_height = max(row_height, self._panel_hardware_stack_height(profile.panel_mount))
        return row_height

    def _render_section_parts(
        self,
        profile: StandSectionProfile,
        stand_width: float,
        bottom_edge: edges.BaseEdge,
        *,
        center_depth: float,
        center_height: float,
        label_prefix: str,
        top_depth_override: float | None = None,
        top_front_edge_override: edges.BaseEdge | str | None = None,
        top_back_edge_override: edges.BaseEdge | str | None = None,
    ) -> None:
        """Render all parts for one angled section.

        Args:
            profile: Section geometry profile.
            stand_width: Overall stand width in mm.
            bottom_edge: Edge profile for the bottom.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
            label_prefix: Prefix used for part labels.
            top_depth_override: Optional override for the top depth.
            top_front_edge_override: Optional override for the top front edge profile.
            top_back_edge_override: Optional override for the top back edge profile.
        Returns:
            None.
        """
        back_top_edge = "f"

        # Front wall (below the panel).
        self.rectangularWall(
            profile.face_height,
            stand_width,
            ("F", "e", "F", bottom_edge),
            ignore_widths=[7, 4],
            move="right",
            label=f"{label_prefix} Front Wall",
        )

        # Face panel.
        panel_edges = "hehe" if profile.panel_removable else "FeFe"
        panel_width = self._panel_opening_width(stand_width, panel_edges)
        self.rectangularWall(
            profile.panel_length,
            panel_width,
            panel_edges,
            move="right",
            label=f"{label_prefix} Face Panel",
        )

        # Top.
        if profile.has_top:
            top_front_edge = top_front_edge_override or "E"
            top_back_edge = top_back_edge_override or "F"
            top_depth = (
                top_depth_override
                if top_depth_override is not None
                else self._top_depth_for_profile(profile, top_front_edge, top_back_edge)
            )
            if top_depth > 0:
                self.rectangularWall(
                    top_depth,
                    stand_width,
                    ("F", top_front_edge, "F", top_back_edge),
                    move="right",
                    label=f"{label_prefix} Top",
                )

        # Back wall.
        back_bottom_edge = self._back_wall_bottom_edge(stand_width)
        back_wall_callback = None
        if center_depth > 0 and center_height > 0:
            center_top_y = profile.back_wall_height - center_height
            # Finger holes for the center bridge top in the back wall.
            back_wall_callback = [lambda: self.fingerHolesAt(center_top_y, 0, stand_width, 90), None, None, None]
        self.rectangularWall(
            profile.back_wall_height,
            stand_width,
            ("f", back_bottom_edge, "f", back_top_edge),
            ignore_widths=[0, 3],
            callback=back_wall_callback,
            move="right",
            label=f"{label_prefix} Back Wall",
        )

        # Hardware for removable panels.
        if profile.panel_removable:
            if profile.panel_mount == "springs":
                self._render_panel_spring_latch(profile.panel_length, "up")
                self._render_panel_spring_latch(profile.panel_length, "up")
            self._render_panel_side_clip(profile.panel_length, "up", panel_mount=profile.panel_mount)
            self._render_panel_side_clip(profile.panel_length, "up", panel_mount=profile.panel_mount)

    def _side_row_height(
        self,
        front_section: StandSectionProfile,
        rear_section: StandSectionProfile,
        bottom_edge: edges.BaseEdge,
    ) -> float:
        """Compute the row height for the side panels.

        Args:
            front_section: Geometry for the front section.
            rear_section: Geometry for the rear section.
            bottom_edge: Edge profile for the bottom.
        Returns:
            float: Row height in mm.
        """
        max_height = max(front_section.back_wall_height, rear_section.back_wall_height)
        side_height = max_height + bottom_edge.spacing() + self.edges["f"].spacing()
        return side_height + self.spacing

    def _base_row_layout(
        self,
        *,
        total_depth: float,
        stand_width: float,
        center_depth: float,
        center_height: float,
    ) -> tuple[float, edges.BaseEdge | str | None]:
        """Compute the row height and edge profile for the base row.

        Args:
            total_depth: Total stand depth in mm.
            stand_width: Overall stand width in mm.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
        Returns:
            tuple[float, edges.BaseEdge | str | None]: Row height and center bridge edge profile.
        """
        bottom_height = self._rect_wall_overall_size(total_depth, stand_width, "ffff")[1] + self.spacing
        row_height = bottom_height
        center_bridge_edge: edges.BaseEdge | str | None = None

        if center_depth > 0 and center_height > 0:
            clearance, span_length = self._finger_joint_span(center_depth)
            if span_length > 0:
                # Keep finger joints in the middle span to avoid tight corners.
                center_bridge_edge = edges.CompoundEdge(self, ("e", "f", "e"), (clearance, span_length, clearance))
            else:
                center_bridge_edge = "e"
            bridge_height = (
                self._rect_wall_overall_size(center_depth, stand_width, (center_bridge_edge, "f", center_bridge_edge, "f"))[1]
                + self.spacing
            )
            row_height = max(row_height, bridge_height)

        return row_height, center_bridge_edge

    def _render_side_row(
        self,
        *,
        row_y: float,
        row_height: float,
        front_section: StandSectionProfile,
        rear_section: StandSectionProfile,
        center_depth: float,
        center_height: float,
        bottom_edge: edges.BaseEdge,
    ) -> float:
        """Render the row containing the left and right side panels.

        Args:
            row_y: Current vertical offset for the row.
            row_height: Height of the row to advance after rendering.
            front_section: Geometry for the front section.
            rear_section: Geometry for the rear section.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
            bottom_edge: Edge profile for the bottom.
        Returns:
            float: New vertical offset after rendering.
        """
        with self.saved_context():
            self.moveTo(0, row_y)
            self._draw_combined_side_panel(
                front_section=front_section,
                rear_section=rear_section,
                center_depth=center_depth,
                center_height=center_height,
                bottom_edge=bottom_edge,
                move="right",
                label="Left Side Panel",
            )
            self._draw_combined_side_panel(
                front_section=front_section,
                rear_section=rear_section,
                center_depth=center_depth,
                center_height=center_height,
                bottom_edge=bottom_edge,
                move="right",
                label="Right Side Panel",
            )
        return row_y + row_height

    def _render_base_row(
        self,
        *,
        row_y: float,
        row_height: float,
        total_depth: float,
        stand_width: float,
        center_depth: float,
        rear_section: StandSectionProfile,
        center_bridge_edge: edges.BaseEdge | str | None,
    ) -> float:
        """Render the row containing the bottom and center bridge top.

        Args:
            row_y: Current vertical offset for the row.
            row_height: Height of the row to advance after rendering.
            total_depth: Total stand depth in mm.
            stand_width: Overall stand width in mm.
            center_depth: Depth of the center bridge section.
            rear_section: Geometry for the rear section.
            center_bridge_edge: Edge profile for the center bridge top.
        Returns:
            float: New vertical offset after rendering.
        """
        with self.saved_context():
            self.moveTo(0, row_y)
            self.rectangularWall(
                total_depth,
                stand_width,
                "ffff",
                callback=[
                    lambda: self._add_bottom_finger_holes(
                        rear_section=rear_section,
                        center_depth=center_depth,
                        stand_width=stand_width,
                    ),
                    None,
                    None,
                    None,
                ],
                move="right",
                label="Bottom",
            )
            if center_bridge_edge is not None:
                self.rectangularWall(
                    center_depth,
                    stand_width,
                    (center_bridge_edge, "f", center_bridge_edge, "f"),
                    move="right",
                    label="Center Bridge Top",
                )
        return row_y + row_height

    def _render_section_row(
        self,
        *,
        row_y: float,
        row_height: float,
        profile: StandSectionProfile,
        stand_width: float,
        bottom_edge: edges.BaseEdge,
        center_depth: float,
        center_height: float,
        label_prefix: str,
        top_depth_override: float | None = None,
        top_front_edge_override: edges.BaseEdge | str | None = None,
        top_back_edge_override: edges.BaseEdge | str | None = None,
    ) -> float:
        """Render the row containing all parts of one section.

        Args:
            row_y: Current vertical offset for the row.
            row_height: Height of the row to advance after rendering.
            profile: Section geometry profile.
            stand_width: Overall stand width in mm.
            bottom_edge: Edge profile for the bottom.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
            label_prefix: Prefix used for part labels.
            top_depth_override: Optional override for the top depth.
            top_front_edge_override: Optional override for the top front edge profile.
            top_back_edge_override: Optional override for the top back edge profile.
        Returns:
            float: New vertical offset after rendering.
        """
        with self.saved_context():
            self.moveTo(0, row_y)
            self._render_section_parts(
                profile,
                stand_width,
                bottom_edge,
                center_depth=center_depth,
                center_height=center_height,
                label_prefix=label_prefix,
                top_depth_override=top_depth_override,
                top_front_edge_override=top_front_edge_override,
                top_back_edge_override=top_back_edge_override,
            )
        return row_y + row_height

    def render(self) -> None:
        """Render the Matrix stand parts in ordered layout rows.

        Args:
            None.
        Returns:
            None.
        """
        stand_width = self.x
        front_depth = self.front_depth
        rear_depth = self.rear_depth
        center_depth = self.center_depth
        front_section_height = self.front_section_height
        rear_section_height = self.rear_section_height
        center_height = self.center_height

        bottom_edge = self.edges["F"]

        if self.outside:
            stand_width = self.adjustSize(stand_width)
            front_depth = self.adjustSize(front_depth)
            rear_depth = self.adjustSize(rear_depth)
            center_depth = self.adjustSize(center_depth)
            front_section_height = self.adjustSize(front_section_height, bottom_edge)
            rear_section_height = self.adjustSize(rear_section_height, bottom_edge)
            center_height = self.adjustSize(center_height, bottom_edge)

        front_section = self._build_section_profile(
            depth=front_depth,
            back_wall_height=front_section_height,
            face_height=self.front_face_height,
            panel_angle_deg=self.front_panel_angle,
            panel_removable=self.front_panel_removable,
            panel_mount=self.front_panel_mount,
        )
        rear_section = self._build_section_profile(
            depth=rear_depth,
            back_wall_height=rear_section_height,
            face_height=self.rear_face_height,
            panel_angle_deg=self.rear_panel_angle,
            panel_removable=self.rear_panel_removable,
            panel_mount=self.rear_panel_mount,
        )

        if center_height > min(front_section.back_wall_height, rear_section.back_wall_height):
            raise ValueError(
                "center_height must be <= both section heights so the side panels cover the center bridge."
            )

        total_depth = rear_section.depth + center_depth + front_section.depth

        logger.debug(
            "MatrixStand dimensions: width=%s front_depth=%s center_depth=%s rear_depth=%s",
            stand_width,
            front_section.depth,
            center_depth,
            rear_section.depth,
        )
        logger.debug("Front section profile: %s", front_section)
        logger.debug("Rear section profile: %s", rear_section)

        side_row_height = self._side_row_height(front_section, rear_section, bottom_edge)
        base_row_height, center_bridge_edge = self._base_row_layout(
            total_depth=total_depth,
            stand_width=stand_width,
            center_depth=center_depth,
            center_height=center_height,
        )
        front_row_height = self._section_row_height(front_section, stand_width, bottom_edge)
        rear_row_height = self._section_row_height(
            rear_section,
            stand_width,
            bottom_edge,
            top_depth_override=rear_section.top_depth,
            top_front_edge_override=self._flush_back_top_edge(),
            top_back_edge_override="e",
        )

        logger.debug(
            "Row heights: sides=%s base=%s front=%s rear=%s",
            side_row_height,
            base_row_height,
            front_row_height,
            rear_row_height,
        )

        row_y = 0.0
        row_y = self._render_side_row(
            row_y=row_y,
            row_height=side_row_height,
            front_section=front_section,
            rear_section=rear_section,
            center_depth=center_depth,
            center_height=center_height,
            bottom_edge=bottom_edge,
        )
        row_y = self._render_base_row(
            row_y=row_y,
            row_height=base_row_height,
            total_depth=total_depth,
            stand_width=stand_width,
            center_depth=center_depth,
            rear_section=rear_section,
            center_bridge_edge=center_bridge_edge,
        )
        row_y = self._render_section_row(
            row_y=row_y,
            row_height=front_row_height,
            profile=front_section,
            stand_width=stand_width,
            bottom_edge=bottom_edge,
            center_depth=center_depth,
            center_height=center_height,
            label_prefix="Front Section",
        )
        row_y = self._render_section_row(
            row_y=row_y,
            row_height=rear_row_height,
            profile=rear_section,
            stand_width=stand_width,
            bottom_edge=bottom_edge,
            center_depth=center_depth,
            center_height=center_height,
            label_prefix="Rear Section",
            top_depth_override=rear_section.top_depth,
            top_front_edge_override=self._flush_back_top_edge(),
            top_back_edge_override="e",
        )
