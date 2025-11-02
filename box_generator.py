#!/usr/bin/env python3

import argparse
import textwrap

# all dimensions in millimeters
DEFAULT_BOOK_WIDTH = 150
DEFAULT_BOOK_HEIGHT = 200
DEFAULT_BOOK_THICKNESS = 30

# 3 mm is the thickness of 1/8 wood
DEFAULT_MATERIAL_THICKNESS = 3

CORNER_LENGTH = 20
MIN_SLOT_LENGTH = 25
MAX_SLOT_LENGTH = 50
MARGIN_LENGTH = 5

# millimeters must be multiplied by 1000 for the SVG file
SVG_SCALE = 1000


def calculate_slots_and_fingers_for_width(
    length,
    corner_length,
    material_thickness,
    min_length=MIN_SLOT_LENGTH,
    max_length=MAX_SLOT_LENGTH,
):
    """
    Calculate optimal number of even slots/fingers for a given length.
    Each slot/finger must be between min_length and max_length.
    Always returns an even number of slots/fingers.
    """
    available_length = (length + material_thickness) - (2 * corner_length)

    # Start with 2 slots/fingers (minimum even number)
    number_of_slots_and_fingers = 2

    while True:
        slots_and_fingers_length = available_length / number_of_slots_and_fingers

        # If slot/finger length is within bounds, we're done
        if min_length <= slots_and_fingers_length <= max_length:
            break

        # If too big, add 2 more slots/fingers
        if slots_and_fingers_length > max_length:
            number_of_slots_and_fingers += 2
        # If too small, remove 2 slots/fingers (but keep minimum of 2)
        elif slots_and_fingers_length < min_length and number_of_slots_and_fingers > 2:
            number_of_slots_and_fingers -= 2
        else:
            # Can't make it work with current constraints
            break

    slots_and_fingers_length = available_length / number_of_slots_and_fingers
    return number_of_slots_and_fingers, slots_and_fingers_length


def calculate_slots_and_fingers_for_height(
    length,
    corner_length,
    material_thickness,
    min_length=MIN_SLOT_LENGTH,
    max_length=MAX_SLOT_LENGTH,
):
    """
    Calculate odd number of slots and even number of fingers.
    Sockets are the gaps, fingers are the protruding parts.
    Returns (number_of_slots_and_fingers_for_height, slots_and_fingers_length)
    """
    available_length = (length + (2 * material_thickness)) - (2 * corner_length)

    # Start with 3 slots (minimum odd number) and 2 fingers (even)
    number_of_slots = 3

    while True:
        # Total slots/fingers = slots + fingers
        total_number_of_slots = number_of_slots + (
            number_of_slots - 1
        )  # fingers = slots - 1 (to keep even)
        slots_and_fingers_length = available_length / total_number_of_slots

        if min_length <= slots_and_fingers_length <= max_length:
            break

        if slots_and_fingers_length > max_length:
            number_of_slots += 2  # Keep odd
        elif slots_and_fingers_length < min_length and number_of_slots > 3:
            number_of_slots -= 2  # Keep odd, minimum 3
        else:
            break

    number_of_fingers = number_of_slots - 1  # Even number
    total_number_of_slots = number_of_slots + number_of_fingers
    slots_and_fingers_length = available_length / total_number_of_slots

    return number_of_slots + number_of_fingers, slots_and_fingers_length


