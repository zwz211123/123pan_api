import requests

def get_share_list(access_token, limit, last_share_id=None):
    url = "https://open-api.123pan.com/api/v1/share/list"
    headers = {
        "Authorization": access_token,
        "platform": "open_platform"
    }
    params = {
        "limit": limit
    }

    if last_share_id:
        params['lastShareId'] = last_share_id

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("获取分享链接列表成功！")
                for share in data['data'].get("shareList", []):
                    print("  分享 ID:", share.get("shareId"))
                    print("  分享名称:", share.get("shareName"))
                    print("  分享码:", share.get("shareKey"))
                    print("  过期时间:", share.get("expiration"))
                    print("  是否失效:", "是" if share.get("expired") == 1 else "否")
                    print("  分享链接提取码:", share.get("sharePwd") or "无")
            else:
                print("请求失败，返回信息:", data.get("message"))
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
    except Exception as e:
        print("发生错误:", e)

def update_share_info(access_token, share_id_list, traffic_switch=None, traffic_limit_switch=None, traffic_limit=None):
    url = "https://open-api.123pan.com/api/v1/share/list/info"
    headers = {
        "Authorization": access_token,
        "platform": "open_platform"
    }
    body = {
        "shareIdList": share_id_list
    }

    if traffic_switch is not None:
        body['trafficSwitch'] = traffic_switch
    if traffic_limit_switch is not None:
        body['trafficLimitSwitch'] = traffic_limit_switch
    if traffic_limit is not None:
        body['trafficLimit'] = traffic_limit

    try:
        response = requests.put(url, headers=headers, json=body)
        if response.status_code == 200:
            print("请求成功！分享链接信息已更新。")
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
    except Exception as e:
        print("发生错误:", e)

def create_share_link(access_token, share_name, share_expire, file_id_list, share_pwd=None,
                      traffic_switch=None, traffic_limit_switch=None, traffic_limit=None):
    url = "https://open-api.123pan.com/api/v1/share/create"
    headers = {
        "Authorization": access_token,
        "platform": "open_platform"
    }
    body = {
        "shareName": share_name,
        "shareExpire": share_expire,
        "fileIDList": file_id_list
    }

    if share_pwd:
        body['sharePwd'] = share_pwd
    if traffic_switch:
        body['trafficSwitch'] = traffic_switch
    if traffic_limit_switch:
        body['trafficLimitSwitch'] = traffic_limit_switch
    if traffic_limit:
        body['trafficLimit'] = traffic_limit

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            data = response.json()
            print("请求成功！分享链接已创建。")
            print("分享ID:", data['shareID'])
            print("分享码:", data['shareKey'])
        else:
            print("请求失败，状态码:", response.status_code)
            print("响应内容:", response.text)
    except Exception as e:
        print("发生错误:", e)
