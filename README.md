# 123pan_api 使用说明

## 项目介绍
这是一个完全重构的123云盘API项目，采用模块化设计，提供高度可维护的代码组织结构。项目分离了API逻辑、CLI界面、工具函数和配置，使得代码更加易于扩展和测试。

## 文件结构

```
123pan_api/
├── api/                          # API模块
│   ├── __init__.py              # 模块入口，导出公共接口
│   ├── pan_api.py               # 主API客户端类 (PanAPI)
│   └── exceptions.py            # 自定义异常定义
│
├── cli/                          # 命令行界面模块
│   ├── __init__.py              # 模块入口
│   ├── menu.py                  # 菜单打印和输出格式化
│   ├── input_parser.py          # 用户输入解析和验证
│   └── handlers.py              # 功能处理器类 (ShareHandler, FileHandler, DirectLinkHandler)
│
├── utils/                        # 工具函数模块
│   ├── __init__.py              # 模块入口
│   └── pagination.py            # 通用分页迭代器
│
├── tests/                        # 测试模块
│   ├── __init__.py
│   ├── test_input_parser.py     # 输入解析器测试
│   └── test_pagination.py       # 分页工具测试
│
├── config.py                     # 配置和常量定义
├── main.py                       # 主程序入口
├── requirements.txt              # 项目依赖
├── access.json                   # 凭证存储文件 (自动生成)
└── README.md                     # 项目文档
```

## 使用前准备
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

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

### 命令行界面
1. 运行主程序：
   ```bash
   python main.py
   ```

2. 按照菜单提示选择功能：
   - **分享功能**：获取分享列表、更新分享信息、创建分享链接
   - **文件管理**：获取文件列表、查看文件详情、移动文件、重命名文件、回收站操作
   - **直链功能**：启用/禁用文件直链、获取文件直链

### 编程接口
如果您想在自己的程序中使用API类，可以这样导入和使用：

```python
from api import PanAPI

# 创建API实例
api = PanAPI(token_file="access.json")

# 确保有有效的access_token
access_token = api.ensure_token()

# 使用API功能
file_list, last_file_id = api.get_file_list(parent_file_id=0, limit=100)

# 或者使用分页迭代器处理大量结果
from utils import PaginationIterator

paginator = PaginationIterator(
    api_method=api.get_file_list,
    initial_params={"parent_file_id": 0, "limit": 100},
    page_key="lastFileID",
    items_key="fileList"
)

for file in paginator:
    print(f"File: {file['filename']}")
```

### 运行测试
```bash
python -m unittest discover -s tests -p "test_*.py" -v
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
- access_token有效期为30天，过期后会自动重新获取
- 所有API请求都会进行错误处理并输出相应信息
