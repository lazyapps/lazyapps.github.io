"""A rounded tire cross-section with shallow modeled tread grooves."""
import math

def tire(mesh, material, owner):
    profile = [(-.122,.26),(-.120,.32),(-.115,.36),(-.106,.397),
               (-.09,.421),(-.075,.432),(-.06,.435),(-.049,.435),
               (-.045,.432),(-.041,.435),(-.025,.435),(0,.435),
               (.025,.435),(.041,.435),(.045,.432),(.049,.435),
               (.06,.435),(.075,.432),(.09,.421),(.106,.397),
               (.115,.36),(.120,.32),(.122,.26)]
    segments = 192
    vertices = []
    for z,r in profile:
        for j in range(segments):
            angle=j*math.tau/segments
            phase=(j/3+z*10)%1
            diagonal=max(0,1-min(phase,1-phase)/.13)
            depth=.0014*diagonal if abs(z)<.075 else 0
            radius=r-depth
            vertices.append((radius*math.cos(angle),radius*math.sin(angle),z))
    faces=[]
    for row in range(len(profile)-1):
        for j in range(segments):
            a=row*segments+j;b=row*segments+(j+1)%segments
            faces.append((a,b,b+segments,a+segments))
    for j in range(segments):
        faces.append((j,(len(profile)-1)*segments+j,(len(profile)-1)*segments+(j+1)%segments,(j+1)%segments))
    return mesh('Rounded radial tire with real grooves',vertices,faces,material,owner)
