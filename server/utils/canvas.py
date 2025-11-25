from typing import Optional, Dict, Any, Union
from services.db_service import db_service


async def find_next_best_element_position(canvas_data, max_num_per_row=4, spacing=20):
    """
    Calculates the next best position for a new element on the canvas.
    This final version uses a robust row detection algorithm to handle complex layouts.
    """
    elements = canvas_data.get("elements", [])  # 获取画布中的所有元素

    media_elements = [
        e
        for e in elements
        if e.get("type") in ["image", "embeddable", "video"] and not e.get("isDeleted")
    ]  # 只获取画布中未被删除的image、embeddable、video元素

    if not media_elements:
        return 0, 0

    # Sort elements by their top-left corner 元素排序
    media_elements.sort(key=lambda e: (e.get("y", 0), e.get("x", 0)))

    # Group elements into rows based on vertical overlap  以垂直坐标是否重叠为依据将元素分行
    rows = []
    for element in media_elements:
        y, height = element.get("y", 0), element.get("height", 0)
        placed = False
        for row in rows:
            # Check if the element vertically overlaps with any element in the row
            if any(
                max(y, r.get("y", 0))
                < min(y + height, r.get("y", 0) + r.get("height", 0))
                for r in row
            ):
                row.append(element)
                placed = True
                break
        if not placed:
            rows.append([element])

    # Sort rows by their average y-coordinate 按平均y坐标对所有row进行排序
    rows.sort(key=lambda row: sum(e.get("y", 0) for e in row) / len(row))

    if not rows:
        return 0, 0

    last_row = rows[-1]
    last_row.sort(key=lambda e: e.get("x", 0))  # 按x坐标对最后一行中的元素进行排序

    if len(last_row) < max_num_per_row:  # 如果最后一行元素未满，追加元素到最后一行
        # Add to the last row
        rightmost_element = last_row[-1]
        new_x = (
            rightmost_element.get("x", 0) + rightmost_element.get("width", 0) + spacing
        )
        # Align with the top of the last row for consistency
        new_y = min(e.get("y", 0) for e in last_row)
    else:
        # Start a new row
        new_x = 0
        # Position below the entire last row
        bottom_of_last_row = max(e.get("y", 0) + e.get("height", 0) for e in last_row)
        new_y = bottom_of_last_row + spacing

    return new_x, new_y  # 返回新的x、y坐标
