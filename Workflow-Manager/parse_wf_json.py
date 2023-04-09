import json

def get_service_entry():
    new_service_entry = ""
    print("Hello")
    return new_service_entry

contract_file = "contract.json"
f = open(contract_file)
work_details = json.load(f)["custom_workflow"]

workflow_name = work_details["workflow_name"]
workflow_params_data = work_details["workflow_fn_parameters"]

workflow_params = " , ".join(x for x in workflow_params_data["param_name"])
# check for data types and the corresponding values -- later

service_req_list = []
op_add_list = []

for service_no, service in enumerate(work_details["service_list"]):
    service_name = service["service_name"]
    params_count = service["param_count"]
    service_op = service_name + "_op"

    if(len(service["params_list"]) != params_count):
        print("Parameter count do not match..!!")
        exit()
    
    args = ""

    for params in service["params_list"]:
        if(params["prev_service_output"] == "False"):
            args += (params["param_name"] + ',')
        else:
            val = params["param_name"].split('.')
            args += f'D["{val[0]}"]["{val[1]}"],'

    args = args[:-1]

    op_add_line = f'D["{service_name}"] = {service_op}'
    service_req_line = f'{service_op} = service_req("{service_name}", [{args}])'
    
    service_req_list.append(service_req_line)
    op_add_list.append(op_add_line)

    print(service_req_line)
    print(op_add_line)
    print("\n")


# write code lines to file
f = open("workflow_file.py","w")
f.write("from services import service_req\n")
f.write(f'def {workflow_name}({workflow_params}):\n')
f.write(f'\tD = dict()\n')

for i, service_call in enumerate(service_req_list):
    f.write(f'\t{service_call}\n')
    f.write(f'\t{op_add_list[i]}\n')
 
f.close()










    
    
    
    
