"""
123Pan Cloud Storage API Client
Provides programmatic interface to 123Pan API
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ENDPOINTS,
    PLATFORM_HEADER,
    TOKEN_FILE_PATH,
    TOKEN_TIME_FORMAT,
    TOKEN_ISO_FORMAT,
    SUCCESS_CODE,
    DEFAULT_PAGE_LIMIT,
    DEFAULT_TIMEOUT,
)
from .exceptions import (
    APIError,
    NetworkError,
    TokenExpiredError,
    TokenNotFoundError,
    CredentialsError,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PanAPI:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, token_file: str = TOKEN_FILE_PATH) -> None:
        """
        初始化123云盘API客户端

        参数:
            client_id: 客户端ID，如果为None则从token_file中读取
            client_secret: 客户端密钥，如果为None则从token_file中读取
            token_file: 凭证存储文件路径

        Raises:
            CredentialsError: 如果无法获取客户端凭证
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

        # 验证凭证
        if not self.client_id or not self.client_secret:
            raise CredentialsError(
                "无法获取客户端凭证。请检查 access.json 文件或直接传入凭证"
            )

    def _load_credentials(self) -> None:
        """从token_file加载client_id和client_secret"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    if "client_id" in data and "client_secret" in data:
                        self.client_id = data["client_id"]
                        self.client_secret = data["client_secret"]
                        logger.debug("凭证已从文件加载")
            except json.JSONDecodeError as e:
                logger.error(f"凭证文件格式错误: {e}")
            except (IOError, OSError) as e:
                logger.error(f"读取凭证文件失败: {e}")

    def load_access_token(self) -> Optional[str]:
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
                        if time.time() < time.mktime(time.strptime(expired_at, TOKEN_TIME_FORMAT)):
                            self.access_token = access_token
                            self.expired_at = expired_at
                            logger.debug("已加载有效的 Access Token")
                            return access_token
                        else:
                            logger.info("Access Token 已过期，需要重新获取")
                    else:
                        logger.warning("Access Token 数据不完整，需要重新获取")
            except json.JSONDecodeError as e:
                logger.error(f"Token 文件格式错误: {e}")
            except (IOError, OSError) as e:
                logger.debug(f"未找到 Access Token 文件: {e}")

        return None

    def save_access_token(self, access_token: str, expired_at: str) -> None:
        """
        保存access_token到文件

        参数:
            access_token: 访问令牌
            expired_at: 过期时间
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(self.token_file)), exist_ok=True)

            # 读取现有数据
            data = {}
            if os.path.exists(self.token_file):
                try:
                    with open(self.token_file, 'r') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError, PermissionError):
                    pass

            # 更新token信息
            data['access_token'] = access_token
            data['expired_at'] = expired_at
            data['client_id'] = self.client_id
            data['client_secret'] = self.client_secret

            # 写入文件
            with open(self.token_file, 'w') as f:
                json.dump(data, f)
            logger.debug("Access Token 已保存")
        except (IOError, OSError) as e:
            logger.error(f"保存 Access Token 失败: {e}")

    def get_access_token(self) -> Optional[str]:
        """
        获取access_token，如果已有且未过期则直接返回，否则重新获取

        返回:
            str: 成功返回access_token，失败返回None

        Raises:
            NetworkError: 网络请求失败
            APIError: API 响应错误
        """
        # 如果已有有效token，直接返回
        if self.access_token and self.expired_at:
            if time.time() < time.mktime(time.strptime(self.expired_at, TOKEN_TIME_FORMAT)):
                return self.access_token

        # 重新获取token
        url = ENDPOINTS["access_token"]
        headers = {
            "Platform": PLATFORM_HEADER
        }
        body = {
            "clientID": self.client_id,
            "clientSecret": self.client_secret
        }

        try:
            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    raise APIError("API 响应格式错误", original_error=e)

                if data.get("code") == SUCCESS_CODE:
                    access_token = data['data'].get("accessToken")
                    expired_at = data['data'].get("expiredAt")

                    # 格式化过期时间
                    expired_at_formatted_temo_1 = datetime.strptime(expired_at, TOKEN_ISO_FORMAT)
                    expired_at_timestamp = expired_at_formatted_temo_1.timestamp()
                    expired_at_formatted = time.strftime(TOKEN_TIME_FORMAT, time.localtime(expired_at_timestamp))

                    logger.info("成功获取 Access Token")
                    logger.debug(f"Access Token: {access_token}")

                    # 保存token
                    self.access_token = access_token
                    self.expired_at = expired_at_formatted
                    self.save_access_token(access_token, expired_at_formatted)

                    return access_token
                else:
                    raise APIError(
                        data.get('message', '获取 Access Token 失败'),
                        code=data.get('code'),
                        status_code=response.status_code,
                        response_data=data
                    )
            else:
                raise APIError(
                    f"请求失败，状态码: {response.status_code}",
                    status_code=response.status_code
                )

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)

    def ensure_token(self) -> Optional[str]:
        """确保有有效的access_token，如果没有则获取新的"""
        if not self.access_token:
            try:
                self.access_token = self.get_access_token()
            except (NetworkError, APIError) as e:
                logger.error(f"获取 Access Token 失败: {e}")
                return None
        return self.access_token

    def _handle_request_exceptions(self, exception: Exception) -> None:
        """处理请求异常并记录日志"""
        if isinstance(exception, requests.exceptions.ConnectionError):
            raise NetworkError(f"网络连接失败: {exception}", original_error=exception)
        elif isinstance(exception, requests.exceptions.Timeout):
            raise NetworkError(f"请求超时: {exception}", original_error=exception)
        elif isinstance(exception, requests.exceptions.RequestException):
            raise NetworkError(f"请求失败: {exception}", original_error=exception)
        elif isinstance(exception, json.JSONDecodeError):
            raise APIError("API 响应格式错误", original_error=exception)
        else:
            raise APIError(f"未知错误: {exception}", original_error=exception)

    # 直链相关API
    def enable_direct_link(self, file_id: int) -> bool:
        """
        启用文件直链

        参数:
            file_id: 文件ID

        返回:
            bool: 成功返回True，失败返回False

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["direct_link_enable"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        body = {
            "fileID": file_id
        }

        try:
            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == SUCCESS_CODE:
                    logger.info(f"直链空间已成功启用，文件名称: {data.get('filename')}")
                    return True
                else:
                    raise APIError(
                        data.get('message', '启用直链失败'),
                        code=data.get('code')
                    )
            else:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def disable_direct_link(self, file_id: int) -> bool:
        """
        禁用文件直链

        参数:
            file_id: 文件ID

        返回:
            bool: 成功返回True，失败返回False

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["direct_link_disable"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        body = {
            "fileID": file_id
        }

        try:
            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == SUCCESS_CODE:
                    logger.info(f"直链空间已成功禁用，文件名称: {data.get('filename')}")
                    return True
                else:
                    raise APIError(
                        data.get('message', '禁用直链失败'),
                        code=data.get('code')
                    )
            else:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def get_direct_link(self, file_id: int) -> str:
        """
        获取文件直链

        参数:
            file_id: 文件ID

        返回:
            str: 成功返回直链URL

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["direct_link_get"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        params = {
            "fileID": file_id
        }

        try:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == SUCCESS_CODE:
                    direct_link = data['data'].get("url")
                    logger.info(f"成功获取直链: {direct_link}")
                    return direct_link
                else:
                    raise APIError(
                        data.get('message', '获取直链失败'),
                        code=data.get('code')
                    )
            else:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    # 文件管理相关API
    def get_file_list(
        self,
        parent_file_id: int = 0,
        limit: int = DEFAULT_PAGE_LIMIT,
        search_data: Optional[str] = None,
        search_mode: Optional[str] = None,
        last_file_id: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[int]]:
        """
        获取文件列表

        参数:
            parent_file_id: 父文件夹ID，默认为0（根目录）
            limit: 每页文件数量，默认100，最大不超过100
            search_data: 搜索关键词
            search_mode: 搜索模式
            last_file_id: 上一页最后一个文件ID，用于分页

        返回:
            tuple: (file_list, last_file_id) 文件列表和最后一个文件ID

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["file_list"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
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
            response = requests.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '获取文件列表失败'),
                    code=data.get('code')
                )

            file_list = data.get('data', {}).get('fileList', [])
            last_file_id = data.get('data', {}).get('lastFileID')

            # Debug: Log the raw file list to identify field names
            if file_list:
                logger.debug(f"Sample file data: {json.dumps(file_list[0], ensure_ascii=False)}")

            logger.info(f"获取文件列表成功: {len(file_list)} 个文件")
            return file_list, last_file_id

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def get_file_detail(self, file_id: int) -> Dict[str, Any]:
        """
        获取文件详情

        参数:
            file_id: 文件ID

        返回:
            dict: 成功返回文件详情字典

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["file_info"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        params = {
            "fileID": file_id
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '获取文件详情失败'),
                    code=data.get('code')
                )

            file_info = data.get('data')
            logger.info(f"成功获取文件详情: {file_info.get('filename', 'Unknown')}")
            return file_info

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

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
            print(f"文件ID: {file_info.get('fileId')}")
            print(f"文件名: {file_info.get('filename')}")
            print(f"文件类型: {'文件夹' if file_info.get('type') == 1 else '文件'}")
            print(f"文件大小: {file_info.get('size')} 字节")
            print(f"创建时间: {file_info.get('createAt')}")
            print(f"修改时间: {file_info.get('updateAt')}")
            return True
        return False

    def move_files(self, file_ids: List[int], target_parent_id: int) -> bool:
        """
        移动文件

        参数:
            file_ids: 文件ID列表
            target_parent_id: 目标父文件夹ID

        返回:
            bool: 成功返回True

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["file_move"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        body = {
            "fileIDs": file_ids,
            "parentFileID": target_parent_id
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '文件移动失败'),
                    code=data.get('code')
                )

            logger.info("文件移动成功")
            return True

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def rename_files(self, file_id: int, new_name: str) -> bool:
        """
        重命名文件

        参数:
            file_id: 文件ID
            new_name: 新文件名

        返回:
            bool: 成功返回True

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["file_rename"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        body = {
            "fileID": file_id,
            "filename": new_name
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '文件重命名失败'),
                    code=data.get('code')
                )

            logger.info("文件重命名成功")
            return True

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def trash_files(self, file_ids: List[int]) -> bool:
        """
        将文件移至回收站

        参数:
            file_ids: 文件ID列表

        返回:
            bool: 成功返回True

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["file_trash"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        body = {
            "fileIDs": file_ids
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '文件移至回收站失败'),
                    code=data.get('code')
                )

            logger.info("文件已移至回收站")
            return True

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def delete_files(self, file_ids: List[int]) -> bool:
        """
        永久删除文件

        参数:
            file_ids: 文件ID列表

        返回:
            bool: 成功返回True

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["file_delete"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        body = {
            "fileIDs": file_ids
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '文件永久删除失败'),
                    code=data.get('code')
                )

            logger.info("文件已永久删除")
            return True

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def recover_files(self, file_ids: List[int]) -> bool:
        """
        从回收站恢复文件

        参数:
            file_ids: 文件ID列表

        返回:
            bool: 成功返回True

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["file_recover"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        body = {
            "fileIDs": file_ids
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '文件恢复失败'),
                    code=data.get('code')
                )

            logger.info("文件已从回收站恢复")
            return True

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    # 分享相关API
    def get_share_list(self, limit: int = DEFAULT_PAGE_LIMIT, last_share_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取分享列表

        参数:
            limit: 每页数量，默认100
            last_share_id: 上一页最后一个分享ID，用于分页

        返回:
            dict: 成功返回分享数据字典

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["share_list"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
        }
        params = {
            "limit": limit
        }

        if last_share_id:
            params["lastShareId"] = last_share_id

        try:
            response = requests.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '获取分享列表失败'),
                    code=data.get('code')
                )

            logger.info("获取分享链接列表成功")
            return data['data']

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def update_share_info(
        self,
        share_id_list: List[int],
        traffic_switch: int,
        traffic_limit_switch: Optional[int] = None,
        traffic_limit: Optional[int] = None
    ) -> bool:
        """
        更新分享信息

        参数:
            share_id_list: 分享ID列表
            traffic_switch: 流量开关（1: 关闭, 2: 打开）
            traffic_limit_switch: 流量限制开关（1: 关闭, 2: 打开）
            traffic_limit: 流量限制值（单位：字节）

        返回:
            bool: 成功返回True

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["share_update"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
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
            response = requests.post(url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '分享信息更新失败'),
                    code=data.get('code')
                )

            logger.info("分享信息更新成功")
            return True

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)

    def create_share_link(
        self,
        file_id_list: List[int],
        share_name: str,
        share_expire: int = 7,
        share_pwd: Optional[str] = None,
        traffic_switch: int = 1,
        traffic_limit_switch: int = 1,
        traffic_limit: Optional[int] = None
    ) -> Dict[str, Any]:
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
            dict: 成功返回分享信息字典

        Raises:
            TokenExpiredError: 访问令牌过期
            NetworkError: 网络连接失败
            APIError: API 请求失败
        """
        access_token = self.ensure_token()
        if not access_token:
            raise TokenExpiredError("无法获取访问令牌")

        url = ENDPOINTS["share_create"]
        headers = {
            "Authorization": access_token,
            "Platform": PLATFORM_HEADER
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
            response = requests.post(url, headers=headers, json=body, timeout=DEFAULT_TIMEOUT)

            if response.status_code != 200:
                raise APIError(f"HTTP {response.status_code}", status_code=response.status_code)

            data = response.json()

            if data.get("code") != SUCCESS_CODE:
                raise APIError(
                    data.get('message', '创建分享链接失败'),
                    code=data.get('code')
                )

            share_info = data.get('data')
            logger.info("分享创建成功")
            logger.info(f"分享ID: {share_info.get('shareID')}")
            logger.info(f"分享链接: {share_info.get('shareUrl')}")
            logger.info(f"分享密码: {share_info.get('sharePwd') or '无'}")
            return share_info

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"网络连接失败: {e}", original_error=e)
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"请求超时: {e}", original_error=e)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"请求失败: {e}", original_error=e)
        except json.JSONDecodeError as e:
            raise APIError("响应格式错误", original_error=e)
