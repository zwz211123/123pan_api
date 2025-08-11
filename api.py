import json
import os
import time
import requests
from datetime import datetime

class PanAPI:
    def __init__(self, client_id=None, client_secret=None, token_file="./access.json"):
        """
        初始化123云盘API客户端
        
        参数:
            client_id: 客户端ID，如果为None则从token_file中读取
            client_secret: 客户端密钥，如果为None则从token_file中读取
            token_file: 凭证存储文件路径
        """
        self.token_file = token_file
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.expired_at = None
        
        # 尝试加载已有的access_token
        self.load_access_token()
        
        # 如果没有提供client_id和client_secret，尝试从token_file加载
        if not self.client_id or not self.client_secret:
            self._load_credentials()
    
    def _load_credentials(self):
        """从token_file加载client_id和client_secret"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    if "client_id" in data and "client_secret" in data:
                        self.client_id = data["client_id"]
                        self.client_secret = data["client_secret"]
            except Exception as e:
                print(f"加载凭证出错: {e}")
    
    def load_access_token(self):
        """
        检查access_token文件的有效性，返回有效的token或None
        """
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    access_token = data.get('access_token')
                    expired_at = data.get('expired_at')
                    
                    if access_token and expired_at:
                        # 检查token是否过期
                        if time.time() < time.mktime(time.strptime(expired_at, "%Y-%m-%d %H:%M:%S")):
                            self.access_token = access_token
                            self.expired_at = expired_at
                            return access_token
                        else:
                            print("Access Token 已过期，需要重新获取。")
                    else:
                        print("Access Token 数据不完整，需要重新获取。")
            except Exception as e:
                print(f"没有找到 Access Token 文件，需要获取 Token: {e}")
        
        return None
    
    def save_access_token(self, access_token, expired_at):
        """
        保存access_token到文件
        
        参数:
            access_token: 访问令牌
            expired_at: 过期时间
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.token_file)), exist_ok=True)
        
        # 读取现有数据
        data = {}
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
            except:
                pass
        
        # 更新token信息
        data['access_token'] = access_token
        data['expired_at'] = expired_at
        data['client_id'] = self.client_id
        data['client_secret'] = self.client_secret
        
        # 写入文件
        with open(self.token_file, 'w') as f:
            json.dump(data, f)
    
    def get_access_token(self):
        """
        获取access_token，如果已有且未过期则直接返回，否则重新获取
        
        返回:
            str: 成功返回access_token，失败返回None
        """
        # 如果已有有效token，直接返回
        if self.access_token and self.expired_at:
            if time.time() < time.mktime(time.strptime(self.expired_at, "%Y-%m-%d %H:%M:%S")):
                return self.access_token
        
        # 重新获取token
        url = "https://open-api.123pan.com/api/v1/access_token"
        headers = {
            "Platform": "open_platform"
        }
        body = {
            "clientID": self.client_id,
            "clientSecret": self.client_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    access_token = data['data'].get("accessToken")
                    expired_at = data['data'].get("expiredAt")
                    
                    # 格式化过期时间
                    expired_at_formatted_temo_1 = datetime.strptime(expired_at ,"%Y-%m-%dT%H:%M:%S%z")
                    expired_at_timestamp = expired_at_formatted_temo_1.timestamp()
                    expired_at_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expired_at_timestamp))
                    
                    print("请求成功！获取到 Access Token.")
                    print(f"Access Token: {access_token}")
                    print(f"过期时间: {expired_at_formatted}")
                    
                    # 保存token
                    self.access_token = access_token
                    self.expired_at = expired_at_formatted
                    self.save_access_token(access_token, expired_at_formatted)
                    
                    return access_token
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return None
    
    def ensure_token(self):
        """确保有有效的access_token，如果没有则获取新的"""
        if not self.access_token:
            self.access_token = self.get_access_token()
        return self.access_token
    
    # 直链相关API
    def enable_direct_link(self, file_id):
        """
        启用文件直链
        
        参数:
            file_id: 文件ID
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
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
                    print(f"直链空间已成功启用，文件名称: {data.get('filename')}")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    def disable_direct_link(self, file_id):
        """
        禁用文件直链
        
        参数:
            file_id: 文件ID
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
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
                    print(f"直链空间已成功禁用，文件名称: {data.get('filename')}")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    def get_direct_link(self, file_id):
        """
        获取文件直链
        
        参数:
            file_id: 文件ID
            
        返回:
            str: 成功返回直链URL，失败返回None
        """
        access_token = self.ensure_token()
        if not access_token:
            return None
            
        url = "https://open-api.123pan.com/api/v1/direct-link/get"
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
                    direct_link = data['data'].get("url")
                    print(f"成功获取直链: {direct_link}")
                    return direct_link
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return None
    
    # 文件管理相关API
    def get_file_list(self, parent_file_id=0, limit=100, search_data=None, search_mode=None, last_file_id=None):
        """
        获取文件列表
        
        参数:
            parent_file_id: 父文件夹ID，默认为0（根目录）
            limit: 每页文件数量，默认100，最大不超过100
            search_data: 搜索关键词
            search_mode: 搜索模式
            last_file_id: 上一页最后一个文件ID，用于分页
            
        返回:
            tuple: (file_list, last_file_id) 文件列表和最后一个文件ID，失败返回(None, None)
        """
        access_token = self.ensure_token()
        if not access_token:
            return None, None
            
        url = "https://open-api.123pan.com/api/v2/file/list"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"  # 确保大小写正确
        }
        
        params = {
            "parentFileID": parent_file_id,
            "limit": limit
        }
        
        if search_data is not None:
            params["searchData"] = search_data
        
        if search_mode is not None:
            params["searchMode"] = search_mode
        
        if last_file_id is not None:
            params["lastFileID"] = last_file_id
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if response.status_code == 200:
                last_file_id = data.get('data', {}).get('lastFileID')
                file_list = data.get('data', {}).get('fileList', [])
                
                print(f"文件列表: {len(file_list)} 个文件:")
                return file_list, last_file_id
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return None, None
    
    def get_file_detail(self, file_id):
        """
        获取文件详情
        
        参数:
            file_id: 文件ID
            
        返回:
            dict: 成功返回文件详情字典，失败返回None
        """
        access_token = self.ensure_token()
        if not access_token:
            return None
            
        url = "https://open-api.123pan.com/api/v1/file/info"
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
                    file_info = data.get('data')
                    return file_info
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return None
    
    def print_file_detail(self, file_id):
        """
        打印文件详情
        
        参数:
            file_id: 文件ID
            
        返回:
            bool: 成功返回True，失败返回False
        """
        file_info = self.get_file_detail(file_id)
        if file_info:
            print(f"文件ID: {file_info.get('fileID')}")
            print(f"文件名: {file_info.get('filename')}")
            print(f"文件类型: {'文件夹' if file_info.get('type') == 1 else '文件'}")
            print(f"文件大小: {file_info.get('size')} 字节")
            print(f"创建时间: {file_info.get('createTime')}")
            print(f"修改时间: {file_info.get('updateTime')}")
            return True
        return False
    
    def move_files(self, file_ids, target_parent_id):
        """
        移动文件
        
        参数:
            file_ids: 文件ID列表
            target_parent_id: 目标父文件夹ID
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
        url = "https://open-api.123pan.com/api/v1/file/move"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "fileIDs": file_ids,
            "parentFileID": target_parent_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print(f"文件移动成功")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    def rename_files(self, file_id, new_name):
        """
        重命名文件
        
        参数:
            file_id: 文件ID
            new_name: 新文件名
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
        url = "https://open-api.123pan.com/api/v1/file/rename"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "fileID": file_id,
            "filename": new_name
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print(f"文件重命名成功")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    def trash_files(self, file_ids):
        """
        将文件移至回收站
        
        参数:
            file_ids: 文件ID列表
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
        url = "https://open-api.123pan.com/api/v1/file/trash"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "fileIDs": file_ids
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print(f"文件已移至回收站")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    def delete_files(self, file_ids):
        """
        永久删除文件
        
        参数:
            file_ids: 文件ID列表
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
        url = "https://open-api.123pan.com/api/v1/file/delete"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "fileIDs": file_ids
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print(f"文件已永久删除")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    def recover_files(self, file_ids):
        """
        从回收站恢复文件
        
        参数:
            file_ids: 文件ID列表
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
        url = "https://open-api.123pan.com/api/v1/file/recover"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "fileIDs": file_ids
        }
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print(f"文件已从回收站恢复")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    # 分享相关API
    def get_share_list(self, limit=100, last_share_id=None):
        """
        获取分享列表
        
        参数:
            limit: 每页数量，默认100
            last_share_id: 上一页最后一个分享ID，用于分页
            
        返回:
            list: 成功返回分享列表，失败返回None
        """
        access_token = self.ensure_token()
        if not access_token:
            return None
            
        url = "https://open-api.123pan.com/api/v1/share/list"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        params = {
            "limit": limit
        }
        
        if last_share_id:
            params["lastShareId"] = last_share_id
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print("获取分享链接列表成功！")
                    return data['data'].get("shareList", [])
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return None
    
    def update_share_info(self, share_id_list, traffic_switch, traffic_limit_switch=None, traffic_limit=None):
        """
        更新分享信息
        
        参数:
            share_id_list: 分享ID列表
            traffic_switch: 流量开关（1: 关闭, 2: 打开）
            traffic_limit_switch: 流量限制开关（1: 关闭, 2: 打开）
            traffic_limit: 流量限制值（单位：字节）
            
        返回:
            bool: 成功返回True，失败返回False
        """
        access_token = self.ensure_token()
        if not access_token:
            return False
            
        url = "https://open-api.123pan.com/api/v1/share/update"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "shareIDs": share_id_list,
            "trafficSwitch": traffic_switch
        }
        
        if traffic_switch == 2 and traffic_limit_switch is not None:
            body["trafficLimitSwitch"] = traffic_limit_switch
            
            if traffic_limit_switch == 2 and traffic_limit is not None:
                body["trafficLimit"] = traffic_limit
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    print(f"分享信息更新成功")
                    return True
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return False
    
    def create_share_link(self, file_id_list, share_name, share_expire=7, share_pwd=None, traffic_switch=1, traffic_limit_switch=1, traffic_limit=None):
        """
        创建分享链接
        
        参数:
            file_id_list: 文件ID列表
            share_name: 分享名称
            share_expire: 分享有效期（天数，1/7/30/0表示永久）
            share_pwd: 分享密码，可选
            traffic_switch: 流量开关（1: 关闭, 2: 打开）
            traffic_limit_switch: 流量限制开关（1: 关闭, 2: 打开）
            traffic_limit: 流量限制值（单位：字节）
            
        返回:
            dict: 成功返回分享信息字典，失败返回None
        """
        access_token = self.ensure_token()
        if not access_token:
            return None
            
        url = "https://open-api.123pan.com/api/v1/share/create"
        headers = {
            "Authorization": access_token,
            "Platform": "open_platform"
        }
        body = {
            "fileIDs": file_id_list,
            "shareName": share_name,
            "shareExpire": share_expire,
            "trafficSwitch": traffic_switch
        }
        
        if share_pwd:
            body["sharePwd"] = share_pwd
            
        if traffic_switch == 2:
            body["trafficLimitSwitch"] = traffic_limit_switch
            
            if traffic_limit_switch == 2 and traffic_limit is not None:
                body["trafficLimit"] = traffic_limit
        
        try:
            response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    share_info = data.get('data')
                    print(f"分享创建成功")
                    print(f"分享ID: {share_info.get('shareID')}")
                    print(f"分享链接: {share_info.get('shareUrl')}")
                    print(f"分享密码: {share_info.get('sharePwd') or '无'}")
                    return share_info
                else:
                    print(f"请求失败，返回信息: {data.get('message')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"发生错误: {e}")
        
        return None
