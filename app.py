from flask import Flask, render_template, request, redirect
import redis
import os
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 直接从环境变量 REDIS_URL 连接，不需要 KV_TOKEN
try:
    kv = redis.from_url(os.getenv('REDIS_URL'))
    kv.ping()
except Exception as e:
    print(f"Redis连接失败: {e}")
    kv = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and kv is not None:
        content = request.form.get('content', '').strip()
        if content:
            memo_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            kv.hset('memos', memo_id, f"{content}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return redirect('/')

    keyword = request.args.get('keyword', '').strip()
    memos = []
    if kv is not None:
        all_memos = kv.hgetall('memos')
        sorted_memo_ids = sorted(all_memos.keys(), reverse=True)
        for memo_id in sorted_memo_ids:
            content, create_time = all_memos[memo_id].split('|', 1)
            if keyword == '' or keyword in content:
                memos.append({'content': content, 'create_time': create_time})

    return render_template('index.html', memos=memos, keyword=keyword)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
