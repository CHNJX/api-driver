from api_object.http import Http


class {{ tag }}(Http):

    {%- for key,path in paths.items() %}

    def {{ path["name"] }}(self{{ path["params_list"].__len__() and ", " or "" }}{{ path["params_list"] | join(", ") }}):
        """
        {{path["desc"]}}
        {%- for param in path["parameters"] %}
        :param {{param["name"]}}: {{param["description"]}} {% if param["required"] -%}*{% endif %}
        {%- if loop.last %}
        {% endif %}
        {%- endfor -%}

        {%- for param_name in path["json"] %}
        :param {{param_name}}:
        {%- if loop.last %}
        {% endif %}
        {%- endfor %}
        """

        req_data = {
            "url": {% if path["url_param"] %}f"{{path["url"]}}/{ {{path["url_param"]}} }"{% else %}f"{{key}}"{% endif %},
            {%- if path["parameters"] %}
            "params": {
                {%- for param in path["parameters"] %}
                "{{param["name"]}}": {{param["name"]}}{%- if not loop.last %},{% else %}
                {% endif %}
                {%- endfor -%}
            },
            {% endif -%}
            {%- if path["data"] %}
            "data": {
                {%- for param_name in path["data"] %}
                "{{param_name}}": {{param_name}}{%- if not loop.last %},{% else %}
                {% endif %}
                {%- endfor -%}
            },
            {% endif -%}
            {%- if path["files"] %}
            "files": [
                {%- for file_name in path["files"] %}
                ('{{file_name}}', (file.split('/')[-1] if '/' in file else file.split('\\')[-1],
                          open({{file_name}}, 'rb'),
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
                {%- if not loop.last %},{% else %}
                {% endif %}
                {%- endfor -%}
            ],
            {% endif -%}
            {%- if path["content-type"] %}
            "headers": {"content-type": "{{path["content-type"]}}"}
            {% endif -%}
        }
        return self.req(method="{{path["method"]}}", **req_data)

    {%- endfor -%}