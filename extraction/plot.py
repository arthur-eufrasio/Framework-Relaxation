import json
import matplotlib.pyplot as plt
import numpy as np

def plot_element_stress_s11(file_path):
    with open(file_path, 'r') as f:
        raw_data = json.load(f)

    data = raw_data.get('BIGGER', raw_data)
    nodes_data = data['nodes']
    elements_data = data['elements']

    node_coords = {}
    for node_id, values in nodes_data.items():
        node_coords[int(node_id)] = (
            values['coords'][0],
            values['coords'][2]
        )

    centroids_x = []
    centroids_z = []
    s11_values = []

    for elem_id, values in elements_data.items():
        if 'S' in values and 'connectivity' in values:
            s11 = values['S'][0]
            elem_x = []
            elem_z = []
            valid_element = True
            for node_id in values['connectivity']:
                if node_id in node_coords:
                    x, z = node_coords[node_id]
                    elem_x.append(x)
                    elem_z.append(z)
                else:
                    valid_element = False
                    break
            
            if valid_element and elem_x:
                center_x = sum(elem_x) / len(elem_x)
                center_z = sum(elem_z) / len(elem_z)
                centroids_x.append(center_x)
                centroids_z.append(center_z)
                s11_values.append(s11)

    if not s11_values:
        print("No S11 data found to plot.")
        return

    min_val = min(s11_values)
    max_val = max(s11_values)
    levels = np.linspace(min_val, max_val, 11)

    plt.figure(figsize=(10, 6))

    contour = plt.tricontourf(
        centroids_x,
        centroids_z,
        s11_values,
        levels=levels,
        cmap='jet'
    )

    colorbar = plt.colorbar(contour, label='Stress S11 (Pa)', ticks=levels)
    colorbar.ax.set_yticklabels([f"{t:.6g}" for t in levels])
    
    plt.axis('equal')
    plt.title('2D Element Stress Contour (S11)')
    plt.xlabel('X Coordinate')
    plt.ylabel('Z Coordinate')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_element_stress_s11("C:\\Users\\adam-jd1r2h3ttnmecz9\\Desktop\\arthur\\EXTRACTIONEXPMODEL\\backend\\data\\datateste.json")