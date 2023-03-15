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
        {%- endfor -%}
        """

        req_data = {
            "url": {% if path["url_param"] %}f"{{path["url"]}}/{ {{path["url_param"]}} }"{% else %}f"{{key}}"{% endif %},
            "params": {
                {%- for param in path["parameters"] %}
                "{{param["name"]}}": {{param["name"]}}{%- if not loop.last %},{% else %}
                {% endif %}
                {%- endfor -%}
            },
            "json": {
                {%- for param_name in path["json"] %}
                "{{param_name}}": {{param_name}}{%- if not loop.last %},{% else %}
                {% endif %}
                {%- endfor -%}
            },
            "files": {
                {%- for file_name in path["files"] %}
                "{{file_name}}": open({{file_name}}, "rb"),{%- if not loop.last %},{% else %}
                {% endif %}
                {%- endfor -%}
            }
        }
        return self.req(method="{{path["method"]}}", **req_data)

    {%- endfor -%}