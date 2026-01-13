"""
CadQuery version of digits generator.
Creates 3x3 grid of boxes with text labels.
"""

from cadquery import Workplane, Color
import cadquery as cq

w, b, h = tile_dim = (20, 20, 2)
d = 1

white = (0.990901, 0.990902, 0.990903)
black = (0.010101, 0.010102, 0.010103)

fn = "out/cq-digits"


def digit(num: int | str) -> cq.Assembly:
    """Create a single digit tile with recessed text on top surface."""
    num_str = str(num)

    base = Workplane("XY").box(w, b, h).edges("|Z").fillet(1.5)
    text = base.faces(">Z").workplane().text(num_str, fontsize=15, distance=-1, cut=False)

    base = base.cut(text)
    
    tile = cq.Assembly()
    tile.add(base, name=f"bOx_{num_str}", color=Color(*white))
    tile.add(text, name=f"tExT_{num_str}", color=Color(*black))
    
    return tile

# Build 3x3 grid
grid = cq.Assembly(name="dIgItS")

for i in range(9):
    x = (w + d) * (i % 3)
    y = (b + d) * (i // 3)
    
    grid.add(digit(i + 1), name=f"dIgIt_{i+1}", loc=cq.Location((x, y, 0)))


# Export formats - CadQuery has limited export support
try:
    grid.export(f"{fn}.step")
    print(f"✓ STEP export successful")
except Exception as e:
    print(f"✗ STEP export failed: {e}")

try:
    grid.export(f"{fn}.stl")
    print(f"✓ STL export successful")
except Exception as e:
    print(f"✗ STL export failed: {e}")

# 3MF is not directly supported - skip
print(f"⊘ 3MF export skipped (not supported by CadQuery)")

# BREP export using OCP directly  
try:
    from OCP.BRepTools import BRepTools
    shape = grid.toCompound()
    BRepTools.Write_s(shape, str(f"{fn}.brep"))
    print(f"✓ BREP export successful")
except Exception as e:
    print(f"✗ BREP export failed: {e}")

print(f"\nExports complete at {fn}.*")

# Visualize in OCP VS Code extension
from ocp_vscode import show
show(grid)

