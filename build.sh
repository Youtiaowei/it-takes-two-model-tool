#!/bin/bash
# =============================================
# 🔥 一键发布到 GitHub Actions 自动打包
#
# 用法:
#   bash build.sh "修改了什么"
#   bash build.sh           # 自动生成提交信息
# =============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ─── 颜色 ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── 配置 ───
GH_USER="Youtiaowei"
GH_REPO="it-takes-two-model-tool"
GH_TOKEN_FILE="$HOME/.github_pat"
API="https://api.github.com/repos/$GH_USER/$GH_REPO"

# ─── 提交信息 ───
if [ -z "$1" ]; then
    COMMIT_MSG="chore: $(date '+%Y-%m-%d %H:%M') 自动构建"
else
    COMMIT_MSG="$1"
fi

echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     🚀 一键发布到 GitHub Actions            ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ─── Token ───
if [ ! -f "$GH_TOKEN_FILE" ]; then
    echo -e "${YELLOW}⚠️  未找到 GitHub Token 文件 ($GH_TOKEN_FILE)${NC}"
    exit 1
fi
GH_TOKEN=$(cat "$GH_TOKEN_FILE" | tr -d '\n\r ')
echo -e "${GREEN}✅ 已加载 GitHub Token${NC}"

# ─── 暂存 & 提交 ───
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  没有变更需要提交${NC}"
    if ! git log origin/main..HEAD --oneline 2>/dev/null | grep -q .; then
        echo -e "${RED}❌ 没有新的提交需要推送${NC}"
        exit 0
    fi
    echo -e "${GREEN}📤 有未推送的提交，继续推送${NC}"
else
    echo -e "${CYAN}📦 暂存变更...${NC}"
    git add -A
    echo -e "${CYAN}📝 提交: $COMMIT_MSG${NC}"
    git commit -m "$COMMIT_MSG"
fi

# ─── 获取 base commit ───
echo -e "${CYAN}📤 推送到 GitHub...${NC}"

# 获取远程最新 commit SHA
REMOTE_SHA=$(curl -sf \
    -H "Authorization: token $GH_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "$API/git/refs/heads/main" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['object']['sha'])" 2>/dev/null || echo "")

if [ -z "$REMOTE_SHA" ]; then
    echo -e "${RED}❌ 无法获取远程分支状态${NC}"
    exit 1
fi

# ─── 获取变更文件列表 ───
# 计算本地有但远程没有的提交中的变更
CHANGED=$(git diff --name-only "$(git rev-parse HEAD~1 2>/dev/null || echo HEAD)" HEAD 2>/dev/null || echo "")
if [ -z "$CHANGED" ]; then
    # 如果是第一次提交，用 ls-files
    CHANGED=$(git ls-files)
fi

echo -e "${CYAN}📄 变更文件 ($(echo "$CHANGED" | wc -l) 个)${NC}"

# ─── 检查是否有 workflow 文件变更 ───
HAS_WORKFLOW=$(echo "$CHANGED" | grep -c "^\.github/workflows/" || true)

# Python 脚本：批量创建 blob → tree → commit → update ref
python3 -c "
import json, subprocess, base64, sys, tempfile, os, shlex

TOKEN = '''$GH_TOKEN'''
API = '$API'
MSG = '''$COMMIT_MSG'''

files_str = '''$CHANGED'''
files = [f.strip() for f in files_str.strip().split('\n') if f.strip()]

