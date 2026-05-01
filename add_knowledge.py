#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加用户级/设备级IPsec知识"""

# 新知识点数据
new_knowledge = {
    "icon": "🖥️",
    "content": """<h2>用户级/设备级IPsec详解</h2>
<p>IPsec可以在不同层面进行部署：用户/设备层面、网关/路由器层面，以及操作系统的用户空间/内核空间实现。</p>

<h3>部署架构：设备级 vs 网关级</h3>
<h4>设备级IPsec (Per-Device / Device-Level)</h4>
<p>在每个终端设备上单独部署IPsec客户端。</p>
<ul>
<li>每个设备独立建立IPsec隧道</li>
<li>VPN客户端安装在设备上（如Cisco AnyConnect、Windows内置IPsec客户端）</li>
<li>适用于笔记本、手机等移动设备</li>
</ul>

<h4>网关级IPsec (Router-Level / Gateway-Level)</h4>
<p>在网络入口的路由器或防火墙上集中部署IPsec。</p>
<ul>
<li>网关设备集中建立和管理IPsec隧道</li>
<li>网关后面的所有设备自动受保护</li>
<li>适用于家庭路由器、企业网关、IoT网络</li>
</ul>

<h3>设备级 vs 网关级对比</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>设备级IPsec</th><th>网关级IPsec</th></tr>
<tr><td>覆盖范围</td><td>仅安装了客户端的设备</td><td>网关后面的所有设备</td></tr>
<tr><td>细粒度控制</td><td>✅ 每设备/每用户策略</td><td>❌ 全网统一策略</td></tr>
<tr><td>管理复杂度</td><td>高（多设备维护）</td><td>低（单点管理）</td></tr>
<tr><td>IoT设备支持</td><td>❌ 常无法安装客户端</td><td>✅ 自动保护所有设备</td></tr>
<tr><td>漫游能力</td><td>✅ 支持Wi-Fi/Cellular切换</td><td>❌ 依赖网关位置</td></tr>
<tr><td>审计溯源</td><td>✅ 可逐用户审计</td><td>❌ 流量混合难追踪</td></tr>
<tr><td>网络中断影响</td><td>仅单设备受影响</td><td>全网受影响</td></tr>
</table>

<h3>部署决策框架</h3>
<ul>
<li><b>仅家庭智能设备/IoT</b>：网关级IPsec</li>
<li><b>远程办公/出差</b>：设备级IPsec（IKEv2）</li>
<li><b>混合场景</b>：网关级保护IoT+TV，设备级保护工作设备</li>
</ul>

<h3>架构实现：用户空间 vs 内核空间</h3>
<p>操作系统中的IPsec实现通常采用分层架构：</p>

<h4>用户空间 (User Space)</h4>
<ul>
<li>IKE守护进程（如`in.iked`、`strongSwan`、`libreswan`）</li>
<li>SA管理和密钥协商</li>
<li>策略配置管理</li>
<li>PKI证书处理</li>
<li>通过`pf_key`或`netlink`接口与内核通信</li>
</ul>

<h4>内核空间 (Kernel Space)</h4>
<ul>
<li>ESP/AH数据包加解密处理</li>
<li>SAD/SPD管理</li>
<li>高性能加密（硬件加速支持）</li>
<li>直接挂接在IP协议栈中</li>
</ul>

<h3>Linux IPsec实现架构</h3>
<pre>
┌─────────────────────────────────────────────────────────┐
│                  应用层 (User Space)                    │
│ strongSwan / libreswan / IKE 守护进程  ← 密钥协商     │
│                   /sbin/setkey  ← 策略管理工具             │
└───────────────────┬─────────────────────────────────────┘
                    │ pf_key / netlink
┌───────────────────┴─────────────────────────────────────┐
│                  内核层 (Kernel Space)                  │
│    ┌──────────────────────────────────────────────┐   │
│    │  SADB (Security Association Database)     │   │
│    │  SPD (Security Policy Database)         │   │
│    └──────────────────┬───────────────────────────┘   │
│                       │                               │
│    ┌──────────────────┴───────────────────────────┐   │
│    │  ESP/AH 处理  +  加密/认证算法            │   │
│    └──────────────────┬───────────────────────────┘   │
│                       │                               │
│    ┌──────────────────┴───────────────────────────┐   │
│    │           IP 协议栈                    │   │
│    └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
</pre>

<h3>应用级IPsec (Per-Socket / Per-Application)</h3>
<p>除了设备级/网关级，还可以在应用层面控制IPsec：</p>
<ul>
<li>应用程序可以通过socket API指定使用IPsec保护</li>
<li>仅保护特定应用的流量</li>
<li>适合需要细粒度控制的场景</li>
</ul>

<h3>混合部署模式推荐</h3>
<table border="1" cellpadding="5">
<tr><th>场景</th><th>推荐架构</th></tr>
<tr><td>智能家居</td><td>网关级IPsec保护所有IoT设备</td></tr>
<tr><td>远程办公</td><td>设备级IPsec + IKEv2 MOBIKE</td></tr>
<tr><td>企业分支</td><td>网关级Site-to-Site + 员工设备级Remote</td></tr>
<tr><td>双SSID网络</td><td>Guest/IoT走网关隧道，工作设备走独立客户端</td></tr>
</table>

<h3>性能考量</h3>
<ul>
<li>设备级：加解密在CPU，有负载限制</li>
<li>网关级：需要硬件加密能力，避免瓶颈</li>
<li>MTU设置：减少分片，优化性能</li>
</ul>
"""
}

