import requests

def enable_direct_link(access_token, file_id):
    url = "https://open-api.123pan.com/api/v1/direct-link/enable"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    body = {
        "fileID": file_id
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("直链空间已成功启用，文件夹名称:", data.get("filename"))
            else:
                print("请求失败，返回信息:", data.get("message"))
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
    except Exception as e:
        print("发生错误:", e)


def disable_direct_link(access_token, file_id):
    url = "https://open-api.123pan.com/api/v1/direct-link/disable"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    body = {
        "fileID": file_id
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("直链空间已成功禁用")
            else:
                print("请求失败，返回信息:", data.get("message"))
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
    except Exception as e:
        print("发生错误:", e)

def get_direct_link(access_token, file_id):
    url = "https://open-api.123pan.com/api/v1/direct-link/url"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    params = {
        "fileID": file_id
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                # 输出获取到的直链链接
                print("获取直链链接成功！直链链接:", data['data'].get("url"))
            else:
                print("请求失败，返回信息:", data.get("message"))
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
    except Exception as e:
        print("发生错误:", e)
