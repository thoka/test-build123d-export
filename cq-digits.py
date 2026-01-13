"""
CadQuery version of digits generator.
Creates 3x3 grid of boxes with text labels.
"""

from cadquery import Workplane, Color
import cadquery as cq

w, b, h = tile_dim = (20, 20, 2)
d = 1

white_rgb = (0.990901, 0.990902, 0.990903)
black_rgb = (0.010101, 0.010102, 0.010103)

fn = "out/cq-digits"


def digit(num: int | str) -> cq.Assembly:
    """Create a single digit tile with recessed text on top surface."""
    num_str = str(num)

    # Base part: main box
    base = Workplane("XY").box(w, b, h).edges("|Z").fillet(1.5)
    
    # Get top face and create workplane on it
    top_face = base.faces(">Z").first()
    
    # Create text sketch positioned at top surface for cutting
    text_cut = Workplane("XY").moveTo(0, 0).text(num_str, fontsize=8, distance=0).extrude(-0.6)
    text_cut = text_cut.translate((0, 0, h/2))
    
    # Cut the pocket into the base
    base = base.cut(text_cut)
    
    # Create black text part - same shape, positioned in the pocket
    text_part = Workplane("XY").moveTo(0, 0).text(num_str, fontsize=8, distance=0).extrude(-0.55)
    text_part = text_part.translate((0, 0, h/2))
    
    # Combine as assembly
    asm = cq.Assembly()
    asm.add(base, name=f"bOx_{num_str}", color=Color(*white_rgb))
    asm.add(text_part, name=f"tExT_{num_str}", color=Color(*black_rgb))
    
    return asm


# Build 3x3 grid
root_asm = cq.Assembly(name="dIgItS")

for i in range(9):
    x = (w + d) * (i % 3)
    y = (b + d) * (i // 3)
    
    digit_asm = digit(i + 1)
    root_asm.add(digit_asm, name=f"dIgIt_{i+1}", loc=cq.Location((x, y, 0)))


# Export formats - CadQuery has limited export support
try:
    root_asm.save(f"{fn}.step")
    print(f"✓ STEP export successful")
except Exception as e:
    print(f"✗ STEP export failed: {e}")

try:
    root_asm.save(f"{fn}.stl")
    print(f"✓ STL export successful")
except Exception as e:
    print(f"✗ STL export failed: {e}")

# 3MF is not directly supported - skip
print(f"⊘ 3MF export skipped (not supported by CadQuery)")

# BREP export using OCP directly  
try:
    from OCP.BRepTools import BRepTools
    shape = root_asm.toCompound()
    BRepTools.Write_s(shape, str(f"{fn}.brep"))
    print(f"✓ BREP export successful")
except Exception as e:
    print(f"✗ BREP export failed: {e}")

print(f"\nExports complete at {fn}.*")

# Visualize in OCP VS Code extension
from ocp_vscode import show
show(root_asm)