def create_top_and_bottom_path(
    x_position,
    y_position,
    height,
    material_thickness,
    corner_length,
    number_of_slots_and_fingers_for_width,
    slot_and_finger_length_for_width,
):
    height = height * SVG_SCALE
    material_thickness = material_thickness * SVG_SCALE
    slot_and_finger_length = slot_and_finger_length_for_width * SVG_SCALE
    corner_length = corner_length * SVG_SCALE

    path_data = [
        # This is the starting x/y position
        f"M {x_position * SVG_SCALE},{y_position * SVG_SCALE}",
        # Create the top left corner
        f" h {corner_length}",
        # Create the first slot by moving down
        f" v {material_thickness}",
    ]

    path_data.extend(
        # Create a series of slots and fingers
        f" h {slot_and_finger_length} v {-material_thickness if i % 2 == 0 else material_thickness}"
        for i in range(number_of_slots_and_fingers_for_width)
    )

    # Create the top right corner
    path_data.append(f" h {corner_length - material_thickness}")

    # Right edge with single finger
    finger_height = height / 3
    remaining_height = height - finger_height

    path_data.extend(
        [
            # First part of right edge
            f" v {remaining_height / 2}",
            # Single finger
            f" h {material_thickness} v {finger_height} h -{material_thickness}",
            # Rest of the right edge
            f" v {remaining_height / 2}",
            # Create the bottom right corner
            f" h -{corner_length - material_thickness} v {material_thickness}",
        ]
    )

    path_data.extend(
        # Create a series of slots and fingers mirroring the top edge pattern in reverse
        f" h -{slot_and_finger_length} v {material_thickness if i % 2 == 0 else -material_thickness}"
        for i in range(number_of_slots_and_fingers_for_width - 1, -1, -1)
    )

    path_data.extend(
        [
            # Create the bottom left corner
            f" h -{corner_length}",
            " Z",
        ]
    )
    return "".join(path_data)


def create_side_panel(
    x_position,
    y_position,
    material_thickness,
    corner_length,
    number_of_slots_and_fingers_for_height,
    slot_and_finger_length_for_height,
    number_of_slots_and_fingers_for_width,
    slot_and_finger_length_for_width,
):
    slot_and_finger_length_for_width = slot_and_finger_length_for_width * SVG_SCALE
    slot_and_finger_length_for_height = slot_and_finger_length_for_height * SVG_SCALE
    material_thickness = material_thickness * SVG_SCALE
    corner_length = corner_length * SVG_SCALE

    path_data = [
        f"M {x_position * SVG_SCALE},{y_position * SVG_SCALE}",
        # Create the top left corner
        f" h {corner_length} v {-material_thickness}",
    ]

    path_data.extend(
        # Create a series of slots and fingers along the top edge
        f" h {slot_and_finger_length_for_width} v {material_thickness if i % 2 == 0 else -material_thickness}"
        for i in range(number_of_slots_and_fingers_for_width)
    )

    # Create the top right corner
    path_data.append(f" h {corner_length} v {corner_length}")

    # Create a series of slots and fingers along the right edge
    for i in range(number_of_slots_and_fingers_for_height):
        if i % 2 == 0:
            # slot
            path_data.append(
                f" h -{material_thickness} v {slot_and_finger_length_for_height} h {material_thickness}"
            )
        else:
            # Finger
            path_data.append(f" v {slot_and_finger_length_for_height}")

    path_data.extend(
        [
            # Create the bottom right corner
            f" v {corner_length} h -{corner_length}",
            # Create the first slot by moving up
            f" v {-material_thickness}",
        ]
    )

    path_data.extend(
        # Create a series of slots and fingers along the bottom edge
        f" h -{slot_and_finger_length_for_width} v {-material_thickness if i % 2 == 0 else material_thickness}"
        for i in range(number_of_slots_and_fingers_for_width - 1, -1, -1)
    )

    path_data.extend(
        [
            # Create the bottom left corner
            f" h -{corner_length}",
            " Z",
        ]
    )
    return "".join(path_data)


