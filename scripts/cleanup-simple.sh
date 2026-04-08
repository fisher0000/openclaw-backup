#!/bin/bash
# 清理重复文件 - 使用 OpenClaw CLI

echo "开始清理重复文件..."

# ICH 文件夹重复文件 (保留最新，删除旧版本)
delete_file() {
    local token=$1
    echo "删除: $token"
    openclaw tools feishu_drive_file action=delete file_token="$token" type=file 2>&1 | grep -E "(成功|失败|error)" || echo "命令已发送"
}

# ICH 文件夹 - 删除 4月4日和4月7日的版本
echo "=== 清理 ICH 文件夹 ==="
delete_file "Y55MbLUokoxJpIxfqcRc6Axjndb"  # Q3D R2 - 4月4日
delete_file "FkBBbbtXho7KfLxQcj0c6HJwn4c"  # Q3D R2 - 4月7日
delete_file "TdPhbIHpzoiZ6uxOutUcsAMtnVb"  # Q8 R2 - 4月4日
delete_file "VUaXbpvxbo3VfgxaHhzc09vQn5c"  # Q8 R2 - 4月7日

echo "=== 清理 FDA 文件夹 ==="
delete_file "DWi3bm6inoX4RhxPGG3cG4JFn1e"  # FDA Orange Book - 4月4日
delete_file "L31Hb6ByqoFoz1xbh4HcxRZ5nGg"  # FDA Orange Book - 4月7日
delete_file "KNDBbnhgbo3u1OxpS5Dcuw0inBd"  # ANDA - 4月4日
delete_file "EJYZbQepdobKerxmzwuce66Dnze"  # ANDA - 4月7日

echo "=== 清理 EMA 文件夹 ==="
delete_file "MRiDbK2hBoNCM1xO1y2cZvp5nyZ"  # EMA - 4月4日
delete_file "HHfubr1upoRjydxHTWochkyJn0c"  # EMA - 4月7日

echo "清理完成！"
