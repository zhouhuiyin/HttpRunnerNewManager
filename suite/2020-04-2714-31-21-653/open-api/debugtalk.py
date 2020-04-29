# debugtalk.py

import requests
import json
import base64
import hmac
import os
import random
import string
import time
import uuid
from datetime import datetime
from hashlib import sha1

BASE_URL = "https://api.yovole.com/v1"
EAST_BASE_URL = "https://cn-east-1.api.yovole.com/v1"
NORTH_BASE_URL = "https://cn-north-1.api.yovole.com/v1"

TIMESTAMP = ""
REQUESTID = ""
signature = ""
#REQUESTBODY = json.loads(request.body.decode('utf-8'))


def get_base_url(*region):
    if region:
        re = str(region[0])
        if re.strip() == "east":
            return EAST_BASE_URL
        elif re.strip() == "north":
            return NORTH_BASE_URL
    else:
        return BASE_URL


class RequestHeader(object):
    def __init__(self, app_id, secret_key, request_body_str, other_headers):
        self.encypt_algorithm = "YCS1-HMAC-SHA1"
        self.signed_headers = ""
        self.app_id = app_id
        self.secret_key = secret_key
        self.request_body_str = request_body_str
        self.other_headers = other_headers

    # 获取当前时间并转为 RFC_1123 格式
    def _current_time_ISO_8601(self):
        now = datetime.now()
        time_8601 = now.replace(microsecond=0).isoformat() + "Z"
        return time_8601

    def _random_uuid(self):
        request_id = uuid.uuid1()
        return request_id

    # CMP-API 请求签名
    def _base64_hmac_sha1(self, code, key, digestmod=sha1):
        hmac_code = hmac.new(key.encode(), code.encode(), digestmod).digest()
        return base64.b64encode(hmac_code).decode()

    def assemble_authorization(self):
        r_id = str(self._random_uuid())
        r_time = self._current_time_ISO_8601()

        # generate signature summary and signed header
        required_header = {"x-ycs-timestamp": r_time, "x-ycs-requestid": r_id, "requestBody": self.request_body_str}
        optional_header = self.other_headers
        auth_header = dict(required_header, **optional_header)
        s_keys = sorted(auth_header.keys())
        sign_params = ""
        count = 1
        for key in s_keys:
            sign_params = sign_params + key + "=" + auth_header[key]
            if key.strip() != "requestBody":
                self.signed_headers = self.signed_headers + key
            if count < len(s_keys):
                sign_params = sign_params + "&"
                if key.strip() != "requestBody":
                    self.signed_headers = self.signed_headers + ";"
                count += 1

        # generate encypt key
        e_key = self._base64_hmac_sha1(sign_params, self.secret_key)

        authorization = "Authorization: " + self.encypt_algorithm + " Credential=" + self.app_id + ",SignedHeaders=" + self.signed_headers + ",Signature=" + e_key

        auth_header.pop("requestBody")
        request_headers = dict(auth_header, **{"x-ycs-security-authorization": authorization})
        return request_headers


def get_request_header(id, key, body_json_str, o_headers={}):
    rh = RequestHeader(id, key, body_json_str, o_headers)
    headers = rh.assemble_authorization()
    return headers
    
# new way to get Signature info
def get_signature(id, key, body_json_str, o_headers={}):
    rh = RequestHeader(id, key, body_json_str, o_headers)
    headers = rh.assemble_authorization()
    TIMESTAMP = headers['x-ycs-timestamp']
    REQUESTID = headers['x-ycs-requestid']
    signature = headers['x-ycs-security-authorization']

def get_time_stamp():
    return TIMESTAMP

def get_requestid():
    return REQUESTID
    
def get_solved_signature():
    return signature


def get_default_request():
    return {
        "base_url": BASE_URL,
        "headers": {
            "content-type": "application/json"
        }
    }


def get_json_str(json_dict):
    return json.dumps(json_dict)


def get_json_dict(json_str):
    return json.loads(json_str)


def sum_two(m, n):
    return m + n


def sum_status_code(status_code, expect_sum):
    """ sum status code digits
        e.g. 400 => 4, 201 => 3
    """
    sum_value = 0
    for digit in str(status_code):
        sum_value += int(digit)

    assert sum_value == expect_sum


def is_status_code_200(status_code):
    return status_code == 200


os.environ["TEST_ENV"] = "PRODUCTION"


def skip_test_in_production_env():
    """ skip this test in production environment
    """
    return os.environ["TEST_ENV"] == "PRODUCTION"


def skip_test_comparation(expect, actual):
    if expect == actual:
        return True
    else:
        return False


def get_user_agent():
    return ["iOS/10.1", "iOS/10.2"]


def gen_app_version():
    return [
        {"app_version": "2.8.5"},
        {"app_version": "2.8.6"}
    ]


def get_account():
    return [
        {"username": "user1", "password": "111111"},
        {"username": "user2", "password": "222222"}
    ]


