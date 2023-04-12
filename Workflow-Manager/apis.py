from fastapi import FastAPI
import os
import shutil
import json
import uvicorn
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

# templates = Jinja2Templates(directory="templates")

# @app.get("/upload")
# async def index(request: Request, response_class=HTMLResponse):
#     return templates.TemplateResponse("uploadfile.html", {"request": request})

# @app.post("/uploader")
# async def upload_file(file: UploadFile = File(...)):
#    if file.content_type != "application/json":
#       raise HTTPException(status_code=400, detail="File must be JSON.")

#    file_path = os.path.join("uploads", file.filename)
#    with open(file_path, "wb") as f:
#       contents = await file.read()
#       f.write(contents)

#    is_created = define_workflow(file_path)[0]
   
#    return {"Workflow created": is_created}

@app.post("/upload_file")
def upload_file(file: UploadFile):
    if file.content_type != "application/json":
        raise HTTPException(400, detail="Invalid file type")

    data=json.loads(file.file.read())
    is_created = define_workflow(data)[0]

    return {"success":1, "is_created":is_created}

@app.get("/foo")
def foo_api(inp1: int, inp2: str):
   data = {"key1": inp1, "key2" : inp2}
   return data

@app.get("/bar")
def bar_api(inp11: int, inp21: str):
   data = {"key11": inp11, "key21" : inp21}
   return data

@app.get("/foobar")
def foo_bar_api():
   data = {"msg":"Message from foobar"}
   return data


@app.get("/call_wf/{app_name}/{wf_name}")
def call_wf_api(app_name, wf_name):
   folder = "./workflow/"+app_name
   cmd = "python "+folder+"/"+wf_name+".py"
   j = os.system(cmd)
   if(j == 0):
    is_called = True
   else:
    is_called = False
   

   return {"success":is_called}


def define_workflow(contract_object):
    # f = open(contract_file)
    # work_details = json.load(f)["custom_workflow"]

    work_details = contract_object["custom_workflow"]
    app_name = work_details["app_name"] 

    if not os.path.exists('workflow/'+app_name):
       os.makedirs('workflow/'+app_name)
       shutil.copy("./workflow/services.py", "./workflow/"+app_name+"/services.py")
   
    workflow_name = work_details["workflow_name"]
    workflow_params_data = work_details["workflow_fn_parameters"]
    workflow_params_vals = workflow_params_data["param_vals"]
    workflow_params_dtype = workflow_params_data["param_dtype"]

    workflow_params = " , ".join(x for x in workflow_params_data["param_name"])
    # check for data types and the corresponding values -- later

    service_req_list = []
    op_add_list = []

    for service in work_details["service_list"]:
        service_name = service["service_name"]
        params_count = service["param_count"]
        service_op = service_name + "_op"

        if(len(service["params_list"]) != params_count):
            print("Parameter count do not match..!!")
            return (False, "")
        
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

        # print(service_req_line)
        # print(op_add_line)
        # print("\n")


    # write code lines to file
    folder = "./workflow/"+app_name
    f = open(folder+"/"+workflow_name+".py","w")

    f.write("from services import service_req\n")
    f.write(f'def {workflow_name}({workflow_params}):\n')
    f.write(f'\tD = dict()\n')

    for i, service_call in enumerate(service_req_list):
        f.write(f'\t{service_call}\n')
        f.write(f'\t{op_add_list[i]}\n')
    
    f.write("\n")
    f.write("if __name__ == '__main__':\n")
    
    arguments = ""
    for idx, val in enumerate(workflow_params_vals):
        if(workflow_params_dtype[idx] == "str"):    
            arguments += f"'{val}',"
        else:
            arguments += f"{val},"
    
    arguments = arguments[:-1]
    
    f.write(f"\t{workflow_name}({arguments})")

    f.close()

    return (True, workflow_name)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1",port=8000)