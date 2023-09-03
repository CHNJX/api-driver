# -*- coding:utf-8 -*-
# @Time     :2023/8/20 10:38
# @Author   :CHNJX
# @File     :adf_proxy.py
# @Desc     :
from mitmproxy import options
from mitmproxy.proxy import ProxyConfig
from mitmproxy.tools.dump import DumpMaster


class InterceptAddon:
    def request(self, flow):
        print("Intercepted request:", flow.request.url)


if __name__ == "__main__":
    opts = options.Options(listen_host="0.0.0.0", listen_port=8080)  # 设置代理监听的地址和端口
    config = ProxyConfig(opts)
    master = DumpMaster(opts, with_termlog=False)

    addons = [
        InterceptAddon()
    ]

    master.server = ProxyServer(config)
    master.addons.add(*addons)

    try:
        print("Starting mitmproxy")
        master.run()
    except KeyboardInterrupt:
        master.shutdown()
        print("Mitmproxy has been shut down")
