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
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from boxes import Boxes, edges

logger = logging.getLogger(__name__)

EdgeSpec = str | Sequence[edges.BaseEdge | str]


@dataclass(frozen=True)
class SectionInputs:
    """
    Raw input dimensions for a stand section.

    Args:
        depth: Section depth from front to back.
        back_wall_height: Total height at the back wall of the section.
        face_height: Height of the vertical face below the angled panel.
        face_panel_angle_deg: Panel angle in degrees (90 degrees is vertical).
        face_panel_mount: Panel mounting style ("springs" or "magnets").
    """

    depth: float
    back_wall_height: float
    face_height: float
    face_panel_angle_deg: float
    face_panel_mount: str


@dataclass(frozen=True)
class StandInputs:
    """
    Raw input dimensions for the overall stand.

    Args:
        stand_width: Overall stand width in mm.
        center_depth: Depth of the center bridge section.
        center_height: Height of the center bridge section.
        front: Input dimensions for the front section.
        rear: Input dimensions for the rear section.
    """

    stand_width: float
    center_depth: float
    center_height: float
    front: SectionInputs
    rear: SectionInputs


@dataclass
class StandSectionProfile:
    """
    Derived geometry for one angled section of the stand.

    Args:
        depth: Section depth from front to back.
        back_wall_height: Total height at the back wall of the section.
        face_height: Height of the vertical face below the angled panel.
        face_panel_angle_deg: Panel angle in degrees (90 degrees is vertical).
        face_panel_length: Slanted length of the face panel.
        top_depth: Horizontal top depth behind the panel.
        has_top: Whether the top depth is large enough to render.
        face_panel_mount: Panel mounting style ("springs" or "magnets").
    """

    depth: float
    back_wall_height: float
    face_height: float
    face_panel_angle_deg: float
    face_panel_length: float
    top_depth: float
    has_top: bool
    face_panel_mount: str


@dataclass(frozen=True)
class RowPlan:
    """
    Layout row plan for rendering.

    Args:
        name: Human-readable label for the row.
        height: Row height in mm, including spacing.
        render: Callable that draws the row at a given y offset.
    """

    name: str
    height: float
    render: Callable[[float], None]


class RectangularFingerJointSettings(edges.FingerJointSettings):
    """
    Settings for Finger Joints (rectangular only).

    Values:

    * absolute
      * style : "rectangular" : style of the fingers (fixed)
      * surroundingspaces : 2.0 : space at the start and end in multiple of normal spaces

    * relative (in multiples of thickness)

      * space : 2.0 : space between fingers (multiples of thickness)
      * finger : 2.0 : width of the fingers (multiples of thickness)
      * width : 1.0 : width of finger holes (multiples of thickness)
      * edge_width : 1.0 : space below holes of FingerHoleEdge (multiples of thickness)
      * play : 0.0 : extra space to allow finger move in and out (multiples of thickness)
      * extra_length : 0.0 : extra material to grind away burn marks (multiples of thickness)
      * bottom_lip : 0.0 : height of the bottom lips sticking out  (multiples of thickness) FingerHoleEdge only!
    """

    absolute_params = {
        **edges.FingerJointSettings.absolute_params,
        "style": ("rectangular",),
    }


