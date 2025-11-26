"""
CLI event handlers for various operations
"""

from api import PanAPI
from utils import PaginationIterator
from .menu import MenuPrinter
from .input_parser import InputParser


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

    def get_share_list(self):
        """Get and display share list with pagination"""
        limit = self.parser.prompt_positive_int(
            "请输入每页分享数量 (最大不超过100): "
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

    def update_share_info(self):
        """Update share information"""
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

    def create_share_link(self):
        """Create new share link"""
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

        self.api.create_share_link(
            file_ids,
            share_name,
            share_expire,
            share_pwd,
            traffic_switch,
            traffic_limit_switch,
            traffic_limit
        )


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

    def get_file_list(self):
        """Get and display file list with pagination"""
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
                file_id = file.get('fileID')
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

    def view_file_detail(self):
        """View file details"""
        file_id = self.parser.prompt_positive_int("请输入文件ID: ")
        if file_id is None:
            self.menu.print_error("文件ID无效")
            return

        file_info = self.api.get_file_detail(file_id)
        if file_info:
            self.menu.print_file_info(file_info)
        else:
            self.menu.print_error("无法获取文件信息")

    def move_files(self):
        """Move files to another folder"""
        file_ids = self.parser.prompt_file_ids("请输入要移动的文件ID列表 (以逗号分隔): ")
        if not file_ids:
            self.menu.print_error("文件ID列表无效")
            return

        target_parent_id = self.parser.prompt_positive_int("请输入目标父文件夹ID: ")
        if target_parent_id is None:
            self.menu.print_error("目标文件夹ID无效")
            return

        self.api.move_files(file_ids, target_parent_id)

    def rename_file(self):
        """Rename a file"""
        file_id = self.parser.prompt_positive_int("请输入文件ID: ")
        if file_id is None:
            self.menu.print_error("文件ID无效")
            return

        new_name = input("请输入新文件名: ").strip()
        if not new_name:
            self.menu.print_error("文件名不能为空")
            return

        self.api.rename_files(file_id, new_name)

    def trash_files(self):
        """Move files to trash"""
        file_ids = self.parser.prompt_file_ids(
            "请输入要移至回收站的文件ID列表 (以逗号分隔): "
        )
        if not file_ids:
            self.menu.print_error("文件ID列表无效")
            return

        self.api.trash_files(file_ids)

    def delete_files(self):
        """Permanently delete files"""
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

    def recover_files(self):
        """Recover files from trash"""
        file_ids = self.parser.prompt_file_ids(
            "请输入要从回收站恢复的文件ID列表 (以逗号分隔): "
        )
        if not file_ids:
            self.menu.print_error("文件ID列表无效")
            return

        self.api.recover_files(file_ids)


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

    def enable_direct_link(self):
        """Enable direct link for a file"""
        file_id = self.parser.prompt_positive_int("请输入文件ID: ")
        if file_id is None:
            self.menu.print_error("文件ID无效")
            return

        self.api.enable_direct_link(file_id)

    def disable_direct_link(self):
        """Disable direct link for a file"""
        file_id = self.parser.prompt_positive_int("请输入文件ID: ")
        if file_id is None:
            self.menu.print_error("文件ID无效")
            return

        self.api.disable_direct_link(file_id)

    def get_direct_link(self):
        """Get direct link for a file"""
        file_id = self.parser.prompt_positive_int("请输入文件ID: ")
        if file_id is None:
            self.menu.print_error("文件ID无效")
            return

        self.api.get_direct_link(file_id)
