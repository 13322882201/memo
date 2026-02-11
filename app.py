from flask import Flask, render_template, request, redirect
import redis
import os
from datetime import datetime

# 初始化 Flask 应用（适配 Vercel 环境）
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 连接 Vercel KV 数据库（关键：替换成你的 KV_URL 和 KV_TOKEN）
# 你可以在 Vercel 后台的 Storage -> KV 里找到这两个值
kv = redis.Redis(
    url=os.getenv('KV_URL', '你的KV_URL地址'),  # 替换成实际的KV_URL
    token=os.getenv('KV_TOKEN', '你的KV_TOKEN'),# 替换成实际的KV_TOKEN
    decode_responses=True  # 确保返回字符串而非字节
)

# 首页：显示/新增/搜索备忘录
@app.route('/', methods=['GET', 'POST'])
def index():
    # 处理「新增备忘录」
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:  # 非空内容才保存
            # 用时间戳生成唯一ID，保证不重复
            memo_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            # 存储格式：内容|创建时间
            kv.hset('memos', memo_id, f"{content}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return redirect('/')  # 新增后刷新页面

    # 处理「搜索备忘录」
    keyword = request.args.get('keyword', '').strip()
    memos = []
    # 获取所有备忘录并按时间倒序排列（最新的在最前面）
    all_memos = kv.hgetall('memos')
    sorted_memo_ids = sorted(all_memos.keys(), reverse=True)

    # 过滤搜索结果
    for memo_id in sorted_memo_ids:
        content, create_time = all_memos[memo_id].split('|', 1)
        if keyword == '' or keyword in content:
            memos.append({
                'content': content,
                'create_time': create_time
            })

    return render_template('index.html', memos=memos, keyword=keyword)

# Vercel 启动入口（必须保留，适配云环境）
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),  # Vercel 自动分配端口
        debug=False  # 生产环境关闭调试，更省资源
    )