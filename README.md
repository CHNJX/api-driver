# api-driver
### 项目介绍
  - api-driver是一个的接口测试框架，项目架构采取了api-object设计模式，将用例和接口定义进行分离
  - 设计初衷：
      1. 统一的项目架构可以更好地支持团队协作以及日后的维护
      2. 提供便捷的功能让用例编写更加简单和高效
  - 目前实现：
      1. 一建生成接口测试项目
      2. swagger接口文档
      3. har生成测试用例
      4. 快速运行并集成测试报告
      
### 安装
  ```shell
  pip install apidriver
  ```

### 使用
安装完成后会得到一个命令行工具：adf
具体使用方法：
```
# 获取帮助
adf --help:
Usage: adf [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  har2case       将har转换成用例
  run            运行用例并集成allure报告
  start_project  创建项目
  swagger2api    swagger文档转换成api-object


# 生成接口测试项目
Usage: adf start_project [OPTIONS]

  创建项目 :param project_name: 项目名称

Options:
  -n, --project-name TEXT  project name  [required]
  --help                   Show this message and exit.
  
示例：
adf start_project -n "project_name"
会在当前目录下生成一个项目：
project_name:.
├───api_object
├───har
├───swagger
└───testcase

# swagger 生成 api-object
Usage: adf swagger2api [OPTIONS]

  swagger文档转换成api-object :param swagger_doc: swagger.json 文件 :param api_dir:
  api存放路径 非必填

Options:
  -s, --swagger-doc TEXT  Swagger doc file.  [required]
  -d, --api-dir TEXT      api save dir.
  --help                  Show this message and exit.

示例：
adf swagger2api -s swagger.json
会在api-object路径下生成对应的api模块

# har转测试用例
Usage: adf har2case [OPTIONS]

  将har转换成用例 :param har: har文件路径 :param api: har对应api-object文件 :param testcase:
  用例路径 :param exclude:  过来的url :return:

Options:
  -h, --har TEXT       har file path  [required]
  -a, --api TEXT       api object dir
  -t, --testcase TEXT  testcase dir
  -e, --exclude TEXT   exclude url
  --help               Show this message and exit.

示例
adf har2case -h har_file_dir -e "png|js|css"
会将har转成测试用例放在testcase目录下 并将 png/js/css结尾的路径给剔除
adf har2case -h har_file_dir -a api_object
api_object目录下查找是否存在har对应api类并生成api-object模式的测试用例
```
api使用
```python
# 占位符替换
# 占位符使用${random(num)} 或 ${random(num1,num2)} 前面是生成字符串，后面的是生成范围内的数字
from api_driver.testcase_mixin import TestcaseMixin
# 替换字典中的占位符
TestcaseMixin().replace_formal_dict_2_actual(data_dict)
# 替换列表中的占位符
TestcaseMixin().replace_formal_list_2_actual(data_list)
# 替换字符串的占位符
TestcaseMixin().replace_formal_str_2_actual(data)

# 进行json_schema的校验
TestcaseMixin().assert_schema(res,schema_file_dir,schema_file)

# 假数据生成
from api_driver.utils.fake import Fake
Fake # 提供了丰富的假数据生成方法 
```

### 后续优化
1. 往基于模型测试的设计模式方向优化
2. 实现swagger导入生成基本测试用例
3. 提供更丰富的api
4. 集成mock功能