def create_back_panel(
    x_position,
    y_position,
    width,
    material_thickness,
    corner_length,
    number_of_slots_and_fingers_for_height,
    slots_and_fingers_length_for_height,
):
    width = width * SVG_SCALE
    material_thickness = material_thickness * SVG_SCALE
    slots_and_fingers_length = slots_and_fingers_length_for_height * SVG_SCALE
    corner_length = corner_length * SVG_SCALE

    # generally the thickness of a book is not very big, so we won't create a serices of slots/fingers. We'll just divide the back of the box into thirds
    third_of_the_width = width / 3

    path_data = [
        f"M {x_position * SVG_SCALE},{y_position * SVG_SCALE}",
        # First part of top edge
        f" h {third_of_the_width}",
        # Single slot
        f" v {material_thickness} h {third_of_the_width} v -{material_thickness}",
        # Rest of top edge
        f" h {third_of_the_width}",
        # Start with 20mm vertical line
        f" v {corner_length}",
    ]

    # Create a series of slots and fingers along the right edge
    # These slots/fingers should fit the edge of the side panel
    for i in range(number_of_slots_and_fingers_for_height):
        if i % 2 == 0:
            # Finger
            path_data.append(
                f" h {material_thickness} v {slots_and_fingers_length} h -{material_thickness}"
            )
        else:
            # Slot
            path_data.append(f" v {slots_and_fingers_length}")

    path_data.extend(
        [
            # End with 20mm vertical line
            f" v {corner_length}",
            # Bottom edge with socket (mirror top)
            f" h -{third_of_the_width}",
            # Single socket (inward)
            f" v -{material_thickness} h -{third_of_the_width} v {material_thickness}",
            # Rest of bottom edge
            f" h -{third_of_the_width}",
            # Left edge with slots (mirror right edge)
            f" v -{corner_length}",
        ]
    )

    # Create a series of slots and fingers along the left edge
    # These slots/fingers should fit the edge of the side panel
    for i in range(number_of_slots_and_fingers_for_height - 1, -1, -1):
        if i % 2 == 0:
            # Finger
            path_data.append(
                f" h -{material_thickness} v -{slots_and_fingers_length} h {material_thickness}"
            )
        else:
            # Slot
            path_data.append(f" v -{slots_and_fingers_length}")

    path_data.extend(
        [
            # End with 20mm vertical line
            f" v -{corner_length}",
            " Z",
        ]
    )
    return "".join(path_data)


