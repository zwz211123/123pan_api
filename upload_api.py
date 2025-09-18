import hashlib
import os
import requests
from api import PanAPI

class UploadAPI(PanAPI):
    """
    继承PanAPI类，添加上传功能
    """

    def get_upload_domains(self):
        """
        获取上传域名

        返回:
            list: 成功返回上传域名列表，失败返回None
        """
        access_token = self.ensure_token()
        if not access_token:
            return None

        url = "https://open-api.123pan.com/upload/v2/file/domain"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    domains = data['data'].get('data', [])
                    print(f"获取上传域名成功")
                    return domains
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")

        return None

    def calculate_md5(self, file_path):
        """
        计算文件MD5值

        参数:
            file_path: 文件路径

        返回:
            str: MD5值
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"计算MD5失败: {e}")
            return None

    def upload_file(self, file_path, parent_file_id=0):
        """
        上传文件（单步上传，适用于小文件）

        参数:
            file_path: 本地文件路径
            parent_file_id: 父目录ID，默认为0（根目录）

        返回:
            int: 成功返回文件ID，失败返回None
        """
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None

        # 获取文件信息
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        print(f"准备上传文件: {filename}")
        print(f"文件大小: {file_size} 字节")

        # 检查文件大小限制（单步上传限制1GB）
        if file_size > 1024 * 1024 * 1024:
            print("文件过大，超过1GB限制")
            return None

        # 计算文件MD5
        print("正在计算文件MD5...")
        file_md5 = self.calculate_md5(file_path)
        if not file_md5:
            return None
        print(f"文件MD5: {file_md5}")

        # 使用正确的上传域名
        server_url = "http://openapi-upload.123242.com"
        print(f"使用上传域名: {server_url}")

        # 获取access token
        access_token = self.ensure_token()
        if not access_token:
            print("无法获取access token")
            return None

        # 单步上传
        print("开始上传文件...")
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            url = f"{server_url}/upload/v2/file/single/create"

            # 设置正确的headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Platform': 'open_platform'
            }

            files = {'file': (filename, file_data, 'application/octet-stream')}
            data = {
                'parentFileID': parent_file_id,
                'filename': filename,
                'etag': file_md5,
                'size': file_size
            }

            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)

            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                result_data = response.json()
                if result_data.get("code") == 0:
                    result = result_data.get('data')
                    if result and result.get('completed'):
                        file_id = result.get('fileID')
                        print(f"文件上传成功，文件ID: {file_id}")
                        return file_id
                    else:
                        print("上传未完成")
                        return None
                else:
                    print(f"上传失败: {result_data.get('message')}")
                    return None
            else:
                print(f"上传失败，HTTP状态码: {response.status_code}")
                return None

        except Exception as e:
            print(f"上传文件时发生错误: {e}")
            return None

    def create_directory(self, name, parent_id=0):
        """
        创建目录

        参数:
            name: 目录名称
            parent_id: 父目录ID，默认为0（根目录）

        返回:
            int: 成功返回目录ID，失败返回None
        """
        access_token = self.ensure_token()
        if not access_token:
            return None

        url = "https://open-api.123pan.com/api/v1/upload/v1/file/mkdir"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "name": name,
            "parentID": parent_id
        }

        try:
            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    dir_id = data['data'].get('dirID')
                    print(f"目录创建成功，目录ID: {dir_id}")
                    return dir_id
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")

        return None