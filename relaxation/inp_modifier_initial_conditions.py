import json

json_file_path = 'C:/Users/adam-jd1r2h3ttnmecz9/Desktop/arthur/Framework-Relaxation/relaxation/backend/model_config/data.json'
inp_source_path = 'C:/Users/adam-jd1r2h3ttnmecz9/Desktop/arthur/Framework-Relaxation/relaxation/backend/files/inp/ImplicitRelaxation.inp'
inp_output_path = 'C:/Users/adam-jd1r2h3ttnmecz9/Desktop/arthur/Framework-Relaxation/relaxation/backend/files/inp/ImplicitRelaxation_modified.inp'

with open(json_file_path, 'r') as f:
    data = json.load(f)

elements_data = data["BIGGER"]["elements"]

stress_lines = []
hardening_lines = []

for elem_id, props in elements_data.items():
    s = props["S"]
    pe = props["PE"]
    peeq = props["PEEQ"]

    str_line = f"ZOI-1.{elem_id}, {s[0]}, {s[2]}, {s[1]}, {s[4]}, 0., 0.\n"
    stress_lines.append(str_line)

    hard_line = f"ZOI-1.{elem_id}, {peeq}, 0., 0., 0., 0., 0., 0.\n"
    hardening_lines.append(hard_line)

with open(inp_source_path, 'r') as f_in, open(inp_output_path, 'w') as f_out:

    for line in f_in:
        if line.strip().upper().startswith("** PREDEFINED FIELDS"):
            f_out.write("*Initial Conditions, type=STRESS\n")
            f_out.writelines(stress_lines)
            
            f_out.write("*Initial Conditions, type=HARDENING\n")
            f_out.writelines(hardening_lines)
            
        f_out.write(line)