def generate_svg(book_width, book_height, book_thickness, material_thickness):
    top_panel_width = book_width
    # add an extra millimeter to give the book a little room:
    side_panel_inner_height = book_height + 1
    top_panel_inner_thickness = book_thickness + 1

    paths = []

    (
        number_of_slots_and_fingers_for_width,
        slot_and_finger_length_for_width,
    ) = calculate_slots_and_fingers_for_width(
        top_panel_width,
        CORNER_LENGTH,
        material_thickness,
    )
    (
        number_of_slots_and_fingers_for_height,
        slot_and_finger_length_for_height,
    ) = calculate_slots_and_fingers_for_height(
        side_panel_inner_height,
        CORNER_LENGTH,
        material_thickness,
    )

    # Panel 1: Top/Bottom panels
    x_position = MARGIN_LENGTH
    y_position = MARGIN_LENGTH
    top_path = create_top_and_bottom_path(
        x_position,
        y_position,
        top_panel_inner_thickness,
        material_thickness,
        CORNER_LENGTH,
        number_of_slots_and_fingers_for_width,
        slot_and_finger_length_for_width,
    )
    paths.append(top_path)

    # Panel 2: Second top/bottom panel
    x_position += top_panel_width + (2 * material_thickness) + MARGIN_LENGTH
    bottom_path = create_top_and_bottom_path(
        x_position,
        y_position,
        top_panel_inner_thickness,
        material_thickness,
        CORNER_LENGTH,
        number_of_slots_and_fingers_for_width,
        slot_and_finger_length_for_width,
    )
    paths.append(bottom_path)

    # Panel 3: Side panels
    x_position = MARGIN_LENGTH
    y_position += top_panel_inner_thickness + (3 * material_thickness) + MARGIN_LENGTH
    left_path = create_side_panel(
        x_position,
        y_position,
        material_thickness,
        CORNER_LENGTH,
        number_of_slots_and_fingers_for_height,
        slot_and_finger_length_for_height,
        number_of_slots_and_fingers_for_width,
        slot_and_finger_length_for_width,
    )
    paths.append(left_path)

    # Panel 4: Second side panel (mirrored)
    x_position += top_panel_width + (2 * material_thickness) + MARGIN_LENGTH
    right_path = create_side_panel(
        x_position,
        y_position,
        material_thickness,
        CORNER_LENGTH,
        number_of_slots_and_fingers_for_height,
        slot_and_finger_length_for_height,
        number_of_slots_and_fingers_for_width,
        slot_and_finger_length_for_width,
    )
    paths.append(right_path)

    # Panel 5: Back panel
    x_position += top_panel_width + (2 * material_thickness) + MARGIN_LENGTH
    y_position = (
        top_panel_inner_thickness + (2 * material_thickness) + (MARGIN_LENGTH * 2)
    )
    back_path = create_back_panel(
        x_position,
        y_position,
        top_panel_inner_thickness,
        material_thickness,
        CORNER_LENGTH,
        number_of_slots_and_fingers_for_height,
        slot_and_finger_length_for_height,
    )
    paths.append(back_path)

    # SVG dimensions (with margins)
    svg_width = (
        x_position + top_panel_inner_thickness + material_thickness + MARGIN_LENGTH
    )
    svg_height = (
        y_position + side_panel_inner_height + (2 * material_thickness) + MARGIN_LENGTH
    )

    svg_header = textwrap.dedent(
        f"""
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <svg width="{svg_width}mm" height="{svg_height}mm" 
                viewBox="0 0 {svg_width * SVG_SCALE} {svg_height * SVG_SCALE}"
                xmlns="http://www.w3.org/2000/svg">
            <defs>
                <style type="text/css">
                .cut-line {{stroke:red;stroke-width:76.2;stroke-linejoin:bevel;fill:none}}
                </style>
            </defs>
        """
    )
    svg_footer = "</svg>"

    return (
        svg_header
        + "".join(f'<path d="{path}" class="cut-line" />' for path in paths)
        + "\n"
        + svg_footer
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate SVG file for a laser-cut book box",
        epilog=textwrap.dedent(
            """
            Examples:
            %(prog)s                                    # Use default dimensions
            %(prog)s --book-width 180 --book-height 250 # Custom book size
            %(prog)s --wood-thickness 4                 # Different wood thickness
            %(prog)s --book-width 160 --book-height 210 --book-thickness 25 --wood-thickness 3

            This script generates an SVG file (box-set.svg) containing laser-cut patterns
            for a three-panel book box. The box will fit a book of the specified dimensions
            with the given wood thickness for the box material.
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--book-width",
        type=int,
        default=DEFAULT_BOOK_WIDTH,
        help=f"Book width in mm (default: {DEFAULT_BOOK_WIDTH})",
    )
    parser.add_argument(
        "--book-height",
        type=int,
        default=DEFAULT_BOOK_HEIGHT,
        help=f"Book height in mm (default: {DEFAULT_BOOK_HEIGHT})",
    )
    parser.add_argument(
        "--book-thickness",
        type=int,
        default=DEFAULT_BOOK_THICKNESS,
        help=f"Book thickness in mm (default: {DEFAULT_BOOK_THICKNESS})",
    )
    parser.add_argument(
        "--material-thickness",
        type=int,
        default=DEFAULT_MATERIAL_THICKNESS,
        help=f"Wood thickness in mm (default: {DEFAULT_MATERIAL_THICKNESS})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    svg_content = generate_svg(
        args.book_width, args.book_height, args.book_thickness, args.material_thickness
    )

    with open("box-set.svg", "w") as f:
        f.write(svg_content)

    print(f"SVG file generated: box-set.svg")