class MatrixStand(Boxes):
    """Stand for Matrix generator outputs with angled front and rear faces."""

    ui_group = "Misc"

    x: float
    front_depth: float
    front_section_height: float
    front_face_height: float
    front_panel_angle: float
    front_panel_mount: str
    rear_depth: float
    rear_section_height: float
    rear_face_height: float
    rear_panel_angle: float
    rear_panel_mount: str
    panel_magnet_diameter: float
    center_depth: float
    center_height: float

    # Geometry tuning values (multiples of material thickness).
    FINGERJOINT_SURROUNDING_SPACES = 0.5
    MIN_TOP_DEPTH_MULTIPLIER = 0.1
    FINGER_CLEARANCE_RATIO = 1.0 / 8.0
    WALL_FINGER_OFFSET_T = 0.5
    FRONT_WALL_IGNORE_WIDTHS = (7, 4)
    BACK_WALL_IGNORE_WIDTHS = (0, 3)
    FACE_PANEL_EDGE_SPEC = "hehe"
    PANEL_HARDWARE_COUNT = 2
    PANEL_CLIP_HEIGHT_T = 4.0
    PANEL_CLIP_SIDE_HEIGHT_T = 3.0
    PANEL_HARDWARE_X_OFFSET_T = 3.0
    PANEL_HARDWARE_Y_OFFSET_T = 1.5
    PANEL_CLIP_SLOT_WIDTH_T = 3.0
    PANEL_EDGE_SLOT_WIDTH_T = 2.5
    PANEL_SLOT_HEIGHT_T = 1.05
    PANEL_CENTER_SLOT_WIDTH_T = 2.0
    PANEL_LATCH_HEIGHT_T = 2.5
    PANEL_LATCH_INSET_T = 4.0
    PANEL_LATCH_END_OFFSET_T = 3.0
    PANEL_LATCH_TAB_DEPTH_T = 1.5
    PANEL_LATCH_STEP_T = 0.5
    PANEL_LATCH_BASE_OFFSET_T = 2.0

    description = """
Matrix stand with front and rear angled faces and a center bridge.

This generator builds a stand around the Matrix enclosure. Before you cut,
measure the Matrix you designed with the Matrix generator and your physical
panel. All dimensions here are internal, so add clearance if you want a loose
fit. Set the stand width (x) and depths so the panel fits snugly with your
preferred clearance.

The stand is made from three depth segments:
- Front section with an angled face panel
- Center bridge between the sections
- Rear section with an angled face panel

The side panels and bottom are each drawn as single parts spanning all three segments.

#### Settings notes
- x: internal stand width; match the Matrix width plus any clearance.
- front_depth / rear_depth: depth of each angled section.
- front_section_height / rear_section_height: total height at each section's back wall.
- front_face_height / rear_face_height: vertical height below each face panel.
- front_panel_angle / rear_panel_angle: tilt angle in degrees (90 degrees is vertical).
- center_depth / center_height: size of the center bridge; center_height must be <= both section heights.
- front_panel_mount / rear_panel_mount: face panels are removable; choose spring tabs or magnets.
- panel_magnet_diameter: magnet diameter when using magnets (match your hardware).
- All dimensions are internal; there is no outside sizing option.

#### Build guide
1. Cut all parts.
2. Glue the left and right side panels to the bottom panel.
3. Add the center bridge top (if any) between the side panels.
4. Assemble the front section: front wall, face panel, top (if any), and back wall.
5. Assemble the rear section: front wall, face panel, top (if any), and back wall.
6. Install the panel hardware (springs or magnets) for the removable face panels.
7. Dry-fit your Matrix and adjust before final glue-up.

#### Customization tips
- Consider adding wiring or button holes to the back walls (front/rear) and to the face panels using a vector editor.
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

        self.addSettingsArgs(
            RectangularFingerJointSettings,
            prefix="FingerJoint",
            surroundingspaces=self.FINGERJOINT_SURROUNDING_SPACES,
        )

        self.buildArgParser(x=100)

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

    def render(self) -> None:
        """Render the Matrix stand parts in ordered layout rows.

        Args:
            None.
        Returns:
            None.
        """
        bottom_edge = self.edges["F"]
        inputs = self._collect_inputs()
        self._validate_inputs(inputs)

        front_section = self._build_section_profile(inputs.front)
        rear_section = self._build_section_profile(inputs.rear)

        total_depth = rear_section.depth + inputs.center_depth + front_section.depth

        logger.debug("MatrixStand inputs: %s", inputs)
        logger.debug("Front section profile: %s", front_section)
        logger.debug("Rear section profile: %s", rear_section)

        side_row_height = self._side_row_height(front_section, rear_section, bottom_edge)
        base_row_height, center_bridge_edge = self._base_row_layout(
            total_depth=total_depth,
            stand_width=inputs.stand_width,
            center_depth=inputs.center_depth,
            center_height=inputs.center_height,
        )
        front_row_height = self._section_row_height(front_section, inputs.stand_width, bottom_edge)
        rear_row_height = self._section_row_height(
            rear_section,
            inputs.stand_width,
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

        # Render rows in build order: side panels, base, then each section.
        rows = [
            RowPlan(
                name="Side Panels",
                height=side_row_height,
                render=lambda y: self._render_side_row(
                    row_y=y,
                    front_section=front_section,
                    rear_section=rear_section,
                    center_depth=inputs.center_depth,
                    center_height=inputs.center_height,
                    bottom_edge=bottom_edge,
                ),
            ),
            RowPlan(
                name="Base",
                height=base_row_height,
                render=lambda y: self._render_base_row(
                    row_y=y,
                    total_depth=total_depth,
                    stand_width=inputs.stand_width,
                    center_depth=inputs.center_depth,
                    rear_section=rear_section,
                    center_bridge_edge=center_bridge_edge,
                ),
            ),
            RowPlan(
                name="Front Section",
                height=front_row_height,
                render=lambda y: self._render_section_row(
                    row_y=y,
                    profile=front_section,
                    stand_width=inputs.stand_width,
                    bottom_edge=bottom_edge,
                    center_depth=inputs.center_depth,
                    center_height=inputs.center_height,
                    label_prefix="Front Section",
                ),
            ),
            RowPlan(
                name="Rear Section",
                height=rear_row_height,
                render=lambda y: self._render_section_row(
                    row_y=y,
                    profile=rear_section,
                    stand_width=inputs.stand_width,
                    bottom_edge=bottom_edge,
                    center_depth=inputs.center_depth,
                    center_height=inputs.center_height,
                    label_prefix="Rear Section",
                    top_depth_override=rear_section.top_depth,
                    top_front_edge_override=self._flush_back_top_edge(),
                    top_back_edge_override="e",
                ),
            ),
        ]

        row_y = 0.0
        for row in rows:
            logger.debug("Rendering row: %s", row.name)
            row.render(row_y)
            row_y += row.height

    def _collect_inputs(self) -> StandInputs:
        """Collect raw input dimensions from CLI arguments.

        Args:
            None.
        Returns:
            StandInputs: Raw input dimensions for the stand.
        """
        return StandInputs(
            stand_width=self.x,
            center_depth=self.center_depth,
            center_height=self.center_height,
            front=SectionInputs(
                depth=self.front_depth,
                back_wall_height=self.front_section_height,
                face_height=self.front_face_height,
                face_panel_angle_deg=self.front_panel_angle,
                face_panel_mount=self.front_panel_mount,
            ),
            rear=SectionInputs(
                depth=self.rear_depth,
                back_wall_height=self.rear_section_height,
                face_height=self.rear_face_height,
                face_panel_angle_deg=self.rear_panel_angle,
                face_panel_mount=self.rear_panel_mount,
            ),
        )

    def _validate_inputs(self, inputs: StandInputs) -> None:
        """Validate input dimensions before rendering.

        Args:
            inputs: Raw or adjusted input dimensions for the stand.
        Returns:
            None.
        Raises:
            ValueError: If any input values are invalid for the geometry.
        """
        if inputs.stand_width <= 0:
            raise ValueError("stand_width must be larger than 0.")
        if inputs.center_depth < 0:
            raise ValueError("center_depth must be 0 or larger.")
        if inputs.center_height < 0:
            raise ValueError("center_height must be 0 or larger.")

        self._validate_section_inputs(inputs.front, "front")
        self._validate_section_inputs(inputs.rear, "rear")

        if (
            self.panel_magnet_diameter <= 0
            and (inputs.front.face_panel_mount == "magnets" or inputs.rear.face_panel_mount == "magnets")
        ):
            raise ValueError("panel_magnet_diameter must be larger than 0 when using magnets.")

        if inputs.center_height > min(inputs.front.back_wall_height, inputs.rear.back_wall_height):
            raise ValueError(
                "center_height must be <= both section heights so the side panels cover the center bridge."
            )

    def _validate_section_inputs(self, section: SectionInputs, label: str) -> None:
        """Validate input dimensions for one section.

        Args:
            section: Input dimensions for the section.
            label: Section label used in error messages.
        Returns:
            None.
        Raises:
            ValueError: If any section values are invalid.
        """
        if section.depth < 0:
            raise ValueError(f"{label} section depth must be 0 or larger.")
        if section.face_height < 0:
            raise ValueError(f"{label} face_height must be 0 or larger.")
        if section.back_wall_height <= section.face_height:
            raise ValueError(f"{label} back_wall_height must be larger than face_height.")
        if not (0 < section.face_panel_angle_deg <= 90):
            raise ValueError(f"{label} face panel angle must be between 0 and 90 degrees.")
        if section.face_panel_mount not in {"springs", "magnets"}:
            raise ValueError(f"{label} face panel mount must be 'springs' or 'magnets'.")

    def _build_section_profile(self, inputs: SectionInputs) -> StandSectionProfile:
        """Compute derived geometry for a stand section.

        Args:
            inputs: Raw input dimensions for the section.
        Returns:
            StandSectionProfile: Resolved geometry for the section.
        """
        panel_angle_rad = math.radians(inputs.face_panel_angle_deg)

        # Panel length is constrained by the available rise and the available depth.
        panel_length_by_height = (inputs.back_wall_height - inputs.face_height) / math.sin(panel_angle_rad)
        panel_length_by_depth = inputs.depth / math.cos(panel_angle_rad)
        face_panel_length = min(panel_length_by_height, panel_length_by_depth)

        top_depth = inputs.depth - face_panel_length * math.cos(panel_angle_rad)
        back_wall_height = inputs.face_height + face_panel_length * math.sin(panel_angle_rad)

        min_top_depth = self.MIN_TOP_DEPTH_MULTIPLIER * self.thickness
        # Avoid tiny top slivers that are hard to cut and glue.
        has_top = top_depth > min_top_depth
        if not has_top:
            top_depth = 0.0

        return StandSectionProfile(
            depth=inputs.depth,
            back_wall_height=back_wall_height,
            face_height=inputs.face_height,
            face_panel_angle_deg=inputs.face_panel_angle_deg,
            face_panel_length=face_panel_length,
            top_depth=top_depth,
            has_top=has_top,
            face_panel_mount=inputs.face_panel_mount,
        )

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

        face_panel_edges = self._face_panel_edges()
        face_panel_width = self._face_panel_width(stand_width, face_panel_edges)
        height_candidates.append(
            self._rect_wall_overall_size(profile.face_panel_length, face_panel_width, face_panel_edges)[1]
        )

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
        row_height = max(row_height, self._face_panel_hardware_height(profile.face_panel_mount))
        return row_height

    def _render_side_row(
        self,
        *,
        row_y: float,
        front_section: StandSectionProfile,
        rear_section: StandSectionProfile,
        center_depth: float,
        center_height: float,
        bottom_edge: edges.BaseEdge,
    ) -> None:
        """Render the row containing the left and right side panels.

        Args:
            row_y: Current vertical offset for the row.
            front_section: Geometry for the front section.
            rear_section: Geometry for the rear section.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
            bottom_edge: Edge profile for the bottom.
        Returns:
            None.
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

    def _render_base_row(
        self,
        *,
        row_y: float,
        total_depth: float,
        stand_width: float,
        center_depth: float,
        rear_section: StandSectionProfile,
        center_bridge_edge: edges.BaseEdge | str | None,
    ) -> None:
        """Render the row containing the bottom and center bridge top.

        Args:
            row_y: Current vertical offset for the row.
            total_depth: Total stand depth in mm.
            stand_width: Overall stand width in mm.
            center_depth: Depth of the center bridge section.
            rear_section: Geometry for the rear section.
            center_bridge_edge: Edge profile for the center bridge top.
        Returns:
            None.
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

    def _render_section_row(
        self,
        *,
        row_y: float,
        profile: StandSectionProfile,
        stand_width: float,
        bottom_edge: edges.BaseEdge,
        center_depth: float,
        center_height: float,
        label_prefix: str,
        top_depth_override: float | None = None,
        top_front_edge_override: edges.BaseEdge | str | None = None,
        top_back_edge_override: edges.BaseEdge | str | None = None,
    ) -> None:
        """Render the row containing all parts of one section.

        Args:
            row_y: Current vertical offset for the row.
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
        self.corner(90 - front_section.face_panel_angle_deg)

        # Front angled panel.
        self._draw_face_panel_edge(
            front_section.face_panel_length,
            front_section.face_panel_mount,
        )

        # Connect the two section heights across the center bridge depth.
        height_delta = rear_section.back_wall_height - front_section.back_wall_height
        center_slope_angle_deg = math.degrees(math.atan2(height_delta, center_depth)) if center_depth else 0.0
        center_slope_length = math.hypot(center_depth, height_delta) if center_depth else 0.0

        if front_section.has_top:
            self.corner(front_section.face_panel_angle_deg)
            self._draw_top_edge_segment(front_section)
            if center_slope_length:
                self.corner(-center_slope_angle_deg)
        else:
            if center_slope_length:
                self.corner(front_section.face_panel_angle_deg - center_slope_angle_deg)
            else:
                self.corner(front_section.face_panel_angle_deg)

        if center_slope_length:
            self.edge(center_slope_length)
            self.corner(center_slope_angle_deg)

        # Rear top edge (reverse direction).
        if rear_section.has_top:
            self._draw_top_edge_segment(rear_section)

        # Rear angled panel.
        self.corner(rear_section.face_panel_angle_deg)
        self._draw_face_panel_edge(
            rear_section.face_panel_length,
            rear_section.face_panel_mount,
        )
        self.corner(90 - rear_section.face_panel_angle_deg)

        # Rear vertical wall (outer face).
        rear_vertical_height = rear_section.face_height + bottom_edge.startwidth()
        self.edges["f"](rear_vertical_height)
        self.corner(90)

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
        wall_offset = self.WALL_FINGER_OFFSET_T * thickness

        # Offset by half a thickness so finger holes align with wall centers.
        rear_wall_pos = rear_section.depth - wall_offset
        front_wall_pos = rear_section.depth + center_depth + wall_offset

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
        self._render_section_front_wall(profile, stand_width, bottom_edge, label_prefix=label_prefix)
        self._render_section_face_panel(profile, stand_width, label_prefix=label_prefix)
        self._render_section_top(
            profile,
            stand_width,
            label_prefix=label_prefix,
            top_depth_override=top_depth_override,
            top_front_edge_override=top_front_edge_override,
            top_back_edge_override=top_back_edge_override,
        )
        self._render_section_back_wall(
            profile,
            stand_width,
            center_depth=center_depth,
            center_height=center_height,
            label_prefix=label_prefix,
        )

        # Hardware for removable face panels.
        self._render_face_panel_hardware(profile)

    def _render_section_front_wall(
        self,
        profile: StandSectionProfile,
        stand_width: float,
        bottom_edge: edges.BaseEdge,
        *,
        label_prefix: str,
    ) -> None:
        """Render the front wall below the angled face panel.

        Args:
            profile: Section geometry profile.
            stand_width: Overall stand width in mm.
            bottom_edge: Edge profile for the bottom.
            label_prefix: Prefix used for part labels.
        Returns:
            None.
        """
        self.rectangularWall(
            profile.face_height,
            stand_width,
            ("F", "e", "F", bottom_edge),
            # Skip finger holes near edges to keep the angled front clean.
            ignore_widths=self.FRONT_WALL_IGNORE_WIDTHS,
            move="right",
            label=f"{label_prefix} Front Wall",
        )

    def _render_section_face_panel(
        self,
        profile: StandSectionProfile,
        stand_width: float,
        *,
        label_prefix: str,
    ) -> None:
        """Render the removable angled face panel.

        Args:
            profile: Section geometry profile.
            stand_width: Overall stand width in mm.
            label_prefix: Prefix used for part labels.
        Returns:
            None.
        """
        face_panel_edges = self._face_panel_edges()
        face_panel_width = self._face_panel_width(stand_width, face_panel_edges)
        self.rectangularWall(
            profile.face_panel_length,
            face_panel_width,
            face_panel_edges,
            move="right",
            label=f"{label_prefix} Face Panel",
        )

    def _render_section_top(
        self,
        profile: StandSectionProfile,
        stand_width: float,
        *,
        label_prefix: str,
        top_depth_override: float | None = None,
        top_front_edge_override: edges.BaseEdge | str | None = None,
        top_back_edge_override: edges.BaseEdge | str | None = None,
    ) -> None:
        """Render the top panel for a section when one is present.

        Args:
            profile: Section geometry profile.
            stand_width: Overall stand width in mm.
            label_prefix: Prefix used for part labels.
            top_depth_override: Optional override for the top depth.
            top_front_edge_override: Optional override for the top front edge profile.
            top_back_edge_override: Optional override for the top back edge profile.
        Returns:
            None.
        """
        if not profile.has_top:
            return

        top_front_edge = top_front_edge_override or "E"
        top_back_edge = top_back_edge_override or "F"
        top_depth = (
            top_depth_override
            if top_depth_override is not None
            else self._top_depth_for_profile(profile, top_front_edge, top_back_edge)
        )
        if top_depth <= 0:
            return

        self.rectangularWall(
            top_depth,
            stand_width,
            ("F", top_front_edge, "F", top_back_edge),
            move="right",
            label=f"{label_prefix} Top",
        )

    def _render_section_back_wall(
        self,
        profile: StandSectionProfile,
        stand_width: float,
        *,
        center_depth: float,
        center_height: float,
        label_prefix: str,
    ) -> None:
        """Render the back wall for a section.

        Args:
            profile: Section geometry profile.
            stand_width: Overall stand width in mm.
            center_depth: Depth of the center bridge section.
            center_height: Height of the center bridge section.
            label_prefix: Prefix used for part labels.
        Returns:
            None.
        """
        back_top_edge = "f"
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
            # Skip finger holes near the base so the back wall seats cleanly.
            ignore_widths=self.BACK_WALL_IGNORE_WIDTHS,
            callback=back_wall_callback,
            move="right",
            label=f"{label_prefix} Back Wall",
        )

    def _render_face_panel_hardware(self, profile: StandSectionProfile) -> None:
        """Render hardware parts for removable face panels.

        Args:
            profile: Section geometry profile.
        Returns:
            None.
        """
        if profile.face_panel_mount == "springs":
            for _ in range(self.PANEL_HARDWARE_COUNT):
                self._render_face_panel_latch(profile.face_panel_length, "up")
        # Two clips per panel (left/right).
        for _ in range(self.PANEL_HARDWARE_COUNT):
            self._render_face_panel_clip(profile.face_panel_length, "up", face_panel_mount=profile.face_panel_mount)

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
        wall_offset = self.WALL_FINGER_OFFSET_T * thickness
        # Offset by half a thickness so finger holes align with wall centers.
        rear_wall_pos = rear_section.depth - wall_offset
        clearance, span_length = self._finger_joint_span(stand_width)
        if span_length > 0:
            self.fingerHolesAt(rear_wall_pos, clearance, span_length, 90)
        else:
            self.fingerHolesAt(rear_wall_pos, 0, stand_width, 90)
        if center_depth > 0:
            front_wall_pos = rear_section.depth + center_depth + wall_offset
            if span_length > 0:
                self.fingerHolesAt(front_wall_pos, clearance, span_length, 90)
            else:
                self.fingerHolesAt(front_wall_pos, 0, stand_width, 90)

    def _render_face_panel_clip(
        self,
        face_panel_length: float,
        move=None,
        *,
        face_panel_mount: str = "springs",
    ) -> None:
        """Render the side clip pieces for removable face panels.

        Args:
            face_panel_length: Length of the face panel edge in mm.
            move: Layout movement hint.
            face_panel_mount: Panel mounting style ("springs" or "magnets").
        Returns:
            None.
        """
        thickness = self.thickness

        total_width = face_panel_length
        clip_height = self.PANEL_CLIP_HEIGHT_T * thickness
        clip_side_height = self.PANEL_CLIP_SIDE_HEIGHT_T * thickness
        hole_x_offset = self.PANEL_HARDWARE_X_OFFSET_T * thickness
        hole_y_offset = self.PANEL_HARDWARE_Y_OFFSET_T * thickness
        slot_width = self.PANEL_CLIP_SLOT_WIDTH_T * thickness
        slot_height = self.PANEL_SLOT_HEIGHT_T * thickness
        center_slot_width = self.PANEL_CENTER_SLOT_WIDTH_T * thickness
        total_height = clip_height

        if self.move(total_width, total_height, move, True):
            return

        if face_panel_mount == "magnets":
            self.hole(hole_x_offset, hole_y_offset, d=self.panel_magnet_diameter)
            self.hole(face_panel_length - hole_x_offset, hole_y_offset, d=self.panel_magnet_diameter)
        else:
            # Slightly taller slots improve spring-tab clearance.
            self.rectangularHole(hole_x_offset, hole_y_offset, slot_width, slot_height)
            self.rectangularHole(face_panel_length - hole_x_offset, hole_y_offset, slot_width, slot_height)
            self.rectangularHole(face_panel_length / 2, hole_y_offset, center_slot_width, thickness)

        self.polyline(face_panel_length, 90, clip_side_height, 90)
        self.edges["f"](face_panel_length)
        self.polyline(0, 90, clip_side_height, 90)
        self.move(total_width, total_height, move)

    def _render_face_panel_latch(self, face_panel_length: float, move=None) -> None:
        """Render a spring latch used by removable face panels.

        Args:
            face_panel_length: Length of the face panel edge in mm.
            move: Layout movement hint.
        Returns:
            None.
        """
        thickness = self.thickness

        # Inset the latch so it clears the panel edges and clip slots.
        latch_length = face_panel_length - self.PANEL_LATCH_INSET_T * thickness
        latch_height = self.PANEL_LATCH_HEIGHT_T * thickness
        latch_end_offset = self.PANEL_LATCH_END_OFFSET_T * thickness
        tab_depth = self.PANEL_LATCH_TAB_DEPTH_T * thickness
        step_depth = self.PANEL_LATCH_STEP_T * thickness
        base_offset = self.PANEL_LATCH_BASE_OFFSET_T * thickness
        total_width = latch_length
        total_height = latch_height

        if self.move(total_width, total_height, move, True):
            return

        # One half of the latch profile; mirrored for symmetry and spring flex.
        end_segment = [
            latch_length / 2 - latch_end_offset,
            -90,
            tab_depth,
            (90, step_depth),
            thickness,
            (90, step_depth),
            thickness,
            90,
            step_depth,
            -90,
            step_depth,
            -90,
            0,
            (90, step_depth),
            0,
            90,
        ]

        # Start one thickness inboard so the latch clears the panel edge.
        latch_mid_offset = latch_length / 2 - thickness
        self.moveTo(latch_mid_offset, base_offset, -90)
        preamble = [thickness, 90, base_offset, 90, thickness, -90]
        self.polyline(
            *(preamble + end_segment + [latch_length] + list(reversed(end_segment)))
        )
        self.move(total_width, total_height, move)

    def _draw_face_panel_edge(self, edge_length: float, face_panel_mount: str) -> None:
        """Draw a face panel edge with mounting cutouts.

        Args:
            edge_length: Length of the face panel edge in mm.
            face_panel_mount: Panel mounting style ("springs" or "magnets").
        Returns:
            None.
        """
        thickness = self.thickness
        hole_x_offset = self.PANEL_HARDWARE_X_OFFSET_T * thickness
        hole_y_offset = self.PANEL_HARDWARE_Y_OFFSET_T * thickness
        slot_width = self.PANEL_EDGE_SLOT_WIDTH_T * thickness
        slot_height = self.PANEL_SLOT_HEIGHT_T * thickness
        if face_panel_mount == "magnets":
            self.hole(hole_x_offset, hole_y_offset, d=self.panel_magnet_diameter)
        else:
            # Slightly taller slots improve spring-tab clearance.
            self.rectangularHole(hole_x_offset, hole_y_offset, slot_width, slot_height)
        self.edge(edge_length)
        if face_panel_mount == "magnets":
            self.hole(-hole_x_offset, hole_y_offset, d=self.panel_magnet_diameter)
        else:
            self.rectangularHole(-hole_x_offset, hole_y_offset, slot_width, slot_height)

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

    def _finger_joint_span(self, length: float) -> tuple[float, float]:
        """Compute clearance and span for finger joints along an edge.

        Args:
            length: Total edge length.
        Returns:
            tuple[float, float]: Clearance on each side and the middle span length.
        """
        finger_length = self.edges["f"].settings.finger * self.thickness
        # Limit clearance to keep a useful center finger span.
        clearance = min(finger_length, length * self.FINGER_CLEARANCE_RATIO)
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

    def _face_panel_hardware_height(self, face_panel_mount: str) -> float:
        """Compute the layout height needed for face panel hardware parts.

        Args:
            face_panel_mount: Panel mounting style ("springs" or "magnets").
        Returns:
            float: Minimum height needed to stack face panel hardware parts.
        """
        thickness = self.thickness
        side_clip_height = self.PANEL_CLIP_HEIGHT_T * thickness
        total_height = self.PANEL_HARDWARE_COUNT * (side_clip_height + self.spacing)
        if face_panel_mount == "springs":
            latch_height = self.PANEL_LATCH_HEIGHT_T * thickness
            total_height += self.PANEL_HARDWARE_COUNT * (latch_height + self.spacing)
        return total_height

    def _resolve_edges(self, edges_spec: EdgeSpec) -> list[edges.BaseEdge]:
        """Resolve an edge specification into edge objects.

        Args:
            edges_spec: Edge specification using chars or edge objects.
        Returns:
            list[edges.BaseEdge]: Resolved edges for sizing.
        """
        if isinstance(edges_spec, str):
            edges_spec = list(edges_spec)
        resolved: list[edges.BaseEdge] = []
        for edge in edges_spec:
            if isinstance(edge, str):
                resolved.append(self.edges[edge])
            else:
                resolved.append(edge)
        return resolved

    def _face_panel_edges(self) -> EdgeSpec:
        """Return the edge specification for removable face panels.

        The opposing "h" edges add finger holes so the clips/latches can engage.

        Args:
            None.
        Returns:
            EdgeSpec: Edge specification for the face panel.
        """
        return self.FACE_PANEL_EDGE_SPEC

    def _rect_wall_overall_size(self, width: float, height: float, edges_spec: EdgeSpec) -> tuple[float, float]:
        """Calculate the overall size of a rectangular wall including edge spacing.

        Args:
            width: Interior width of the wall in mm.
            height: Interior height of the wall in mm.
            edges_spec: Edge specification for the wall.
        Returns:
            tuple[float, float]: Overall width and height including spacing.
        """
        edges_list = self._resolve_edges(edges_spec)
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

    def _face_panel_width(self, stand_width: float, face_panel_edges: EdgeSpec) -> float:
        """Compute the usable face panel width between edge profiles.

        Args:
            stand_width: Overall stand width in mm.
            face_panel_edges: Edge specification for the face panel.
        Returns:
            float: Usable face panel width in mm.
        Raises:
            ValueError: If the panel width is too small for the edge profiles.
        """
        edges_list = self._resolve_edges(face_panel_edges)
        panel_width = stand_width - edges_list[0].startwidth() - edges_list[2].startwidth()
        if panel_width <= 0:
            raise ValueError("Face panel width is too small for the selected edge profile.")
        return panel_width
