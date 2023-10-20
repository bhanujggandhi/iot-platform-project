# coding=utf-8
import random
import os
import requests
import json

server = "http://127.0.0.1:5089"


def create_ae(uri_cse, ae_name, ae_labels="", data_format="json"):
    """
    Method description:
    Create an application entity(AE) inside the OneM2M framework/tree
    under the specified CSE

    Parameters:
    uri_cse : [str] URI of parent CSE
    ae_name : [str] name of the AE
    data_format : [str] payload format
    """
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{};ty=2".format(data_format),
    }

    body = {
        "m2m:ae": {
            "rn": "{}".format(ae_name),
            "api": "acp_admin",
            "rr": "true",  # resource reachable from CSE
            "lbl": ae_labels,
        }
    }

    try:
        response = requests.post(uri_cse, json=body, headers=headers)
    except TypeError:
        response = requests.post(uri_cse, data=json.dumps(body), headers=headers)
    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))
    return


def create_cnt(uri_ae, cnt_name, cnt_labels="", data_format="json"):
    """
    Method description:
    Creates a container(CON) in the OneM2M framework/tree
    under the specified AE

    Parameters:
    uri_ae : [str] URI for the parent AE
    cnt_name : [str] name of the container (DESCRIPTOR/DATA)
    data_format : [str] body format
    """

    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{};ty=3".format(data_format),
    }

    body = {"m2m:cnt": {"rn": "{}".format(cnt_name), "mni": 12, "lbl": cnt_labels}}

    try:
        response = requests.post(uri_ae, json=body, headers=headers)
    except TypeError:
        response = requests.post(uri_ae, data=json.dumps(body), headers=headers)

    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))


def create_desc_cin(
    uri_desc_cnt, node_description, desc_cin_labels="", data_format="json"
):
    """
    Method description:
    Creates a descriptor content instance(desc_CIN) in the OneM2M framework/tree
    under the specified DESCRIPTOR CON

    This holds the detailed description for an specific AE

    Parameters:
    uri_desc_cnt : [str] URI for the parent DESCRIPTOR CON
    data_format : [str] payload format
    """

    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{};ty=4".format(data_format),
    }

    body = {
        "m2m:cin": {
            "cnf": "application/json",
            "con": node_description,
            "lbl": desc_cin_labels,
        }
    }

    try:
        response = requests.post(uri_desc_cnt, json=body, headers=headers)
    except TypeError:
        response = requests.post(uri_desc_cnt, data=json.dumps(body), headers=headers)
    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))


def create_data_cin(uri_cnt, value, cin_labels="", data_format="json"):
    """
    Method description:
    Deletes/Unregisters an application entity(AE) from the OneM2M framework/tree
    under the specified CSE

    Parameters:
    uri_cse : [str] URI of parent CSE
    ae_name : [str] name of the AE
    fmt_ex : [str] payload format
    """
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{};ty=4".format(data_format),
    }

    body = {"m2m:cin": {"con": "{}".format(value), "lbl": cin_labels, "cnf": "text"}}

    try:
        response = requests.post(uri_cnt, json=body, headers=headers)
    except TypeError:
        response = requests.post(uri_cnt, data=json.dumps(body), headers=headers)
    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))


def create_group(uri_cse, group_name, uri_list):
    """
    Method description:
    Creates an AE that groups various other specifies AEs in the OneM2M framework/tree
    under the specified DATA CON

    Parameters:
    uri : [str] URI for the parent DATA CON appended by "la" or "ol"
    fmt_ex : [str] payload format (json/XML)
    """

    headers = {"X-M2M-Origin": "admin:admin", "Content-type": "application/json;ty=9"}

    payload = {"m2m:grp": {"rn": group_name, "mt": 3, "mid": uri_list, "mnm": 10}}

    try:
        response = requests.post(uri_cse, json=payload, headers=headers)
    except TypeError:
        response = requests.post(uri_cse, data=json.dumps(payload), headers=headers)

    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))


##########################################################################################################


def get_data(uri, data_format="json"):
    """
    Method description:
    Deletes/Unregisters an application entity(AE) from the OneM2M framework/tree
    under the specified CSE

    Parameters:
    uri_cse : [str] URI of parent CSE
    ae_name : [str] name of the AE
    fmt_ex : [str] payload format
    """
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{}".format(data_format),
    }

    response = requests.get(uri, headers=headers)
    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))
    _resp = json.loads(response.text)
    # To get latest or oldest content instance
    return response.status_code, _resp["m2m:cin"]["con"]
    # return response.status_code, _resp["m2m:cnt"]#["con"] ## to get whole data of container (all content instances)


def get_group_data(uri, data_format="json"):
    """
    Method description:
    Deletes/Unregisters an application entity(AE) from the OneM2M framework/tree
    under the specified CSE

    Parameters:
    uri_cse : [str] URI of parent CSE
    ae_name : [str] name of the AE
    fmt_ex : [str] payload format
    """
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{}".format(data_format),
    }

    response = requests.get(uri, headers=headers)
    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))
    _resp = json.loads(response.text)
    # To get latest (entered data) instance
    return response.status_code, _resp["m2m:grp"]["lt"]


###########################################################################################################


def delete(uri, data_format="json"):
    """
    Method description:
    Deletes/Unregisters an application entity(AE) from the OneM2M framework/tree
    under the specified CSE

    Parameters:
    uri_cse : [str] URI of parent CSE
    ae_name : [str] name of the AE
    fmt_ex : [str] payload format
    """
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{}".format(data_format),
    }

    response = requests.delete(uri, headers=headers)
    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))
    return


###########################################################################################################


def discovery(uri="", data_format="json"):
    """
    Method description:
    Deletes/Unregisters an application entity(AE) from the OneM2M framework/tree
    under the specified CSE

    Parameters:
    uri_cse : [str] URI of parent CSE
    ae_name : [str] name of the AE
    fmt_ex : [str] payload format
    """
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-type": "application/{}".format(data_format),
    }

    response = requests.delete(uri, headers=headers)
    print("Return code : {}".format(response.status_code))
    print("Return Content : {}".format(response.text))
    _resp = json.loads(response.text)
    return response.status_code, _resp["m2m:uril"]


# ====================================================


if __name__ == "__main__":
    cse = "/~/in-cse/in-name/"
    # ------------------------------------------
    # Fill code here to create AE
    # specified by the URI
    # ------------------------------------------

    ae = "AE-DEV"
    lbl_ae = ["tds", "water_level", "water_density", "lux", "uv", "color"]
    create_ae(server + cse, ae, lbl_ae)

    node_container_name = "DEVICE-4"
    lbl_cnt = lbl_ae
    create_cnt(server + cse + ae, node_container_name, lbl_cnt)

    descriptor_container_name = "Descriptor"
    lbl_cnt = lbl_ae
    create_cnt(
        server + cse + ae + "/" + node_container_name,
        descriptor_container_name,
        lbl_cnt,
    )
    # create cnt in descriptor container
    for label in lbl_ae:
        val = ["TimeStamp", "Occupancy", "Value"]
        create_data_cin(
            server
            + cse
            + ae
            + "/"
            + node_container_name
            + "/"
            + descriptor_container_name,
            val,
            label,
        )

    data_container_name = "Data"
    lbl_cnt = lbl_ae
    create_cnt(
        server + cse + ae + "/" + node_container_name, data_container_name, lbl_cnt
    )
