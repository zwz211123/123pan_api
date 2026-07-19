"""Main entry point for the 123Pan API CLI."""

from api import PanAPI
from api.exceptions import APIError, CredentialsError, NetworkError
from cli import DirectLinkHandler, FileHandler, MenuPrinter, ShareHandler, UploadHandler
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Initialize the API client and start the CLI loop."""
    try:
        api = PanAPI(token_file="access.json")
        if not api.ensure_token():
            logger.error("无法获取有效的 Access Token")
            print("错误：无法获取有效的 Access Token，请检查凭证是否正确")
            return
    except CredentialsError as exc:
        logger.error(f"凭证错误: {exc}")
        print(f"错误：凭证无效 - {exc}")
        return
    except NetworkError as exc:
        logger.error(f"网络错误: {exc}")
        print(f"错误：网络连接失败 - {exc}")
        return
    except APIError as exc:
        logger.error(f"API 错误: {exc}")
        print(f"错误：API 请求失败 - {exc}")
        return
    except Exception as exc:
        logger.exception("初始化失败")
        print(f"错误：初始化失败 - {exc}")
        return

    menu = MenuPrinter()
    share_handler = ShareHandler(api)
    file_handler = FileHandler(api)
    direct_link_handler = DirectLinkHandler(api)
    upload_handler = UploadHandler(api)

    while True:
        menu.print_main_menu()
        choice = input("请输入选项 (0-4): ").strip()

        if choice == "0":
            print("感谢使用，再见！")
            break
        if choice == "1":
            while True:
                menu.print_share_menu()
                subchoice = input("请输入选项 (0-3): ").strip()
                if subchoice == "0":
                    break
                actions = {
                    "1": share_handler.get_share_list,
                    "2": share_handler.update_share_info,
                    "3": share_handler.create_share_link,
                }
                action = actions.get(subchoice)
                action() if action else menu.print_error("无效选项，请重新输入")
        elif choice == "2":
            while True:
                menu.print_file_menu()
                subchoice = input("请输入选项 (0-7): ").strip()
                if subchoice == "0":
                    break
                actions = {
                    "1": file_handler.get_file_list,
                    "2": file_handler.view_file_detail,
                    "3": file_handler.move_files,
                    "4": file_handler.rename_file,
                    "5": file_handler.trash_files,
                    "6": file_handler.delete_files,
                    "7": file_handler.recover_files,
                }
                action = actions.get(subchoice)
                action() if action else menu.print_error("无效选项，请重新输入")
        elif choice == "3":
            while True:
                menu.print_direct_link_menu()
                subchoice = input("请输入选项 (0-3): ").strip()
                if subchoice == "0":
                    break
                actions = {
                    "1": direct_link_handler.enable_direct_link,
                    "2": direct_link_handler.disable_direct_link,
                    "3": direct_link_handler.get_direct_link,
                }
                action = actions.get(subchoice)
                action() if action else menu.print_error("无效选项，请重新输入")
        elif choice == "4":
            while True:
                menu.print_upload_menu()
                subchoice = input("请输入选项 (0-2): ").strip()
                if subchoice == "0":
                    break
                actions = {
                    "1": upload_handler.upload_file,
                    "2": upload_handler.create_directory,
                }
                action = actions.get(subchoice)
                action() if action else menu.print_error("无效选项，请重新输入")
        else:
            menu.print_error("无效选项，请重新输入")


if __name__ == "__main__":
    main()
