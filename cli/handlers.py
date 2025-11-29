"""
CLI event handlers for various operations
"""

from api import PanAPI
from api.exceptions import TokenExpiredError, NetworkError, APIError
from utils import PaginationIterator
from utils.logger import setup_logger
from .menu import MenuPrinter
from .input_parser import InputParser

logger = setup_logger(__name__)


class ShareHandler:
    """Handles share-related operations"""

    def __init__(self, api: PanAPI):
        """
        Initialize ShareHandler

        Args:
            api: PanAPI instance
        """
        self.api = api
        self.menu = MenuPrinter()
        self.parser = InputParser()

    def get_share_list(self) -> None:
        """Get and display share list with pagination"""
        try:
            limit = self.parser.prompt_positive_int(
                "请输入每页分享数量 (最大不超过100): ",
                max_val=100
            )
            limit = min(limit, 100)

            # Use pagination iterator with proper callback
            def print_shares(shares):
                for share in shares:
                    self.menu.print_share_info(share)

            paginator = PaginationIterator(
                api_method=self.api.get_share_list,
                initial_params={"limit": limit},
                page_key="lastShareId",
                items_key="shareList",
                callback=print_shares,
            )

            # Fetch all shares
            total = 0
            for share in paginator:
                total += 1

            if total == 0:
                self.menu.print_info("没有找到分享")
            else:
                self.menu.print_success(f"成功获取 {total} 个分享")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"获取分享失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in get_share_list")

    def update_share_info(self) -> None:
        """Update share information"""
        try:
            share_ids = self.parser.prompt_file_ids("请输入分享ID列表 (以逗号分隔): ")
            if not share_ids:
                self.menu.print_error("分享ID列表无效")
                return

            traffic_switch = self.parser.prompt_optional_int(
                "请输入免登录流量包开关 (1: 关闭, 2: 打开，可选，回车默认为1): ",
                default=1
            )

            traffic_limit_switch = None
            traffic_limit = None

            if traffic_switch == 2:
                traffic_limit_switch = self.parser.prompt_optional_int(
                    "请输入免登录流量限制开关 (1: 关闭, 2: 打开，可选，回车默认为1): ",
                    default=1
                )

                if traffic_limit_switch == 2:
                    traffic_limit = self.parser.prompt_optional_int(
                        "请输入免登录流量限制值 (单位：字节，可选，回车默认为0): ",
                        default=0
                    )

            self.api.update_share_info(
                share_ids,
                traffic_switch,
                traffic_limit_switch,
                traffic_limit
            )
            self.menu.print_success("分享信息更新成功")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"更新分享失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in update_share_info")

    def create_share_link(self) -> None:
        """Create new share link"""
        try:
            file_ids = self.parser.prompt_file_ids("请输入文件ID列表 (以逗号分隔): ")
            if not file_ids:
                self.menu.print_error("文件ID列表无效")
                return

            share_name = input("请输入分享链接名称: ").strip()
            if not share_name:
                self.menu.print_error("分享名称不能为空")
                return

            share_expire = self.parser.prompt_positive_int(
                "请输入分享链接有效期天数 (1, 7, 30, 0表示永久): "
            )

            share_pwd = self.parser.prompt_optional_string(
                "请输入分享链接提取码 (可选，回车跳过): "
            )

            traffic_switch = self.parser.prompt_optional_int(
                "请输入免登录流量包开关 (1: 关闭, 2: 打开，可选，回车默认为1): ",
                default=1
            )

            traffic_limit_switch = 1
            traffic_limit = None

            if traffic_switch == 2:
                traffic_limit_switch = self.parser.prompt_optional_int(
                    "请输入免登录流量限制开关 (1: 关闭, 2: 打开，可选，回车默认为1): ",
                    default=1
                )

                if traffic_limit_switch == 2:
                    traffic_limit = self.parser.prompt_optional_int(
                        "请输入免登录流量限制值 (单位：字节，可选，回车默认为0): ",
                        default=0
                    )

            share_info = self.api.create_share_link(
                file_ids,
                share_name,
                share_expire,
                share_pwd,
                traffic_switch,
                traffic_limit_switch,
                traffic_limit
            )
            self.menu.print_success("分享链接创建成功")
            print(f"分享ID: {share_info.get('shareID')}")
            print(f"分享链接: {share_info.get('shareUrl')}")
            print(f"分享密码: {share_info.get('sharePwd') or '无'}")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"创建分享链接失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in create_share_link")


