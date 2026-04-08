#!/usr/bin/env python3
"""
清理飞书云盘重复文件脚本
保留最新版本，删除旧版本
"""

import subprocess
import json

# 需要删除的文件 token 列表（旧版本）
# 基于时间戳分析：保留 177560xxxx (4月8日)，删除 177512xxxx (4月4日) 和 177534xxxx (4月7日)

files_to_delete = [
    # ICH 文件夹 - 旧版本 (4月4日和4月7日)
    "Y55MbLUokoxJpIxfqcRc6Axjndb",  # Q3D R2 - 4月4日
    "FkBBbbtXho7KfLxQcj0c6HJwn4c",  # Q3D R2 - 4月7日
    "TdPhbIHpzoiZ6uxOutUcsAMtnVb",  # Q8 R2 - 4月4日
    "VUaXbpvxbo3VfgxaHhzc09vQn5c",  # Q8 R2 - 4月7日
    "LGEDbrjbWom7pAx3HeTcrhbcnse",  # Q7 问答 - 4月4日
    "XefobzWlsocfXpxOq0Dc56TZnWd",  # Q7 问答 - 4月7日
    "AHcibnlYuoVfpjxeOPPcWRgLn6d",  # Q7 - 4月4日
    "UEiAbpEhAo1uguxNzcMcCNuGnbd",  # Q7 - 4月7日
    "IHt7b2g1doP1eExpixHcIa2GnQg",  # Q3E - 4月4日
    "CsSsbVR1boXqivxfZHrc1ZBPnRe",  # Q3E - 4月7日
    "ZAw9bbP4zoHaZIxTBDNcYp8Xnfe",  # Q3C R9 - 4月4日
    "Lj18bFhkMofda5xaKxPcVXM1nbh",  # Q3C R9 - 4月7日
    "TAOtboA7QouEKHx4GkEch4k7nP3",  # Q3A R2 - 4月4日
    "Ji9aboIkno3mwOxPwH2czhFBnTb",  # Q3A R2 - 4月7日
    "FUqGbJixlow4sAxAQCucNE1Anxg",  # Q2 R2 - 4月4日
    "EUizbECqaoG6lZxUhSOcvEW6nzb",  # Q2 R2 - 4月7日
    "PartbayQJoBj19xNdL9cmS1mnJb",  # Q1指导原则 - 4月4日
    "CeC8be4aBoa2AUx34a0c7omAnIh",  # Q1指导原则 - 4月7日
    "GGwJbnvsooTsMHxVvQLcjN3znCc",  # Q1B - 4月4日
    "O6VebM5sxoAaCix4GjdcAcOpnKY",  # Q1B - 4月7日
    "ESBwb3j9koCCnPxiCfmcaCJLnuc",  # Q1A R2 - 4月4日
    "Xijnbp6KFo4u9kx6zr3c4yVLnkk",  # Q1A R2 - 4月7日
    "Mq9Pb3RAaoufmCxivz8cSa63nSe",  # Q14 - 4月4日
    "BD5obQhW2owGWexga7bcMfi0nDh",  # Q14 - 4月7日
    "G057b3ZB5oLS42xBhSfcJzGvnoh",  # Q13 - 4月4日
    "NTCcbijvfomBwpxth6lcqGwQnDd",  # Q13 - 4月7日
    "Fvm7b0Yezo9btOxdhFwcZL4Dnbd",  # Q11 问答 - 4月4日
    "NVFEbi1XooPQwqxpuwac0H5qnCh",  # Q11 问答 - 4月7日
    "V4HDbovJJofgE6xWqu3cd01cnlh",  # Q11 - 4月4日
    "AOOBbA9eHoyxlGxDfJccufjVn0e",  # Q11 - 4月7日
    "Au7jbiX3ooGhhhxONdvcix8bnFd",  # M7 R2 问答 - 4月4日
    "VSo3b2sgfoYPyxxCo8jcb3wDnTb",  # M7 R2 问答 - 4月7日
    "Oe72bmHsZo3SStxVOBCc07S5njh",  # M7 R2 - 4月4日
    "W63xbunOeoooHOxhj7Ycp7u2nwb",  # M7 R2 - 4月7日
    "Q0H3byjL2onFVSxO3LmcYo9Gnzd",  # M4Q(R1) - 4月4日
    "JKv5bz5lMonkrlxeLrCcYNFHnAf",  # M4Q(R1) - 4月7日
    
    # FDA 文件夹 - 旧版本
    "DWi3bm6inoX4RhxPGG3cG4JFn1e",  # FDA Orange Book - 4月4日
    "L31Hb6ByqoFoz1xbh4HcxRZ5nGg",  # FDA Orange Book - 4月7日
    "KNDBbnhgbo3u1OxpS5Dcuw0inBd",  # ANDA 申报 - 4月4日
    "EJYZbQepdobKerxmzwuce66Dnze",  # ANDA 申报 - 4月7日
    
    # EMA 文件夹 - 旧版本
    "MRiDbK2hBoNCM1xO1y2cZvp5nyZ",  # EMA - 4月4日
    "HHfubr1upoRjydxHTWochkyJn0c",  # EMA - 4月7日
    
    # NMPA 文件夹 - 旧版本 (4月4日和4月7日)
    "OdjRbexBdoh23wxf0H0cvVmJnCe",  # 广东省 - 4月4日
    "SoY0bKRX6olzmOxiiEKcwCR9nie",  # 广东省 - 4月7日
    "QgOObU4Fvo73z3xOcqPcsHTUnyg",  # SAMR - 4月4日
    "KLXHb6DcyoW3VfxWBZ2cMG31n5f",  # SAMR - 4月7日
    "HQO9bysZ5oIWW6xRryLcDe7Bn7f",  # NMPA 药品记录 - 4月4日
    "Trbob4KNko4I1UxtqB4ckrWonmh",  # NMPA 药品记录 - 4月7日
    "DR5hb7q1zooFSVxtAJmcFUlQned",  # NMPA 化学药品 - 4月4日
    "WqXSbRgHToi5jfxhon2cHhkhnqd",  # NMPA 化学药品 - 4月7日
    "LZBTbm6bhoLMdux9fCycxCAmnie",  # CFDI 核查要点 - 4月4日
    "F2Ohbe6lloc1Wxx6WUncGuJanup",  # CFDI 核查要点 - 4月7日
    "JfG2bqMa5ozK8oxXUoncEq2mnhc",  # CFDI 核查程序 - 4月4日
    "X51obbpNOo08Yqx278Lcat4fn9d",  # CFDI 核查程序 - 4月7日
    "H69mbqO4toGQ2Exm1lRcKmQOnTd",  # CFDI 工艺验证 - 4月4日
    "US1kbjxNxofjlOxTYj2coIA5nxg",  # CFDI 工艺验证 - 4月7日
    "WJhObMXDdo4vHPxGGAVcEZSEngg",  # CDE 已上市 - 4月4日
    "KDU3bf6N8oF5YqxJgltcd3XlnAh",  # CDE 已上市 - 4月7日
    "IYpfbObNPoAOIPxM3R3c5wtMn3f",  # CDE 创新药 - 4月4日
    "XRE4b4zRBol720xzDsqc5SXsnXb",  # CDE 创新药 - 4月7日
    
    # 研究专题 文件夹 - 旧版本
    "I5lKb37WBofR82xEOH0cmZljnBf",  # 分类警示结构 - 4月4日
    "Ai3fbSlsPoxWSSxVj7wcN3K8nUd",  # 分类警示结构 - 4月7日
    "GE2DbK5TEoOWl2x3xcqcGqdNnzg",  # 分类研发质量体系 - 4月4日
    "XQF3bjV4SonbZuxobz7cQpmtnQh",  # 分类研发质量体系 - 4月7日
    "NHWLbGUGvocCnRx2qMScZVBwnWf",  # 分类基因毒性杂质 - 4月4日
    "LWWlbJSYRo9AW0xGey5cTvZSnbg",  # 分类基因毒性杂质 - 4月7日
]

print(f"准备删除 {len(files_to_delete)} 个重复文件...")
print("=" * 60)

deleted_count = 0
failed_count = 0

for file_token in files_to_delete:
    cmd = [
        "openclaw", "tools", "feishu_drive_file",
        "action=delete",
        f"file_token={file_token}",
        "type=file"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ 已删除: {file_token}")
            deleted_count += 1
        else:
            print(f"❌ 删除失败: {file_token} - {result.stderr}")
            failed_count += 1
    except Exception as e:
        print(f"❌ 异常: {file_token} - {e}")
        failed_count += 1

print("=" * 60)
print(f"删除完成: 成功 {deleted_count} 个, 失败 {failed_count} 个")
