import requests

def get_file_list(access_token, parent_file_id, limit, search_data=None, search_mode=None, last_file_id=None):
    url = "https://open-api.123pan.com/api/v2/file/list"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"  # 确保大小写正确
    }

    params = {
        "parentFileId": parent_file_id,  # 文件夹ID，根目录传 0
        "limit": limit                    # 每页文件数量，最大不超过100
    }

    if search_data is not None:
        params["searchData"] = search_data
    if search_mode is not None:
        params["searchMode"] = search_mode
    if last_file_id is not None:
        params["lastFileId"] = last_file_id

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code == 200:
        last_file_id = data.get('data', {}).get('lastFileId')
        file_list = data.get('data', {}).get('fileList', [])

        print(f"文件列表: {len(file_list)} 个文件：")
        for file in file_list:
            # 解构文件信息
            file_id = file.get('fileId')
            filename = file.get('filename')
            file_type = '文件' if file['type'] == 0 else '文件夹'
            size = file.get('size', 0)
            etag = file.get('etag', '')
            status = file.get('status', 0)
            parent_file_id = file.get('parentFileId', 0)
            category = file.get('category', 0)

            # 打印文件信息
            print(f" 文件 ID: {file_id}, 文件名: {filename}, 类型: {file_type}, "
                  f"大小: {size} 字节, MD5: {etag}, 状态: {status}, "
                  f"目录 ID: {parent_file_id}, 分类: {category}")

        return last_file_id  # 返回最后一页文件ID
    else:
        print("获取文件列表失败，状态码:", response.status_code)
        print("响应内容:", data)
        return None

def get_file_detail(access_token, file_id):
    url = f"https://open-api.123pan.com/api/v1/file/detail?fileID={file_id}"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("code") == 0:
        return data.get("data")
    else:
        print("获取文件详情失败，状态码:", response.status_code)
        print("响应内容:", data)
        return None

def print_file_detail(file_detail):
    """ 打印文件详情 """
    if file_detail:
        file_id = file_detail.get('fileID')
        filename = file_detail.get('filename')
        file_type = '文件' if file_detail['type'] == 0 else '文件夹'
        size = file_detail.get('size', 0)
        etag = file_detail.get('etag', '')
        status = file_detail.get('status', 0)
        parent_file_id = file_detail.get('parentFileID', 0)
        create_at = file_detail.get('createAt', '')
        trashed = '是' if file_detail.get('trashed', 0) == 1 else '否'

        print("文件详情:")
        print(f" 文件 ID: {file_id}")
        print(f" 文件名: {filename}")
        print(f" 文件类型: {file_type}")
        print(f" 文件大小: {size} 字节")
        print(f" MD5: {etag}")
        print(f" 审核状态: {status}")
        print(f" 父级目录 ID: {parent_file_id}")
        print(f" 创建时间: {create_at}")
        print(f" 是否在回收站: {trashed}")
    else:
        print("未获取到文件信息。")

def move_files(access_token, file_ids, to_parent_file_id):
    url = "https://open-api.123pan.com/api/v1/file/move"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    body = {
        "fileIDs": file_ids,
        "toParentFileID": to_parent_file_id
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    if response.status_code == 200 and data.get("code") == 0:
        print("文件移动成功！")
    else:
        print("移动文件失败，状态码:", response.status_code)
        print("响应内容:", data)

def rename_files(access_token, rename_list):
    url = "https://open-api.123pan.com/api/v1/file/rename"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    body = {
        "renameList": rename_list
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    if response.status_code == 200 and data.get("code") == 0:
        print("文件重命名成功！")
    else:
        print("重命名文件失败，状态码:", response.status_code)
        print("响应内容:", data)

def trash_files(access_token, file_ids):
    url = "https://open-api.123pan.com/api/v1/file/trash"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    body = {
        "fileIDs": file_ids
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    if response.status_code == 200 and data.get("code") == 0:
        print("文件已移入回收站！")
    else:
        print("移入回收站失败，状态码:", response.status_code)
        print("响应内容:", data)

def delete_files(access_token, file_ids):
    url = "https://open-api.123pan.com/api/v1/file/delete"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    body = {
        "fileIDs": file_ids
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    if response.status_code == 200 and data.get("code") == 0:
        print("文件已彻底删除！")
    else:
        print("彻底删除文件失败，状态码:", response.status_code)
        print("响应内容:", data)

def recover_files(access_token, file_ids):
    url = "https://open-api.123pan.com/api/v1/file/recover"
    headers = {
        "Authorization": access_token,
        "Platform": "open_platform"
    }
    body = {
        "fileIDs": file_ids
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    if response.status_code == 200 and data.get("code") == 0:
        print("文件已成功恢复！")
    else:
        print("恢复文件失败，状态码:", response.status_code)
        print("响应内容:", data)