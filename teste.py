# teste_circuito.py
# Circuito:
# Vin -- R1 --●(nó X)------> (+) opamp
#              |             |
#              |             R2
#              |             |
#              |             ●(nó Y)
#              |             |
#             C1            C2
#              |             |
#             (-) opamp     GND
#
# Saída do opamp (Vout) em realimentação para a entrada (-).

import schemdraw
import schemdraw.elements as elm
from schemdraw import ImageFormat

# Usa backend matplotlib
schemdraw.use("matplotlib")

# Valores só para teste de labels
R1 = 1.0
R2 = 1.0
C1 = 1.0
C2 = 1.0

d = schemdraw.Drawing(scale=0.9)

# ----- Vin, R1 e nó X -----
vin = d.add(elm.SourceV().left().label('$V_{in}$', loc='left'))
d += elm.Ground()
d += elm.Line().right()
d += elm.Resistor().right().label(f'R1 = {R1:g} Ω')
d += elm.Line().right()
node_x = d.here      # nó entre R1 e R2
d += elm.Dot()

# ----- Opamp virado para a direita (– em cima, + embaixo) -----
# Colocamos o opamp um pouco à direita e alinhado com node_x.
d += elm.Line().right().length(2)
op_pos = d.here

op = d.add(
    elm.Opamp(leads=True)   # opamp com pinos explícitos
    .at(op_pos)             # triângulo aqui
)

# Garantir orientação padrão: schemdraw já desenha apontando para a direita,
# com in2 (–) em cima e in1 (+) embaixo.

# ----- Conexão do nó X à entrada + -----
# Ligamos node_x ao pino positivo (in1).
d += elm.Line().to(op.in1).at(node_x)

# ----- R2 e C2 em série para baixo a partir da entrada + -----
d += elm.Resistor().down().at(op.in1).label(f'R2 = {R2:g} Ω', loc='right')
node_y = d.here
d += elm.Dot()

d += elm.Capacitor().down().label(f'C2 = {C2:g} F', loc='right')
d += elm.Ground()

# ----- C1 do nó X à entrada – -----
d += elm.Capacitor().up().at(node_x).toy(
    op.in2).label(f'C1 = {C1:g} F', loc='left')
d += elm.Line().to(op.in2)

# ----- Saída, Vout e realimentação para entrada – -----
d += elm.Line().right().at(op.out).length(2)
fb = d.here
d += elm.Dot(open=True)
d += elm.Line().right().label('$V_{out}$', loc='right')

# Realimentação: da saída volta por cima até a entrada negativa
d += elm.Line().up().at(fb).length(2)
d += elm.Line().left().tox(op.in2)
d += elm.Line().down().to(op.in2)

# ----- Gera PNG em bytes e salva em arquivo -----
png_bytes = d.get_imagedata(ImageFormat.PNG)

with open('circuito.png', 'wb') as f:
    f.write(png_bytes)

print('Imagem salva como circuito.png')
