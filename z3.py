from build123d import *

w,b, h = tile_dim = (20, 20, 2)
d = 1

white = Color("White") 
black = Color("Black")

import os
script_name = os.path.basename(__file__)
fn = "out/" + script_name.replace(".py", "")    


def card(digit: int|str) -> Compound:
    digit = str(digit)

    with BuildPart() as p_base:
        Box(*tile_dim)
        fillet(p_base.edges().filter_by(Axis.Z), radius=1.5)
        
        with BuildSketch(p_base.faces().sort_by().last) as text_sketch:
            Text(digit, font_size=15)
        extrude(amount=-0.6, mode=Mode.SUBTRACT)
    
    p_base.part.color = white
    p_base.part.label = f"Basis_{digit}"

    with BuildPart() as p_digit:
        add(text_sketch.sketch)
        extrude(amount=-0.6)
    
    p_digit.part.color = black
    p_digit.part.label = f"Ziffer_{digit}"

    return Compound(label=f"Karte {digit}", children=[p_base.part, p_digit.part])

cards = Compound(
    label="Numbers",
    children = [ Location(( (w+d) * (i % 3), (b+d) * (i // 3) ,0)) * card(i+1) for i in range(0,9)]
)

export_step(cards,f"{fn}.step")

exporter = Mesher()

exporter.add_shape(cards)
exporter.write(f"{fn}.3mf")
exporter.write(f"{fn}.stl")

from ocp_vscode import show, show_all
show_all()

