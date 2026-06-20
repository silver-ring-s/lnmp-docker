from flask import Flask, render_template, request, redirect, url_for
import psutil
import subprocess
import os

app = Flask(__name__)

HOST_ROOT = "/host"

ALLOWED_COMMANDS = {
    "磁盘使用": ["chroot", HOST_ROOT, "df", "-h"],
    "内存使用": ["chroot", HOST_ROOT, "free", "-h"],
    "系统运行时间": ["chroot", HOST_ROOT, "uptime"],
    "网络接口": ["chroot", HOST_ROOT, "ip", "addr"],
    "路由表": ["chroot", HOST_ROOT, "ip", "route"],
    "Ping 网关": ["chroot", HOST_ROOT, "ping", "-c", "4", "192.168.152.2"],
}

def get_docker_containers():
    """通过 docker CLI 获取容器列表"""
    try:
        # 执行 docker ps -a --format 获取结构化信息
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}"],
            capture_output=True, text=True, timeout=5
        )
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) == 4:
                    containers.append({
                        "id": parts[0],
                        "short_id": parts[0][:12],
                        "name": parts[1],
                        "status": parts[2],
                        "image": parts[3]
                    })
        return containers
    except Exception as e:
        return []

def control_container(container_id, action):
    """启动或停止容器"""
    try:
        subprocess.run(
            ["docker", action, container_id],
            capture_output=True, text=True, timeout=10, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"操作失败: {e.stderr}")

@app.route('/')
def index():
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(HOST_ROOT)
    info = {
        "hostname": os.uname().nodename,
        "os": f"{os.uname().sysname} {os.uname().release}",
        "cpu_percent": cpu_percent,
        "mem_total": f"{mem.total // (1024**3)} GB",
        "mem_used": f"{mem.used // (1024**3)} GB",
        "mem_free": f"{mem.available // (1024**3)} GB",
        "disk_total": f"{disk.total // (1024**3)} GB",
        "disk_used": f"{disk.used // (1024**3)} GB",
        "disk_free": f"{disk.free // (1024**3)} GB",
    }
    return render_template('index.html', info=info)

@app.route('/containers')
def list_containers():
    containers = get_docker_containers()
    return render_template('containers.html', containers=containers)

@app.route('/container/start/<container_id>')
def start_container(container_id):
    control_container(container_id, 'start')
    return redirect(url_for('list_containers'))

@app.route('/container/stop/<container_id>')
def stop_container(container_id):
    control_container(container_id, 'stop')
    return redirect(url_for('list_containers'))

@app.route('/commands', methods=['GET', 'POST'])
def run_command():
    result = None
    if request.method == 'POST':
        command_key = request.form.get('command')
        cmd_list = ALLOWED_COMMANDS.get(command_key)
        if cmd_list:
            try:
                output = subprocess.check_output(cmd_list, stderr=subprocess.STDOUT, timeout=10)
                result = output.decode('utf-8', errors='replace')
            except subprocess.CalledProcessError as e:
                result = f"命令执行失败: {e.output.decode('utf-8', errors='replace')}"
            except subprocess.TimeoutExpired:
                result = "命令执行超时"
        else:
            result = "不允许的命令"
    return render_template('commands.html', commands=list(ALLOWED_COMMANDS.keys()), result=result)

@app.route('/logs')
def show_logs():
    log_path = os.path.join(HOST_ROOT, "var/log/syslog")
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            content = ''.join(lines[-50:])
    except Exception as e:
        content = f"无法读取日志文件: {e}"
    return render_template('logs.html', log_content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
