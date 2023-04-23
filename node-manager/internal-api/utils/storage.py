import os
from azure.storage.blob import BlobServiceClient
from decouple import config

AZURE_STORAGE_CONNECTION_STRING = config("AZURE_STORAGE_CONNECTION_STRING")


# Getting Container Name
def getContainer(containerName):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )
    except:
        return {"status": False, "message": "Network Error"}

    try:
        container_client = blob_service_client.create_container(containerName)
    except:
        try:
            container_client = blob_service_client.get_container_client(
                container=containerName
            )
        except:
            return {"status": False, "message": "Network Error"}
    return {
        "status": True,
        "blob_service_client": blob_service_client,
        "container_client": container_client,
    }


# Upload File to Azure Storage
def uploadFile(containerName, sourcePath, localFileName):
    resp = getContainer(containerName)
    if resp["status"] == False:
        return resp

    blob_service_client = resp["blob_service_client"]
    container_client = resp["container_client"]

    try:
        upload_file_path = os.path.join(sourcePath, localFileName)
        blob_client = blob_service_client.get_blob_client(
            container=containerName, blob=localFileName
        )
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)
        return {
            "status": True,
            "message": f"File {localFileName} uploaded successfully",
        }
    except:
        return {"status": False, "message": "Network Error"}


# Download File from Azure Storage
def downloadFile(containerName, serverFileName, destinationPath):
    resp = getContainer(containerName)
    if resp["status"] == False:
        return resp

    blob_service_client = resp["blob_service_client"]
    container_client = resp["container_client"]

    try:
        download_file_path = os.path.join(destinationPath, serverFileName)
        blob_client = blob_service_client.get_blob_client(
            container=containerName, blob=serverFileName
        )
        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        return {
            "status": True,
            "message": f"File {serverFileName} downloaded successfully",
        }
    except:
        return {"status": False, "message": "Network Error"}


# Delete File from Azure Storage
def deleteFile(containerName, fileName):
    resp = getContainer(containerName)
    if resp["status"] == False:
        return resp

    blob_service_client = resp["blob_service_client"]
    container_client = resp["container_client"]

    try:
        blob_client = blob_service_client.get_blob_client(
            container=containerName, blob=fileName
        )
        blob_client.delete_blob()
        return {"status": True, "message": f"File {fileName} deleted successfully"}
    except:
        return {"status": False, "message": "Network Error"}


# List Files in storage
def listFiles(containerName):
    resp = getContainer(containerName)
    if resp["status"] == False:
        return resp

    blob_service_client = resp["blob_service_client"]
    container_client = resp["container_client"]

    try:
        blob_list = container_client.list_blobs()
        fileList = [blob.name for blob in blob_list]
        return {"status": True, "file_list": fileList}
    except:
        return {"status": False, "message": "Network Error"}


# Sample Driver Code
if __name__ == "__main__":
    containerName = "apps"
    downloadFilePath = "."
    uploadFilePath = "."
    fileNames = ["validate.py"]

    # upload and list file
    for fileName in fileNames:
        resp = uploadFile(containerName, uploadFilePath, fileName)
        if resp["status"] == False:
            print(resp["message"])
        else:
            print(resp["message"])

        print("---------------LIST FILES------------------------")

        resp = listFiles(containerName)
        if resp["status"] == False:
            print(resp["message"])
        else:
            print(resp["fileList"])

        print("-------------------------------------------")

    # # download files
    # for fileName in fileNames :
    #     resp = downloadFile(containerName, fileName, downloadFilePath)
    #     if(resp['status'] == False) :
    #         print(resp['message'])
    #     else :
    #         print(resp['message'])

    #     print('-------------------------------------------')

    # # delete and list file
    # for fileName in fileNames :
    #     resp = deleteFile(containerName, fileName)
    #     if(resp['status'] == False) :
    #         print(resp['message'])
    #     else :
    #         print(resp['message'])

    #     print('---------------LIST FILES------------------------')

    #     resp = listFiles(containerName)
    #     if(resp['status'] == False) :
    #         print(resp['message'])
    #     else :
    #         print(resp['fileList'])

    #     print('-------------------------------------------')
