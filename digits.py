from build123d import *

w,b, h = tile_dim = (20, 20, 2)
d = 1

white = Color( (0.990901,0.990902,0.990903) ) 
black = Color( (0.010101,0.010102,0.010103) )

fn = "out/digits"

def digit(digit: int|str) -> Compound:
    digit = str(digit)
    
    # Base part
    with BuildPart() as p_base:
        Box(*tile_dim)
        fillet(p_base.edges().filter_by(Axis.Z), radius=1.5)
        
        with BuildSketch(p_base.faces().sort_by().last) as text_sketch:
            Text(digit, font_size=15)
        extrude(amount=-0.6, mode=Mode.SUBTRACT)
    
    p_base.part.color = white
    p_base.part.label = f"bOx_{digit}"

    with BuildPart() as p_digit:
        add(text_sketch.sketch)
        extrude(amount=-0.6)
    
    p_digit.part.color = black
    p_digit.part.label = f"tExT_{digit}"
    return Compound(label=f"dIgIt_{digit}", children=[p_base.part, p_digit.part])

digits = Compound(
    label="dIgItS",
    children = [ Location(( (w+d) * (i % 3), (b+d) * (i // 3) ,0)) * digit(i+1) for i in range(0,9)]
)

export_step(digits,f"{fn}.step")
export_brep(digits,f"{fn}.brep")
export_gltf(digits,f"{fn}.gltf")

exporter = Mesher()

exporter.add_shape(digits)
exporter.write(f"{fn}.3mf")
exporter.write(f"{fn}.stl")

from ocp_vscode import show, show_all
show_all()