def api_call(method, endpoint, data=None):
    url = f'{API}/{endpoint}'
    cmd = ['curl', '-sf', '-X', method,
           '-H', f'Authorization: token {TOKEN}',
           '-H', 'Accept: application/vnd.github.v3+json']
    if data:
        js = json.dumps(data)
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        tmp.write(js)
        tmp.close()
        cmd += ['-H', 'Content-Type: application/json', '-d', f'@{tmp.name}']
    cmd += [url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if data:
        os.unlink(tmp.name)
    if result.returncode != 0:
        print(f'  ⚠️  API call failed ({method} {endpoint}): {result.stderr[:100]}')
        return None
    try:
        return json.loads(result.stdout)
    except:
        return None

# 如果包含 workflow 文件，用 Contents API 单独上传
workflow_files = [f for f in files if f.startswith('.github/workflows/')]
other_files = [f for f in files if not f.startswith('.github/workflows/')]

for wf in workflow_files:
    if not os.path.isfile(wf):
        continue
    with open(wf, 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    # 获取当前文件 SHA
    existing = api_call('GET', f'contents/{wf}?ref=main')
    sha = existing.get('sha', '') if existing else ''
    data = {
        'message': MSG,
        'content': content,
        'branch': 'main'
    }
    if sha:
        data['sha'] = sha
    result = api_call('PUT', f'contents/{wf}', data)
    if result:
        print(f'  ✅ 上传 workflow: {wf}')
    else:
        print(f'  ⚠️  上传 workflow 失败: {wf}')

if not other_files:
    print('✅ 所有文件上传完成')
    sys.exit(0)

# ─── 获取远程 tree SHA ───
remote_commit = api_call('GET', f'git/commits/$REMOTE_SHA')
if not remote_commit:
    print('❌ 无法获取远程 commit')
    sys.exit(1)
base_tree_sha = remote_commit['tree']['sha']

# ─── 创建 blob ───
blobs = []
for f in other_files:
    if not os.path.isfile(f):
        continue
    with open(f, 'rb') as fh:
        raw = fh.read()
    is_text = True
    try:
        raw.decode('utf-8')
    except:
        is_text = False
    
    if is_text:
        b64 = base64.b64encode(raw).decode()
        blob_data = {'content': raw.decode('utf-8'), 'encoding': 'utf-8'}
    else:
        b64 = base64.b64encode(raw).decode()
        blob_data = {'content': b64, 'encoding': 'base64'}
    
    blob = api_call('POST', 'git/blobs', blob_data)
    if blob:
        blobs.append({'path': f, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
        print(f'  ✅ 上传: {f}')
    else:
        print(f'  ⚠️  上传失败: {f}')

if not blobs:
    print('没有可上传的文件')
    sys.exit(0)

# ─── 创建 tree ───
tree_data = {'tree': blobs, 'base_tree': base_tree_sha}
tree_result = api_call('POST', 'git/trees', tree_data)
if not tree_result:
    print('❌ 创建 tree 失败')
    sys.exit(1)
tree_sha = tree_result['sha']

# ─── 创建 commit ───
commit_data = {
    'message': MSG,
    'tree': tree_sha,
    'parents': ['$REMOTE_SHA']
}
commit_result = api_call('POST', 'git/commits', commit_data)
if not commit_result:
    print('❌ 创建 commit 失败')
    sys.exit(1)
new_sha = commit_result['sha']

# ─── 更新 ref ───
ref_result = api_call('PATCH', 'git/refs/heads/main', {'sha': new_sha, 'force': True})
if ref_result:
    print(f'✅ 推送完成! Commit: {new_sha[:12]}')
else:
    print('❌ 更新 ref 失败')
    sys.exit(1)
"

echo ""

# ─── 等待 Actions 完成 ───
echo -e "${CYAN}⏳ 等待 GitHub Actions 构建完成...${NC}"
echo ""

MAX_WAIT=300
INTERVAL=10
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    sleep $INTERVAL
    WAITED=$((WAITED + INTERVAL))
    
    RUN_DATA=$(curl -sf \
        -H "Authorization: token $GH_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "$API/actions/runs?per_page=1" \
        | python3 -c "
import sys,json
d=json.load(sys.stdin)
r = d['workflow_runs'][0]
s = r['status']
c = r.get('conclusion','')
print(f'{s}|{c}|{r[\"id\"]}|{r[\"html_url\"]}')
" 2>/dev/null || echo "pending")
    
    STATUS=$(echo "$RUN_DATA" | cut -d'|' -f1)
    CONCLUSION=$(echo "$RUN_DATA" | cut -d'|' -f2)
    RUN_ID=$(echo "$RUN_DATA" | cut -d'|' -f3)
    RUN_URL=$(echo "$RUN_DATA" | cut -d'|' -f4)
    
    if [ "$STATUS" = "completed" ]; then
        if [ "$CONCLUSION" = "success" ]; then
            echo ""
            echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║     ✅ 构建成功！                          ║${NC}"
            echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "  📎 下载 exe:"
            echo -e "    $RUN_URL"
            echo ""
            echo -e "  打开后点 Artifacts → 下载 zip，解压即得 .exe"
            exit 0
        elif [ "$CONCLUSION" = "failure" ]; then
            echo ""
            echo -e "${RED}╔══════════════════════════════════════════════╗${NC}"
            echo -e "${RED}║     ❌ 构建失败！                          ║${NC}"
            echo -e "${RED}╚══════════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "  查看日志: $RUN_URL"
            exit 1
        fi
    fi
    
    echo -ne "\r⏳ 等待中... ${WAITED}s / ${MAX_WAIT}s   "
done

echo ""
echo -e "${YELLOW}⏰ 等待超时，请手动查看：${NC}"
echo "  https://github.com/$GH_USER/$GH_REPO/actions"
