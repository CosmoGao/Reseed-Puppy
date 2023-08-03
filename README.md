# Reseed-Puppy介绍
基于pieces_hash的辅种工具
# 使用方式
pip install -r requirements.txt
安装好库后
执行 sanic index.app 运行服务
本地会启动8000端口服务，是原始人网页配置页面
index.py中await asyncio.sleep(10)是配置辅种间隔时间