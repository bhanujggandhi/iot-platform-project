# Deployement

**Must have files in the directory structure**

```
package-name.zip
├── package-name
├    ├── main.py*
├    ├── package.json*
├    ├── requirements.txt*
├    └── <anything>
└
```

> `package-name.zip` must have a folder named `package-name` in which specified files are **must**.

> SAMPLE commands to copy repo to VM:
    scp -i /home/aakash/Downloads/Kafka-VM_key.pem -r /home/aakash/workdir/course_work/IAS/hack4/ias-iot-project/ azureuser@74.235.240.222:/home/azureuser/

> SAMPLE commands to connect to VM terminal:
    ssh -i /home/aakash/Downloads/Kafka-VM_key.pem azureuser@74.235.240.222 "cd ias-iot-project;sudo rm -r .git;cd Node-Manager;sudo apt install python3-pip;pip install -r requirements.txt;uvicorn main:app --reload;"

> to test node-manager service:
    -> ssh -i /home/aakash/Downloads/Kafka-VM_key.pem azureuser@74.235.240.222
    -> curl -X 'GET'   'http://127.0.0.1:8000/init'   -H 'accept: application/json';



