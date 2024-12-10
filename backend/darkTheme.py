import processingToolkit

# Example use of processingToolkit

example_grid = [
    [(1, "file1"), (2, "file2"), "_"],
    [(3, "[]"), (4, "file4"), (5, "[]")],
    ["_", (6, "file6"), (7, "file7")]
]

neighbours = processingToolkit.get_neighbors(grid=example_grid, target_id=4)
print(neighbours)
