# Windows exe 交叉构建镜像
# 基于 Wine + Python 3.11 + PyInstaller
FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV WINEPREFIX=/wine
ENV WINEDLLOVERRIDES="winemenubuilder.exe=d"
ENV DISPLAY=:0

# 1. 基础工具 + Wine
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    xauth \
    wine \
    wine64 \
    wine32:i386 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. 复制本地 Python 安装包
COPY python-3.11.9-amd64.exe /tmp/python-installer.exe

# 3. 静默安装 Python（无 GUI）
RUN xvfb-run -a wine /tmp/python-installer.exe \
    /quiet \
    InstallAllUsers=1 \
    PrependPath=1 \
    Include_test=0 \
    Include_tools=0 \
    Include_exe=1 \
    Include_pip=1 \
    Include_dev=1 \
    && rm /tmp/python-installer.exe

# 4. 安装 PyInstaller
RUN xvfb-run -a wine python -m pip install --no-cache-dir pyinstaller

# 5. 设置工作目录
WORKDIR /src
VOLUME ["/src", "/output"]

# 默认命令
COPY build-inside-wine.bat /build-inside-wine.bat
ENTRYPOINT ["xvfb-run", "-a", "wine", "cmd", "/c", "C:\\build-inside-wine.bat"]
