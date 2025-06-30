from graphviz import Digraph

g = Digraph(comment="Red Neuronal Siamés - CV vs Oferta")

# Entradas
g.node("A1", "Texto CV")
g.node("A2", "Texto Oferta")

# Encoder compartido
g.node("B", "Embedding (128)", shape="box")
g.node("C", "Conv1D (64 filtros)", shape="box")
g.node("D", "BiLSTM (128x2)", shape="box")
g.node("E", "Max Pooling (256)", shape="box")
g.node("F", "Vector CV/Oferta", shape="box", style="filled", fillcolor="lightgray")

# Similaridad
g.node("G", "Concatenación", shape="ellipse", fillcolor="khaki", style="filled")
g.node("H", "MLP + ReLU + Dropout", shape="box", fillcolor="orange", style="filled")
g.node("I", "Output: Sigmoid\nScore de afinidad", shape="box", fillcolor="lightgreen", style="filled")

# Rama CV
g.edge("A1", "B", label="Encoder")
g.edge("B", "C")
g.edge("C", "D")
g.edge("D", "E")
g.edge("E", "F")

# Rama Oferta (idéntica)
g.edge("A2", "B", label="Encoder (compartido)", constraint="false")  # mismo encoder
g.edge("E", "F", constraint="false")  # indica convergencia

# Unión y salida
g.edge("F", "G")
g.edge("G", "H")
g.edge("H", "I")

# Renderiza
g.render("arquitectura_red_siamesa", format="png", cleanup=True)