# 读取原文件
with open('ipsec_master.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在最后一个知识点后插入新知识点
# 找到最后的 } 之前插入
last_knowledge_end = content.rfind('},')

# 找到 "GRE over IPsec与IPsec over GRE" 后的位置
insert_point = content.rfind('},')

new_content = content[:insert_point] + ''',
    "用户级/设备级IPsec": {
        "icon": "🖥️",
        "content": """<h2>用户级/设备级IPsec详解</h2>
<p>IPsec可以在不同层面进行部署：用户/设备层面、网关/路由器层面，以及操作系统的用户空间/内核空间实现。</p>

<h3>部署架构：设备级 vs 网关级</h3>
<h4>设备级IPsec (Per-Device / Device-Level)</h4>
<p>在每个终端设备上单独部署IPsec客户端。</p>
<ul>
<li>每个设备独立建立IPsec隧道</li>
<li>VPN客户端安装在设备上（如Cisco AnyConnect、Windows内置IPsec客户端）</li>
<li>适用于笔记本、手机等移动设备</li>
</ul>

<h4>网关级IPsec (Router-Level / Gateway-Level)</h4>
<p>在网络入口的路由器或防火墙上集中部署IPsec。</p>
<ul>
<li>网关设备集中建立和管理IPsec隧道</li>
<li>网关后面的所有设备自动受保护</li>
<li>适用于家庭路由器、企业网关、IoT网络</li>
</ul>

<h3>设备级 vs 网关级对比</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>设备级IPsec</th><th>网关级IPsec</th></tr>
<tr><td>覆盖范围</td><td>仅安装了客户端的设备</td><td>网关后面的所有设备</td></tr>
<tr><td>细粒度控制</td><td>✅ 每设备/每用户策略</td><td>❌ 全网统一策略</td></tr>
<tr><td>管理复杂度</td><td>高（多设备维护）</td><td>低（单点管理）</td></tr>
<tr><td>IoT设备支持</td><td>❌ 常无法安装客户端</td><td>✅ 自动保护所有设备</td></tr>
<tr><td>漫游能力</td><td>✅ 支持Wi-Fi/Cellular切换</td><td>❌ 依赖网关位置</td></tr>
<tr><td>审计溯源</td><td>✅ 可逐用户审计</td><td>❌ 流量混合难追踪</td></tr>
<tr><td>网络中断影响</td><td>仅单设备受影响</td><td>全网受影响</td></tr>
</table>

<h3>部署决策框架</h3>
<ul>
<li><b>仅家庭智能设备/IoT</b>：网关级IPsec</li>
<li><b>远程办公/出差</b>：设备级IPsec（IKEv2）</li>
<li><b>混合场景</b>：网关级保护IoT+TV，设备级保护工作设备</li>
</ul>

<h3>架构实现：用户空间 vs 内核空间</h3>
<p>操作系统中的IPsec实现通常采用分层架构：</p>

<h4>用户空间 (User Space)</h4>
<ul>
<li>IKE守护进程（如`in.iked`、`strongSwan`、`libreswan`）</li>
<li>SA管理和密钥协商</li>
<li>策略配置管理</li>
<li>PKI证书处理</li>
<li>通过`pf_key`或`netlink`接口与内核通信</li>
</ul>

<h4>内核空间 (Kernel Space)</h4>
<ul>
<li>ESP/AH数据包加解密处理</li>
<li>SAD/SPD管理</li>
<li>高性能加密（硬件加速支持）</li>
<li>直接挂接在IP协议栈中</li>
</ul>

<h3>Linux IPsec实现架构</h3>
<pre>
┌─────────────────────────────────────────────────────────┐
│                  应用层 (User Space)                    │
│ strongSwan / libreswan / IKE 守护进程  ← 密钥协商     │
│                   /sbin/setkey  ← 策略管理工具             │
└───────────────────┬─────────────────────────────────────┘
                    │ pf_key / netlink
┌───────────────────┴─────────────────────────────────────┐
│                  内核层 (Kernel Space)                  │
│    ┌──────────────────────────────────────────────┐   │
│    │  SADB (Security Association Database)     │   │
│    │  SPD (Security Policy Database)         │   │
│    └──────────────────┬───────────────────────────┘   │
│                       │                               │
│    ┌──────────────────┴───────────────────────────┐   │
│    │  ESP/AH 处理  +  加密/认证算法            │   │
│    └──────────────────┬───────────────────────────┘   │
│                       │                               │
│    ┌──────────────────┴───────────────────────────┐   │
│    │           IP 协议栈                    │   │
│    └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
</pre>

<h3>应用级IPsec (Per-Socket / Per-Application)</h3>
<p>除了设备级/网关级，还可以在应用层面控制IPsec：</p>
<ul>
<li>应用程序可以通过socket API指定使用IPsec保护</li>
<li>仅保护特定应用的流量</li>
<li>适合需要细粒度控制的场景</li>
</ul>

<h3>混合部署模式推荐</h3>
<table border="1" cellpadding="5">
<tr><th>场景</th><th>推荐架构</th></tr>
<tr><td>智能家居</td><td>网关级IPsec保护所有IoT设备</td></tr>
<tr><td>远程办公</td><td>设备级IPsec + IKEv2 MOBIKE</td></tr>
<tr><td>企业分支</td><td>网关级Site-to-Site + 员工设备级Remote</td></tr>
<tr><td>双SSID网络</td><td>Guest/IoT走网关隧道，工作设备走独立客户端</td></tr>
</table>

<h3>性能考量</h3>
<ul>
<li>设备级：加解密在CPU，有负载限制</li>
<li>网关级：需要硬件加密能力，避免瓶颈</li>
<li>MTU设置：减少分片，优化性能</li>
</ul>
</content>
    }''' + content[insert_point+1:]

# 写回文件
with open('ipsec_master.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ 已成功添加用户级/设备级IPsec知识！")
print("现在知识库有27个知识点了！")