def get_account_in_tuple():
    return [("user1", "111111"), ("user2", "222222")]


def gen_random_string(str_len):
    random_char_list = []
    for _ in range(str_len):
        random_char = random.choice(string.ascii_letters + string.digits)
        random_char_list.append(random_char)

    random_string = ''.join(random_char_list)
    return random_string


def setup_hook_add_kwargs(request):
    request["key"] = "value"


def setup_hook_remove_kwargs(request):
    request.pop("key")


def teardown_hook_sleep_n_sec(n_secs):
    """ sleep n seconds after request
    """
    time.sleep(n_secs)


def teardown_hook_sleep_N_secs(response, n_secs):
    """ sleep n seconds after request
    """
    if response.status_code == 200:
        time.sleep(0.1)
    else:
        time.sleep(n_secs)


def hook_print(msg):
    print("print message: {}".format(msg))


def modify_request_json(request, os_platform):
    request["json"]["os_platform"] = os_platform


def alter_response(response):
    response.status_code = 500
    response.headers["Content-Type"] = "html/text"
    response.json["headers"]["Host"] = "127.0.0.1:8888"
    response.new_attribute = "new_attribute_value"
    response.new_attribute_dict = {
        "key": 123
    }


def get_msec():
    msec = datetime.now().strftime("%Y%m%d%H%M%S%f")[0:17]
    print("get millsecond is: {}".format(msec))
    return msec


def get_permission_num():
    p_num = random.randrange(1, 8, 2)
    print("get permission number: {}".format(p_num))
    return p_num


def str_to_dict(dict_str):
    return dict(dict_str)


def dict_to_str(c_dict):
    return str(c_dict)


def get_color_number():
    c_num = random.randint(1, 10)
    print("get color number: {}".format(c_num))
    return c_num


def contains_str(content, expect):
    content_str = str(content)
    expect_str = str(expect)
    assert expect_str in content_str


class LoopList(object):
    def __init__(self, id, key, base_url, api_path, project_id, name_or_sn):
        self.request_url = base_url + api_path
        self.project_id = project_id
        self.name_or_sn = name_or_sn
        self.loop_time = 6
        self.sleep_time = 10
        self.request_body = {"projectId": self.project_id, "nameOrSn": self.name_or_sn}
        print("self.request_body is {}".format(self.request_body))
        request_header = RequestHeader(id, key, json.dumps(self.request_body), {})
        self.headers = request_header.assemble_authorization()
        print("self.headers is {}".format(self.headers))

    def get_vm_status(self, status, response=None):
        while self.loop_time > 0:
            reg = requests.post(self.request_url, json=self.request_body, headers=self.headers)
            response_content = json.loads((reg.content).decode("utf-8"))
            print("response_content is : {}".format(response_content))
            page_data = response_content["pager"]["pageData"]
            self.loop_time -= 1
            time.sleep(self.sleep_time)
            if len(page_data) != 0:
                resource_attr = page_data[0]
                resource_status = resource_attr["status"]
                if resource_status.strip() == status.upper().strip():
                    print("vm is exist with status [{}].".format(resource_status))
                    break
                else:
                    print("vm is exist with status [{}].".format(resource_status))
                    continue
            else:
                print("vm is not exist.")
                continue

        else:
            response.status_code = 600
            print("response code is {}.".format(response.status_code))

    def get_resouce_status(self, response=None):
        while self.loop_time > 0:
            reg = requests.post(self.request_url, json=self.request_body, headers=self.headers)
            response_content = json.loads(reg.content)
            print("response_content is : {}".format(response_content))
            page_data = response_content["pager"]["pageData"]
            self.loop_time -= 1
            time.sleep(self.sleep_time)
            if len(page_data) != 0:
                resource_attr = page_data[0]
                resource_name = resource_attr["name"]
                if resource_name.strip() == self.name_or_sn:
                    print("resouce is created")
                    break
                else:
                    print("resource is created but not actived.")
                    continue
            else:
                print("resource is not created.")
                continue

        else:
            response.status_code = 600
            print("response code is {}.".format(response.status_code))


def get_create_volume_status(id, key, base_url, project_id, name_or_sn, response):
    api_path = "/volume/list"
    loop_status = LoopList(id, key, base_url, api_path, project_id, name_or_sn)
    loop_status.get_resouce_status(response)


def get_create_vm_status(id, key, base_url, project_id, name_or_sn, response):
    api_path = "/vm/list"
    loop_status = LoopList(id, key, base_url, api_path, project_id, name_or_sn)
    loop_status.get_vm_status("active", response)

def get_create_eip_status(id,key,base_url,project_id,name_or_sn,response):
    api_path = "/eip/list"
    loop_status = LoopList(id,key,base_url,api_path,project_id,name_or_sn)
    loop_status.get_vm_status("active",response)

def getresult(a,b):
    result = a+b
    return result
