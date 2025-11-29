"""
Menu printing utilities for CLI interface
"""


class MenuPrinter:
    """Handles printing of various menus for the CLI"""

    @staticmethod
    def print_main_menu():
        """Print main menu"""
        print("\n欢迎使用123云盘 API")
        print("1. 分享功能")
        print("2. 文件管理")
        print("3. 直链功能")
        print("0. 退出程序")

    @staticmethod
    def print_share_menu():
        """Print share functionality menu"""
        print("\n选择分享功能:")
        print("1. 获取分享列表")
        print("2. 更新分享信息")
        print("3. 创建分享链接")
        print("0. 返回主菜单")

    @staticmethod
    def print_file_menu():
        """Print file management menu"""
        print("\n选择文件管理功能:")
        print("1. 获取文件列表")
        print("2. 查看文件详情")
        print("3. 移动文件")
        print("4. 重命名文件")
        print("5. 将文件移至回收站")
        print("6. 永久删除文件")
        print("7. 从回收站恢复文件")
        print("0. 返回主菜单")

    @staticmethod
    def print_direct_link_menu():
        """Print direct link functionality menu"""
        print("\n选择直链功能:")
        print("1. 启用文件直链")
        print("2. 禁用文件直链")
        print("3. 获取文件直链")
        print("0. 返回主菜单")

    @staticmethod
    def print_file_info(file_info):
        """Print file information"""
        if file_info:
            print(f"  文件ID: {file_info.get('fileId')}")
            print(f"  文件名: {file_info.get('filename')}")
            print(f"  类型: {'文件夹' if file_info.get('type') == 1 else '文件'}")
            print(f"  文件大小: {file_info.get('size')} 字节")
            print(f"  创建时间: {file_info.get('createAt')}")
            print(f"  修改时间: {file_info.get('updateAt')}")

    @staticmethod
    def print_file_list(file_list, last_file_id=None):
        """Print file list"""
        if file_list:
            for file in file_list:
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

            if last_file_id is not None:
                print(f"\n最后一个文件ID: {last_file_id}")

    @staticmethod
    def print_share_info(share_info):
        """Print share information"""
        if share_info:
            print(f"\n  分享 ID: {share_info.get('shareId')}")
            print(f"  分享名称: {share_info.get('shareName')}")
            print(f"  分享码: {share_info.get('shareKey')}")
            print(f"  过期时间: {share_info.get('expiration')}")
            print(f"  是否失效: {'是' if share_info.get('expired') == 1 else '否'}")
            print(f"  分享链接提取码: {share_info.get('sharePwd') or '无'}")

    @staticmethod
    def print_success(message):
        """Print success message"""
        print(f"✓ {message}")

    @staticmethod
    def print_error(message):
        """Print error message"""
        print(f"✗ 错误: {message}")

    @staticmethod
    def print_warning(message):
        """Print warning message"""
        print(f"! 警告: {message}")

    @staticmethod
    def print_info(message):
        """Print info message"""
        print(f"ℹ {message}")
