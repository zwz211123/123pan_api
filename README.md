# 123pan_api 使用说明

## 项目介绍
这是一个重构后的123云盘API项目，将所有API请求集中到单一文件中，并优化了主文件的用户交互逻辑。项目保持了原有的凭证外部存储方式，使用更加简洁和易于维护。

## 文件结构
- `api.py`: 包含所有API请求的集中实现，以类的形式提供
- `main.py`: 主程序文件，提供用户友好的交互界面
- `access.json`: 存储client_id、client_secret和access_token的凭证文件

## 使用前准备
1. 确保已安装Python 3.x和requests库
2. 在`access.json`文件中填写您的client_id和client_secret
   ```json
   {
       "client_id": "您的client_id",
       "client_secret": "您的client_secret",
       "access_token": "",
       "expired_at": ""
   }
   ```
   注意：access_token和expired_at会在首次运行时自动获取和填充

## 使用方法
1. 运行主程序：
   ```
   python main.py
   ```

2. 按照菜单提示选择功能：
   - 分享功能：获取分享列表、更新分享信息、创建分享链接
   - 文件管理：获取文件列表、查看文件详情、移动文件、重命名文件等
   - 直链功能：启用/禁用文件直链、获取文件直链

## API类使用方法
如果您想在自己的程序中使用API类，可以这样导入和使用：

```python
from api import PanAPI

# 创建API实例
api = PanAPI(token_file="access.json")

# 确保有有效的access_token
access_token = api.ensure_token()

# 使用API功能
file_list, last_file_id = api.get_file_list(parent_file_id=0, limit=100)
```

## 主要功能
1. 文件管理
   - 获取文件列表
   - 查看文件详情
   - 移动文件
   - 重命名文件
   - 文件回收站操作

2. 分享功能
   - 获取分享列表
   - 更新分享信息
   - 创建分享链接

3. 直链功能
   - 启用文件直链
   - 禁用文件直链
   - 获取文件直链

## 注意事项
- 首次运行时会自动获取access_token并保存到access.json文件中
- access_token有效期通常为7天，过期后会自动重新获取
- 所有API请求都会进行错误处理并输出相应信息
