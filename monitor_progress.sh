#!/bin/bash
# 监控 AI 处理进度

OUTPUT_FILE="/tmp/claude-1000/-home-vone-zjn-2-peresonal-repo/57076d29-d8b7-415f-b463-c1956d49953c/tasks/br7o5yo8x.output"
STATUS_FILE="/tmp/arxiv_processing_status.txt"

echo "开始监控..." > "$STATUS_FILE"

while true; do
    # 检查进程是否还在运行
    if ! ps aux | grep -v grep | grep "uv run.*main.py" > /dev/null; then
        echo "✅ 处理完成！" >> "$STATUS_FILE"
        # 获取最终统计
        tail -200 "$OUTPUT_FILE" | grep -E "论文 [0-9]+/(149|130|262)|INFO.*过滤完成|INFO.*评分完成|INFO.*处理流程完成" >> "$STATUS_FILE"
        break
    fi

    # 每 5 分钟更新一次状态
    CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    echo "" >> "$STATUS_FILE"
    echo "════════════════════════════════════════" >> "$STATUS_FILE"
    echo "📊 状态更新 - $CURRENT_TIME" >> "$STATUS_FILE"
    echo "════════════════════════════════════════" >> "$STATUS_FILE"

    # 获取当前处理的论文信息
    tail -100 "$OUTPUT_FILE" | grep -E "论文 [0-9]+/(149|130|262)" | tail -5 >> "$STATUS_FILE"

    # 统计成功和失败
    SUCCESS_COUNT=$(tail -500 "$OUTPUT_FILE" | grep -c "论文.*AI 回复: yes\|论文.*AI 回复: no" || echo 0)
    FAIL_COUNT=$(tail -500 "$OUTPUT_FILE" | grep -c "达到最大重试次数" || echo 0)

    echo "" >> "$STATUS_FILE"
    echo "✅ 成功: $SUCCESS_COUNT 篇" >> "$STATUS_FILE"
    echo "❌ 失败: $FAIL_COUNT 篇" >> "$STATUS_FILE"
    echo "⏱️  运行时间: $(ps -o etime= -p $(pgrep -f 'uv run.*main.py' | tail -1) 2>/dev/null | tr -d ' ' || echo '未知')" >> "$STATUS_FILE"

    echo "" >> "$STATUS_FILE"

    # 等待 5 分钟
    sleep 300
done

echo "监控结束" >> "$STATUS_FILE"
