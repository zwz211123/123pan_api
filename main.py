"""
Main entry point for 123Pan API CLI
"""

from api import PanAPI
from cli import MenuPrinter, ShareHandler, FileHandler, DirectLinkHandler


def main():
    """Main function - initialize API and start CLI loop"""
    # Create API instance, load credentials from access.json
    api = PanAPI(token_file="access.json")

    # Ensure we have a valid access token
    access_token = api.ensure_token()
    if not access_token:
        print("无法获取有效的Access Token，请检查凭证是否正确")
        return

    # Initialize menu printer and handlers
    menu = MenuPrinter()
    share_handler = ShareHandler(api)
    file_handler = FileHandler(api)
    direct_link_handler = DirectLinkHandler(api)

    # Main menu loop
    while True:
        menu.print_main_menu()
        choice = input("请输入选项 (0-3): ").strip()

        if choice == '0':
            print("感谢使用，再见！")
            break

        elif choice == '1':
            # Share functions submenu
            while True:
                menu.print_share_menu()
                share_choice = input("请输入选项 (0-3): ").strip()

                if share_choice == '0':
                    break
                elif share_choice == '1':
                    share_handler.get_share_list()
                elif share_choice == '2':
                    share_handler.update_share_info()
                elif share_choice == '3':
                    share_handler.create_share_link()
                else:
                    menu.print_error("无效选项，请重新输入")

        elif choice == '2':
            # File management submenu
            while True:
                menu.print_file_menu()
                file_choice = input("请输入选项 (0-7): ").strip()

                if file_choice == '0':
                    break
                elif file_choice == '1':
                    file_handler.get_file_list()
                elif file_choice == '2':
                    file_handler.view_file_detail()
                elif file_choice == '3':
                    file_handler.move_files()
                elif file_choice == '4':
                    file_handler.rename_file()
                elif file_choice == '5':
                    file_handler.trash_files()
                elif file_choice == '6':
                    file_handler.delete_files()
                elif file_choice == '7':
                    file_handler.recover_files()
                else:
                    menu.print_error("无效选项，请重新输入")

        elif choice == '3':
            # Direct link functions submenu
            while True:
                menu.print_direct_link_menu()
                direct_choice = input("请输入选项 (0-3): ").strip()

                if direct_choice == '0':
                    break
                elif direct_choice == '1':
                    direct_link_handler.enable_direct_link()
                elif direct_choice == '2':
                    direct_link_handler.disable_direct_link()
                elif direct_choice == '3':
                    direct_link_handler.get_direct_link()
                else:
                    menu.print_error("无效选项，请重新输入")

        else:
            menu.print_error("无效选项，请重新输入")


if __name__ == "__main__":
    main()
