def get_neighbors(grid, target_id):
    """
    Method that accepts a grid as produced in main.py at group_elements_fixed_10x10
    and a single id from the given grid to return all the neighbours of the item
    that has the given id.

    Returns: All eight neighbours in following order. Each neighbour is either the filename, "[]" for empty slot
            or "_" for no slot.

        neighbors:  ¦----¦-----------¦----¦
                    ¦ 0  ¦     1     ¦ 2  ¦
                    ¦----¦-----------¦----¦
                    ¦ 3  ¦ target_id ¦ 4  ¦
                    ¦----¦-----------¦----¦
                    ¦ 5  ¦     6     ¦ 7  ¦
                    ¦----¦-----------¦----¦
    """
    neighbors = []
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Finding x and y "coordinates" in given grid
    x, y = -1, -1
    for i in range(rows):
        for j in range(cols):
            if isinstance(grid[i][j], tuple) and grid[i][j][0] == target_id:
                x, y = i, j
                break
        if x != -1:
            break

    if x == -1 or y == -1:
        raise ValueError("ID not found.")

    # Creating neighbour matrix
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        ( 0, -1),          ( 0, 1),
        ( 1, -1), ( 1, 0), ( 1, 1)
    ]

    # Adding/ Subtracting from the position of the given element
    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < rows and 0 <= ny < cols:
            neighbor = grid[nx][ny]

            if neighbor != "_" and isinstance(neighbor, tuple):
                neighbors.append(neighbor[1])
            else:
                neighbors.append("_")
        else:
            neighbors.append("_")

    return neighbors