class FileHandler:
    """Handles file management operations"""

    def __init__(self, api: PanAPI):
        """
        Initialize FileHandler

        Args:
            api: PanAPI instance
        """
        self.api = api
        self.menu = MenuPrinter()
        self.parser = InputParser()

    def get_file_list(self) -> None:
        """Get and display file list with pagination"""
        try:
            parent_file_id = self.parser.prompt_optional_int(
                "请输入父文件夹ID (默认为0，表示根目录): ",
                default=0
            )

            limit = self.parser.prompt_optional_int(
                "请输入每页文件数量 (最大不超过100): ",
                default=100
            )
            limit = min(limit, 100)

            search_data = self.parser.prompt_optional_string(
                "请输入搜索关键词 (可选，回车跳过): "
            )

            search_mode = self.parser.prompt_optional_string(
                "请输入搜索模式 (可选，回车跳过): "
            )

            # Use pagination iterator
            initial_params = {
                "parent_file_id": parent_file_id,
                "limit": limit,
                "search_data": search_data,
                "search_mode": search_mode,
            }

            def print_files(files):
                for file in files:
                    file_id = file.get('fileId')
                    filename = file.get('filename')
                    file_type = '文件夹' if file.get('type') == 0 else '文件'
                    size = file.get('size', 0)
                    etag = file.get('etag', '')

                    print(f"\n  文件ID: {file_id}")
                    print(f"  文件名: {filename}")
                    print(f"  类型: {file_type}")
                    print(f"  大小: {size} 字节")
                    print(f"  ETag: {etag}")

            paginator = PaginationIterator(
                api_method=self.api.get_file_list,
                initial_params=initial_params,
                page_key="lastFileID",
                items_key="fileList",
                callback=print_files,
            )

            # Fetch all files
            total = 0
            for file in paginator:
                total += 1

            if total == 0:
                self.menu.print_info("没有找到文件")
            else:
                self.menu.print_success(f"成功获取 {total} 个文件")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"获取文件列表失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in get_file_list")

    def view_file_detail(self) -> None:
        """View file details"""
        try:
            file_id = self.parser.prompt_positive_int("请输入文件ID: ")
            if file_id is None:
                self.menu.print_error("文件ID无效")
                return

            file_info = self.api.get_file_detail(file_id)
            self.menu.print_file_info(file_info)

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"获取文件详情失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in view_file_detail")

    def move_files(self) -> None:
        """Move files to another folder"""
        try:
            file_ids = self.parser.prompt_file_ids("请输入要移动的文件ID列表 (以逗号分隔): ")
            if not file_ids:
                self.menu.print_error("文件ID列表无效")
                return

            target_parent_id = self.parser.prompt_positive_int("请输入目标父文件夹ID: ")
            if target_parent_id is None:
                self.menu.print_error("目标文件夹ID无效")
                return

            self.api.move_files(file_ids, target_parent_id)
            self.menu.print_success("文件移动成功")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"移动文件失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in move_files")

    def rename_file(self) -> None:
        """Rename a file"""
        try:
            file_id = self.parser.prompt_positive_int("请输入文件ID: ")
            if file_id is None:
                self.menu.print_error("文件ID无效")
                return

            new_name = input("请输入新文件名: ").strip()
            if not new_name:
                self.menu.print_error("文件名不能为空")
                return

            self.api.rename_files(file_id, new_name)
            self.menu.print_success("文件重命名成功")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"重命名文件失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in rename_file")

    def trash_files(self) -> None:
        """Move files to trash"""
        try:
            file_ids = self.parser.prompt_file_ids(
                "请输入要移至回收站的文件ID列表 (以逗号分隔): "
            )
            if not file_ids:
                self.menu.print_error("文件ID列表无效")
                return

            self.api.trash_files(file_ids)
            self.menu.print_success("文件已移至回收站")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"移至回收站失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in trash_files")

    def delete_files(self) -> None:
        """Permanently delete files"""
        try:
            file_ids = self.parser.prompt_file_ids(
                "请输入要永久删除的文件ID列表 (以逗号分隔): "
            )
            if not file_ids:
                self.menu.print_error("文件ID列表无效")
                return

            # Confirm deletion
            confirm = input("确定要永久删除这些文件吗？(y/n): ").strip().lower()
            if confirm != 'y':
                self.menu.print_info("取消删除")
                return

            self.api.delete_files(file_ids)
            self.menu.print_success("文件已永久删除")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"删除文件失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in delete_files")

    def recover_files(self) -> None:
        """Recover files from trash"""
        try:
            file_ids = self.parser.prompt_file_ids(
                "请输入要从回收站恢复的文件ID列表 (以逗号分隔): "
            )
            if not file_ids:
                self.menu.print_error("文件ID列表无效")
                return

            self.api.recover_files(file_ids)
            self.menu.print_success("文件已从回收站恢复")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"恢复文件失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in recover_files")


class DirectLinkHandler:
    """Handles direct link operations"""

    def __init__(self, api: PanAPI):
        """
        Initialize DirectLinkHandler

        Args:
            api: PanAPI instance
        """
        self.api = api
        self.menu = MenuPrinter()
        self.parser = InputParser()

    def enable_direct_link(self) -> None:
        """Enable direct link for a file"""
        try:
            file_id = self.parser.prompt_positive_int("请输入文件ID: ")
            if file_id is None:
                self.menu.print_error("文件ID无效")
                return

            self.api.enable_direct_link(file_id)
            self.menu.print_success("直链已启用")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"启用直链失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in enable_direct_link")

    def disable_direct_link(self) -> None:
        """Disable direct link for a file"""
        try:
            file_id = self.parser.prompt_positive_int("请输入文件ID: ")
            if file_id is None:
                self.menu.print_error("文件ID无效")
                return

            self.api.disable_direct_link(file_id)
            self.menu.print_success("直链已禁用")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"禁用直链失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in disable_direct_link")

    def get_direct_link(self) -> None:
        """Get direct link for a file"""
        try:
            file_id = self.parser.prompt_positive_int("请输入文件ID: ")
            if file_id is None:
                self.menu.print_error("文件ID无效")
                return

            direct_link = self.api.get_direct_link(file_id)
            self.menu.print_success(f"直链: {direct_link}")

        except (TokenExpiredError, NetworkError, APIError) as e:
            self.menu.print_error(f"获取直链失败: {e}")
        except KeyboardInterrupt:
            self.menu.print_info("操作已取消")
        except Exception as e:
            self.menu.print_error(f"未知错误: {e}")
            logger.exception("Unexpected error in get_direct_link")
