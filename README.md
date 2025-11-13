小米运动（Zepp Life）自动刷步数（邮箱/手机号通用）- Github Actions 指南

一、部署步骤

1. Fork 仓库：访问目标仓库，点击右上角「Fork」到自己账号。

2. 配置变量（Settings → Secrets and variables → Actions → New repository secret）：

◦ USER：Zepp Life账号（邮箱/手机号均可，独立账号，非小米账号）

◦ PWD：Zepp Life登录密码

3. 设置步数区间：
编辑仓库配置文件（如config.py），修改step_min（最小步数）和step_max（最大步数），示例：5000-8000步。

4. 触发运行：
仓库页面 → Actions → 选择「刷步数」→ 点击「Run workflow」。

二、可选：自定义运行时间

编辑 .github/workflows/run.yml 中的cron语句（UTC时间，北京时间=UTC+8小时），示例：北京时间19点对应 0 11 * * *。

name: 步数自动运行写入
on:
  #⚠️schedule:                使用时删除前端#
  #⚠️- cron: '05 11 * * *'  使用时删除前端#

三、注意事项

1. 步数仅同步至第三方（如支付宝），Zepp Life App内不显示；

2. 支付宝步数未更新：注销Zepp Life账号→清空数据→重新登录绑定；

3. 需用Zepp Life独立账号，勿用小米账号登录。