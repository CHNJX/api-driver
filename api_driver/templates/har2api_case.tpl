from api_object.http import Http
from jsonpath import jsonpath
from testcase.test_base import TestBase
{%- for module in module_dir_list %}
from {{module}} import *
{%- endfor %}


class Test{{model_name}}(TestBase):

    def setup_class(self):
        self.http = Http()

    def test_{{case_name}}(self):
        self.logger.info('用例名称：{{case_name}}')
        {%- for step in testcase_steps %}
        self.logger.info('测试步骤：{{step['name']}}')
        {% if step['api_class'] and step['func_name'] %}
        request_data = {}
        {%- if step['request']['params'] %}
        request_data.update({{step['request']['params']}})
        {% endif %}
        {%- if step['request']['data'] %}
        request_data.update({{step['request']['data']}})
        {% endif %}
        {%- if step['request']['json'] %}
        request_data.update({{step['request']['json']}})
        {% endif %}
        resp = {{step['api_class']}}().{{step['func_name']}}(**request_data)
        {% else %}
        req_data = {
            "url": "{{step['request']['url']}}",
            "method": "{{step['request']['method']}}",
            {%- if step['request']['params'] %}
            'params': {{step['request']['params']}},
            {% endif %}
            {%- if step['request']['data'] %}
            'data': {{step['request']['data']}},
            {% endif %}
            {%- if step['request']['json'] %}
            'json': {{step['request']['json']}},
            {% endif %}
            {%- if step['request']['headers'] -%}
            'headers': {{step['request']['headers']}},
            {% endif -%}
        }
        resp = self.http.req(**req_data)
        {%- endif %}

        # 断言
        {% for valid in step['validate'] %}
        {%- for key,value in valid.items() -%}
        {%- if key=='equals' -%}
        assert resp['{{value[0]}}'] == {{value[1]}}
        {% else %}
        assert {{value[0]}} in "{{value[1]}}"
        {% endif %}
        {%- endfor -%}
        {%- endfor -%}

        {%- if step['header_validate'] -%}
        {% for valid in step['header_validate'] %}
        {%- for key,value in valid.items() -%}
        {%- if key=='equals' -%}
        assert resp['headers']['{{value[0]}}'] == "{{value[1]}}"
        {% else %}
        assert resp['headers']['{{value[0]}}'] == "{{value[1]}}"
        {% endif %}
        {%- endfor -%}
        {%- endfor -%}
        {% endif %}

        {%- if step['json_validate'] -%}
        {% for valid in step['json_validate'] %}
        {%- for key,value in valid.items() -%}
        {%- if key=='equals' -%}
        assert str(jsonpath(resp, '$..{{value[0]}}')[0]) == "{{value[1]}}"
        {% else %}
        assert str(jsonpath(resp, '$..{{value[0]}}')[0]) in "{{value[1]}}"
        {% endif %}
        {%- endfor -%}
        {%- endfor -%}
        {% endif %}
        {%- endfor -%}