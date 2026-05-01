import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QScrollArea, QFrame,
                             QTextEdit, QProgressBar, QGroupBox, QComboBox, QCheckBox,
                             QSpinBox, QFormLayout, QMessageBox, QSplitter, QTabWidget,
                             QRadioButton, QButtonGroup, QLineEdit, QListWidget, QListWidgetItem,
                             QGridLayout, QSizePolicy, QInputDialog, QDialog)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter


# ============ 知识数据 ============
KNOWLEDGE_DATA = {
    "IPsec概述": {
        "icon": "📖",
        "content": """<h2>IPsec (Internet Protocol Security) 概述</h2>
<p>IPsec 是一组协议，用于在 IP 层保护通信安全。它是企业网络、数据中心和云计算中 VPN 连接的基础技术。</p>

<h3>核心组件</h3>
<ul>
<li><b>IKE (Internet Key Exchange)</b>: 负责安全关联(SA)的建立和密钥协商</li>
<li><b>ESP (Encapsulating Security Payload)</b>: 提供加密和认证</li>
<li><b>AH (Authentication Header)</b>: 仅提供认证和完整性保护</li>
</ul>

<h3>工作模式</h3>
<table border="1" cellpadding="5">
<tr><th>模式</th><th>说明</th><th>使用场景</th></tr>
<tr><td>Tunnel Mode</td><td>加密整个IP包，添加新IP头</td><td>Site-to-Site VPN</td></tr>
<tr><td>Transport Mode</td><td>只加密载荷部分</td><td>Host-to-Host</td></tr>
</table>

<h3>SA (Security Association)</h3>
<p>SA是IPsec的基础，包含：SPI、目标地址、安全协议、密钥等信息。IKE负责建立和维护SA。</p>

<h3>IPsec 协议栈位置</h3>
<p>IPsec 工作在网络层（OSI 第3层），对上层应用完全透明。这意味着应用程序无需修改即可获得安全保护。</p>

<h3>RFC 参考</h3>
<ul>
<li>RFC 4301 - IPsec 安全架构</li>
<li>RFC 4302 - AH 协议</li>
<li>RFC 4303 - ESP 协议</li>
<li>RFC 7296 - IKEv2 协议</li>
</ul>"""
    },
    "IPsec安全架构": {
        "icon": "🏗️",
        "content": """<h2>IPsec 安全架构 (Security Architecture)</h2>
<p>IPsec 安全架构定义了如何将安全服务集成到 IP 层，由三个核心数据库支撑。</p>

<h3>SPD (Security Policy Database)</h3>
<p>定义哪些流量需要保护、如何保护。</p>
<ul>
<li><b>INBOUND</b>: 入方向策略</li>
<li><b>OUTBOUND</b>: 出方向策略</li>
<li>动作: <b>PROTECT</b>(加密) / <b>BYPASS</b>(放行) / <b>DISCARD</b>(丢弃)</li>
</ul>

<h3>SAD (Security Association Database)</h3>
<p>存储当前活跃的 SA 信息。</p>
<ul>
<li>SPI (Security Parameter Index) - SA 的唯一标识</li>
<li>目的 IP 地址</li>
<li>安全协议标识 (AH/ESP)</li>
<li>加密/认证算法和密钥</li>
<li>序列号计数器</li>
<li>SA 生命周期</li>
<li>模式 (Tunnel/Transport)</li>
</ul>

<h3>PAD (Peer Authorization Database)</h3>
<p>定义哪些对端被授权建立 SA，以及使用什么认证方式。</p>

<h3>处理流程</h3>
<pre>
出方向: 查SPD → 匹配PROTECT → 查SAD → 加密发送
入方向: 查SAD → 解密 → 查SPD → 验证策略
</pre>"""
    },
    "AH协议详解": {
        "icon": "🛡️",
        "content": """<h2>AH (Authentication Header) 协议详解</h2>
<p>AH 协议号为 51，提供数据完整性验证和来源认证，但<b>不提供加密</b>。</p>

<h3>AH 报文结构</h3>
<pre>
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Next Header  |  Payload Len  |          RESERVED             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Security Parameters Index (SPI)               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Sequence Number Field                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                Integrity Check Value (ICV)                    |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
</pre>

<h3>AH 认证范围</h3>
<p>AH 认证覆盖：<b>整个IP头 + AH头 + 载荷</b>（可变字段除外）</p>

<h3>AH 的局限性</h3>
<ul>
<li>不提供加密，数据明文传输</li>
<li>无法穿越 NAT（AH 保护 IP 头，NAT 修改 IP 头会破坏认证）</li>
<li>现代网络中很少单独使用</li>
</ul>

<h3>使用场景</h3>
<ul>
<li>仅需完整性验证，无需保密的场景</li>
<li>AH+ESP 组合使用（双重保护）</li>
</ul>

<h3>RFC 参考</h3>
<p>RFC 4302 - IP Authentication Header</p>"""
    },
    "ESP协议详解": {
        "icon": "🔒",
        "content": """<h2>ESP (Encapsulating Security Payload) 协议详解</h2>
<p>ESP 协议号为 50，提供加密、认证和完整性保护，是 IPsec 最常用的安全协议。</p>

<h3>ESP 报文结构</h3>
<pre>
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|               Security Parameters Index (SPI)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Sequence Number                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Payload Data (variable)                    |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Padding (0-255 bytes)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Pad Length   |       Next Header                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Integrity Check Value (ICV, variable)              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
</pre>

<h3>ESP 加密范围</h3>
<ul>
<li><b>Tunnel Mode</b>: 加密整个原始 IP 包（原始 IP 头 + 载荷）</li>
<li><b>Transport Mode</b>: 只加密载荷部分</li>
</ul>

<h3>ESP vs AH</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>AH</th><th>ESP</th></tr>
<tr><td>加密</td><td>❌</td><td>✅</td></tr>
<tr><td>认证</td><td>✅ (含IP头)</td><td>✅ (不含IP头)</td></tr>
<tr><td>NAT穿越</td><td>❌</td><td>✅ (配合NAT-T)</td></tr>
<tr><td>协议号</td><td>51</td><td>50</td></tr>
</table>

<h3>ESP 加密-认证组合推荐</h3>
<table border="1" cellpadding="5">
<tr><th>安全级别</th><th>加密</th><th>认证</th></tr>
<tr><td>标准</td><td>AES-128-CBC</td><td>HMAC-SHA-256</td></tr>
<tr><td>高安全</td><td>AES-256-CBC</td><td>HMAC-SHA-384</td></tr>
<tr><td>现代推荐</td><td>AES-256-GCM</td><td>AEAD (内置认证)</td></tr>
</table>

<h3>RFC 参考</h3>
<p>RFC 4303 - IP Encapsulating Security Payload</p>"""
    },
    "IKEv1协议详解": {
        "icon": "🔑",
        "content": """<h2>IKEv1 (Internet Key Exchange v1) 协议详解</h2>
<p>IKEv1 使用 UDP 端口 500，分为 Phase 1 和 Phase 2 两个阶段。</p>

<h3>Phase 1 - 建立 ISAKMP SA (IKE SA)</h3>
<p>目的：建立安全的控制通道，用于后续的 Phase 2 协商。</p>

<h4>Main Mode (6个报文)</h4>
<table border="1" cellpadding="5">
<tr><th>报文</th><th>方向</th><th>内容</th></tr>
<tr><td>1-2</td><td>双向</td><td>协商 IKE 提案 (加密/认证/DH组)</td></tr>
<tr><td>3-4</td><td>双向</td><td>DH 密钥交换</td></tr>
<tr><td>5-6</td><td>双向</td><td>身份认证 (加密传输)</td></tr>
</table>

<h4>Aggressive Mode (3个报文)</h4>
<table border="1" cellpadding="5">
<tr><th>报文</th><th>方向</th><th>内容</th></tr>
<tr><td>1</td><td>发起→响应</td><td>提案 + DH公开值 + 身份</td></tr>
<tr><td>2</td><td>响应→发起</td><td>接受提案 + DH公开值 + 身份</td></tr>
<tr><td>3</td><td>发起→响应</td><td>认证确认</td></tr>
</table>

<h3>Phase 2 - 建立 IPsec SA</h3>
<p>Quick Mode: 3个报文，在 Phase 1 SA 保护下协商 IPsec 参数。</p>

<h3>Main Mode vs Aggressive Mode</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>Main Mode</th><th>Aggressive Mode</th></tr>
<tr><td>报文数</td><td>6</td><td>3</td></tr>
<tr><td>身份保护</td><td>✅</td><td>❌</td></tr>
<tr><td>安全性</td><td>高</td><td>较低</td></tr>
<tr><td>速度</td><td>慢</td><td>快</td></tr>
<tr><td>适用场景</td><td>固定IP</td><td>动态IP/快速建链</td></tr>
</table>

<h3>IKEv1 的缺陷</h3>
<ul>
<li>协商流程复杂，报文数量多</li>
<li>不支持 EAP 认证</li>
<li>NAT-T 支持不完善</li>
<li>不支持 MOBIKE（移动性）</li>
<li>已逐步被 IKEv2 取代</li>
</ul>

<h3>RFC 参考</h3>
<p>RFC 2409 - The Internet Key Exchange (IKE)</p>"""
    },
    "IKEv2协议详解": {
        "icon": "🔄",
        "content": """<h2>IKEv2 协议详解</h2>
<p>IKEv2 是 IKEv1 的升级版本，简化了协商流程，增强了安全性和功能性。</p>

<h3>初始交换 (IKE_SA_INIT) - 4个报文</h3>
<table border="1" cellpadding="5">
<tr><th>报文</th><th>方向</th><th>内容</th></tr>
<tr><td>1 (IKE_SA_INIT Request)</td><td>发起→响应</td><td>SA提案 + KE(DH) + Ni(随机数)</td></tr>
<tr><td>2 (IKE_SA_INIT Response)</td><td>响应→发起</td><td>SA选择 + KE(DH) + Nr(随机数) + [COOKIE]</td></tr>
<tr><td>3 (IKE_AUTH Request)</td><td>发起→响应</td><td>IDi + AUTH + SA + TSi + TSr</td></tr>
<tr><td>4 (IKE_AUTH Response)</td><td>响应→发起</td><td>IDr + AUTH + SA + TSi + TSr</td></tr>
</table>

<h3>创建子SA交换 (CREATE_CHILD_SA) - 2个报文</h3>
<p>在 IKE SA 建立后，可随时创建新的 IPsec SA。</p>

<h3>信息交换 (INFORMATIONAL)</h3>
<p>用于删除 SA、错误通知、配置交换等。</p>

<h3>IKEv2 新增特性</h3>
<ul>
<li><b>MOBIKE</b>: 移动性支持，IP地址变化不断开VPN (RFC 4555)</li>
<li><b>EAP 认证</b>: 支持 EAP-TLS/EAP-MSCHAPv2 等</li>
<li><b>Cookie 机制</b>: 防止 DoS 攻击</li>
<li><b>原生 NAT-T</b>: 无需额外配置</li>
<li><b>配置载荷 (CP)</b>: 远端地址分配</li>
<li><b>重定向机制</b>: 负载均衡 (RFC 5685)</li>
<li><b>多认证</b>: 支持双重认证 (RFC 4739)</li>
</ul>

<h3>IKEv1 vs IKEv2 对比</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>IKEv1</th><th>IKEv2</th></tr>
<tr><td>初始交换报文</td><td>6 (Main) / 3 (Aggressive)</td><td>4</td></tr>
<tr><td>子SA创建</td><td>3 (Quick Mode)</td><td>2</td></tr>
<tr><td>NAT穿越</td><td>需要额外配置</td><td>原生支持</td></tr>
<tr><td>MOBIKE</td><td>不支持</td><td>支持</td></tr>
<tr><td>EAP</td><td>不支持</td><td>支持</td></tr>
<tr><td>DoS防护</td><td>无</td><td>Cookie机制</td></tr>
<tr><td>可靠性</td><td>无确认机制</td><td>请求-响应确认</td></tr>
</table>

<h3>RFC 参考</h3>
<p>RFC 7296 - Internet Key Exchange Protocol Version 2 (IKEv2)</p>"""
    },
    "ISAKMP框架": {
        "icon": "📋",
        "content": """<h2>ISAKMP 框架详解</h2>
<p>ISAKMP (Internet Security Association and Key Management Protocol) 定义了 SA 管理和密钥交换的框架。</p>

<h3>ISAKMP 与 IKE 的关系</h3>
<p>ISAKMP 是框架，IKE 是基于此框架的具体实现。IKE 使用 ISAKMP 定义的消息格式和流程。</p>

<h3>ISAKMP 载荷类型</h3>
<table border="1" cellpadding="5">
<tr><th>载荷类型</th><th>值</th><th>说明</th></tr>
<tr><td>SA</td><td>1</td><td>安全关联提案</td></tr>
<tr><td>KE</td><td>4</td><td>Diffie-Hellman 公开值</td></tr>
<tr><td>IDi / IDr</td><td>5/6</td><td>发起方/响应方身份</td></tr>
<tr><td>CERT</td><td>6</td><td>数字证书</td></tr>
<tr><td>CERTREQ</td><td>7</td><td>证书请求</td></tr>
<tr><td>AUTH</td><td>9</td><td>认证数据</td></tr>
<tr><td>Nonce</td><td>10</td><td>随机数</td></tr>
<tr><td>Notify</td><td>11</td><td>通知消息</td></tr>
<tr><td>Delete</td><td>12</td><td>SA 删除通知</td></tr>
<tr><td>Vendor ID</td><td>13</td><td>厂商标识</td></tr>
<tr><td>TSi / TSr</td><td>44/45</td><td>流量选择器(IKEv2)</td></tr>
</table>

<h3>DOI (Domain of Interpretation)</h3>
<p>DOI 定义了特定安全域的参数。IPsec DOI 值为 1。</p>

<h3>RFC 参考</h3>
<p>RFC 2408 - Internet Security Association and Key Management Protocol (ISAKMP)</p>"""
    },
    "SA安全关联": {
        "icon": "🔗",
        "content": """<h2>SA (Security Association) 安全关联详解</h2>
<p>SA 是 IPsec 的核心概念，定义了通信双方使用的安全参数集合。</p>

<h3>SA 三元组标识</h3>
<p>每个 SA 由以下三元组唯一标识：</p>
<ul>
<li><b>SPI (Security Parameter Index)</b>: 32位随机数，标识SA</li>
<li><b>目的 IP 地址</b>: SA 终点的IP地址</li>
<li><b>安全协议标识</b>: AH 或 ESP</li>
</ul>

<h3>SA 参数</h3>
<table border="1" cellpadding="5">
<tr><th>参数</th><th>说明</th></tr>
<tr><td>加密算法 + 密钥</td><td>AES/3DES 等 + 对应密钥</td></tr>
<tr><td>认证算法 + 密钥</td><td>HMAC-SHA256 等 + 对应密钥</td></tr>
<tr><td>序列号</td><td>防重放攻击计数器</td></tr>
<tr><td>抗重放窗口</td><td>接收方滑动窗口大小</td></tr>
<tr><td>SA 生命周期</td><td>时间/流量限制</td></tr>
<tr><td>IPsec 模式</td><td>Tunnel / Transport</td></tr>
<tr><td>PMTU</td><td>路径最大传输单元</td></tr>
</table>

<h3>SA 类型</h3>
<ul>
<li><b>IKE SA (ISAKMP SA)</b>: Phase 1 建立，保护控制平面</li>
<li><b>IPsec SA</b>: Phase 2 建立，保护数据平面，<b>单向的</b>！</li>
</ul>

<h3>SA 生命周期</h3>
<pre>
创建 → 使用 → 软超时(开始重协商) → 硬超时(删除SA)
</pre>

<h3>重协商机制</h3>
<ul>
<li>基于时间: 默认 IKE SA 86400s, IPsec SA 3600s</li>
<li>基于流量: 如 4096000 KB</li>
<li>重协商在软超时时触发，硬超时时强制删除</li>
</ul>"""
    },
    "加密算法详解": {
        "icon": "🔐",
        "content": """<h2>加密算法详解</h2>

<h3>对称加密算法</h3>
<table border="1" cellpadding="5">
<tr><th>算法</th><th>密钥长度</th><th>分组模式</th><th>安全性</th><th>性能</th><th>推荐</th></tr>
<tr><td>DES</td><td>56 bit</td><td>CBC</td><td>❌ 已破解</td><td>快</td><td>❌</td></tr>
<tr><td>3DES</td><td>168 bit</td><td>CBC</td><td>⚠️ 逐步淘汰</td><td>慢</td><td>❌</td></tr>
<tr><td>AES-128-CBC</td><td>128 bit</td><td>CBC</td><td>✅ 安全</td><td>快</td><td>✅</td></tr>
<tr><td>AES-256-CBC</td><td>256 bit</td><td>CBC</td><td>✅ 高安全</td><td>中</td><td>✅</td></tr>
<tr><td>AES-128-GCM</td><td>128 bit</td><td>GCM</td><td>✅✅ AEAD</td><td>快</td><td>✅✅</td></tr>
<tr><td>AES-256-GCM</td><td>256 bit</td><td>GCM</td><td>✅✅ AEAD</td><td>中</td><td>✅✅</td></tr>
<tr><td>ChaCha20-Poly1305</td><td>256 bit</td><td>流密码</td><td>✅✅ AEAD</td><td>快</td><td>✅✅</td></tr>
</table>

<h3>AEAD (Authenticated Encryption with Associated Data)</h3>
<p>AEAD 算法将加密和认证合二为一，如 AES-GCM、ChaCha20-Poly1305。</p>
<ul>
<li>优势: 一次操作完成加密+认证，效率更高</li>
<li>推荐: AES-256-GCM 或 ChaCha20-Poly1305</li>
</ul>

<h3>CBC vs GCM 模式</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>CBC</th><th>GCM</th></tr>
<tr><td>认证</td><td>需单独HMAC</td><td>内置认证</td></tr>
<tr><td>并行加密</td><td>❌</td><td>✅</td></tr>
<tr><td>并行解密</td><td>✅</td><td>✅</td></tr>
<tr><td>性能</td><td>中</td><td>高(有硬件加速)</td></tr>
<tr><td>填充</td><td>需要</td><td>不需要</td></tr>
</table>

<h3>密钥长度与安全等级</h3>
<table border="1" cellpadding="5">
<tr><th>对称密钥</th><th>等效RSA</th><th>等效ECC</th><th>安全等级</th></tr>
<tr><td>128 bit</td><td>3072 bit</td><td>256 bit</td><td>标准</td></tr>
<tr><td>192 bit</td><td>7680 bit</td><td>384 bit</td><td>高</td></tr>
<tr><td>256 bit</td><td>15360 bit</td><td>521 bit</td><td>极高</td></tr>
</table>

<h3>RFC 参考</h3>
<ul>
<li>RFC 4309 - AES-CCM / AES-GCM for ESP</li>
<li>RFC 7634 - ChaCha20-Poly1305 for IPsec</li>
</ul>"""
    },
    "认证与完整性算法": {
        "icon": "🔏",
        "content": """<h2>认证与完整性算法详解</h2>

<h3>HMAC 算法</h3>
<table border="1" cellpadding="5">
<tr><th>算法</th><th>哈希长度</th><th>截断长度</th><th>安全性</th><th>推荐</th></tr>
<tr><td>HMAC-MD5</td><td>128 bit</td><td>96 bit</td><td>❌ 已破解</td><td>❌</td></tr>
<tr><td>HMAC-SHA-1</td><td>160 bit</td><td>96 bit</td><td>⚠️ 逐步淘汰</td><td>❌</td></tr>
<tr><td>HMAC-SHA-256</td><td>256 bit</td><td>128 bit</td><td>✅ 推荐</td><td>✅</td></tr>
<tr><td>HMAC-SHA-384</td><td>384 bit</td><td>192 bit</td><td>✅ 高安全</td><td>✅</td></tr>
<tr><td>HMAC-SHA-512</td><td>512 bit</td><td>256 bit</td><td>✅ 极高安全</td><td>✅</td></tr>
</table>

<h3>HMAC 工作原理</h3>
<pre>
HMAC(K, m) = H((K' ⊕ opad) || H((K' ⊕ ipad) || m))

K' = 密钥填充到块大小
ipad = 0x36 重复
opad = 0x5C 重复
</pre>

<h3>AEAD 内置认证</h3>
<p>使用 AES-GCM 或 ChaCha20-Poly1305 时，不需要单独的认证算法，AEAD 自带认证功能。</p>

<h3>PRF (Pseudo-Random Function)</h3>
<p>IKEv2 中用于密钥材料生成的伪随机函数：</p>
<ul>
<li>PRF_HMAC_SHA1 (默认)</li>
<li>PRF_HMAC_SHA2-256</li>
<li>PRF_HMAC_SHA2-384</li>
<li>PRF_HMAC_SHA2-512</li>
</ul>

<h3>RFC 参考</h3>
<ul>
<li>RFC 4868 - HMAC-SHA-256/384/512 for IPsec</li>
<li>RFC 2404 - HMAC-SHA-1-96 for ESP/AH</li>
</ul>"""
    },
    "DH密钥交换": {
        "icon": "🤝",
        "content": """<h2>Diffie-Hellman (DH) 密钥交换详解</h2>
<p>DH 密钥交换允许双方在不安全的信道上协商出共享密钥。</p>

<h3>DH 工作原理</h3>
<pre>
Alice: 生成私钥 a, 计算公钥 A = g^a mod p
Bob:   生成私钥 b, 计算公钥 B = g^b mod p
交换公钥 A 和 B
共享密钥: Alice 计算 B^a mod p = g^(ab) mod p
          Bob   计算 A^b mod p = g^(ab) mod p
</pre>

<h3>DH Group 一览</h3>
<table border="1" cellpadding="5">
<tr><th>Group</th><th>类型</th><th>位数</th><th>安全性</th><th>推荐</th></tr>
<tr><td>1</td><td>MODP</td><td>768 bit</td><td>❌ 已破解</td><td>❌</td></tr>
<tr><td>2</td><td>MODP</td><td>1024 bit</td><td>❌ 弱</td><td>❌</td></tr>
<tr><td>5</td><td>MODP</td><td>1536 bit</td><td>⚠️ 一般</td><td>❌</td></tr>
<tr><td>14</td><td>MODP</td><td>2048 bit</td><td>✅ 推荐</td><td>✅</td></tr>
<tr><td>15</td><td>MODP</td><td>3072 bit</td><td>✅ 高安全</td><td>✅</td></tr>
<tr><td>16</td><td>MODP</td><td>4096 bit</td><td>✅ 极高安全</td><td>✅</td></tr>
<tr><td>19</td><td>ECP</td><td>256 bit</td><td>✅ 推荐</td><td>✅✅</td></tr>
<tr><td>20</td><td>ECP</td><td>384 bit</td><td>✅ 高安全</td><td>✅✅</td></tr>
<tr><td>21</td><td>ECP</td><td>521 bit</td><td>✅ 极高安全</td><td>✅✅</td></tr>
<tr><td>31</td><td>Curve25519</td><td>255 bit</td><td>✅✅ 现代推荐</td><td>✅✅</td></tr>
<tr><td>32</td><td>Curve448</td><td>448 bit</td><td>✅✅ 极高安全</td><td>✅✅</td></tr>
</table>

<h3>MODP vs ECP</h3>
<ul>
<li><b>MODP</b>: 基于模幂运算，计算量大，密钥长</li>
<li><b>ECP</b>: 基于椭圆曲线，同等安全下密钥更短，计算更快</li>
<li><b>Curve25519/448</b>: 现代椭圆曲线，性能和安全性最优</li>
</ul>

<h3>完美前向保密 (PFS)</h3>
<p>Phase 2 也进行 DH 交换，确保即使 IKE SA 密钥泄露，IPsec SA 的数据仍然安全。</p>

<h3>RFC 参考</h3>
<ul>
<li>RFC 3526 - MODP Groups for IKE</li>
<li>RFC 5903 - ECP Groups for IKE</li>
<li>RFC 8031 - Curve25519/448 for IKEv2</li>
</ul>"""
    },
    "认证方式详解": {
        "icon": "🗝️",
        "content": """<h2>IPsec 认证方式详解</h2>

<h3>预共享密钥 (PSK)</h3>
<p>双方预先配置相同的密钥字符串。</p>
<ul>
<li>✅ 配置简单</li>
<li>✅ 适合小规模部署</li>
<li>❌ 密钥管理困难（大规模）</li>
<li>❌ 密钥泄露风险高</li>
</ul>

<h3>数字证书 (PKI)</h3>
<p>使用 X.509 数字证书进行认证。</p>
<ul>
<li>✅ 安全性高</li>
<li>✅ 可扩展，适合大规模部署</li>
<li>✅ 支持证书撤销 (CRL/OCSP)</li>
<li>❌ 需要 CA 基础设施</li>
<li>❌ 配置复杂</li>
</ul>

<h3>EAP 认证 (IKEv2)</h3>
<p>IKEv2 支持 EAP 扩展认证协议。</p>
<table border="1" cellpadding="5">
<tr><th>EAP 方法</th><th>说明</th><th>场景</th></tr>
<tr><td>EAP-TLS</td><td>基于证书的双向认证</td><td>高安全要求</td></tr>
<tr><td>EAP-MSCHAPv2</td><td>基于用户名密码</td><td>远程接入</td></tr>
<tr><td>EAP-TTLS</td><td>隧道TLS认证</td><td>兼容性好</td></tr>
<tr><td>EAP-PEAP</td><td>受保护的EAP</td><td>企业环境</td></tr>
</table>

<h3>数字签名 (RSA/ECDSA)</h3>
<p>使用私钥签名、公钥验证。</p>
<ul>
<li>RSA 签名: 兼容性最好</li>
<li>ECDSA 签名: 密钥更短，性能更好</li>
</ul>

<h3>认证方式选择建议</h3>
<table border="1" cellpadding="5">
<tr><th>场景</th><th>推荐方式</th></tr>
<tr><td>Site-to-Site (少量)</td><td>PSK</td></tr>
<tr><td>Site-to-Site (大量)</td><td>数字证书</td></tr>
<tr><td>远程接入</td><td>EAP + 数字证书</td></tr>
<tr><td>高安全要求</td><td>双重认证 (证书+EAP)</td></tr>
</table>"""
    },
    "PKI与数字证书": {
        "icon": "📜",
        "content": """<h2>PKI 与数字证书详解</h2>

<h3>PKI 体系架构</h3>
<ul>
<li><b>CA (Certificate Authority)</b>: 证书颁发机构</li>
<li><b>RA (Registration Authority)</b>: 注册机构</li>
<li><b>CRL/OCSP</b>: 证书撤销机制</li>
<li><b>Certificate Database</b>: 证书存储库</li>
</ul>

<h3>X.509 证书结构</h3>
<pre>
Version: V3
Serial Number: 0x01
Issuer: CN=IPsec-CA
Validity: Not Before - Not After
Subject: CN=GW-01
Public Key Info:
  Algorithm: RSA/ECDSA
  Public Key: (公钥数据)
Extensions:
  Subject Alt Name: IP:10.1.1.1
  Key Usage: Digital Signature, Key Encipherment
  Extended Key Usage: IPsec Tunnel / IPsec User
Signature Algorithm: SHA256withRSA
Signature: (CA签名)
</pre>

<h3>证书认证流程</h3>
<pre>
1. 发起方发送 CERT 载荷（自己的证书）
2. 响应方验证证书链 → 检查CA签名 → 检查有效期
3. 检查 CRL/OCSP → 确认证书未被撤销
4. 使用证书公钥验证 AUTH 载荷中的签名
</pre>

<h3>自签名 CA vs 公共 CA</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>自签名CA</th><th>公共CA</th></tr>
<tr><td>成本</td><td>免费</td><td>收费</td></tr>
<tr><td>管理</td><td>自行管理</td><td>CA管理</td></tr>
<tr><td>适用</td><td>内部VPN</td><td>跨组织VPN</td></tr>
<tr><td>信任</td><td>需手动导入</td><td>系统预置</td></tr>
</table>

<h3>RFC 参考</h3>
<ul>
<li>RFC 4945 - IPsec Certificate Profile</li>
<li>RFC 5280 - X.509 PKI Certificate and CRL Profile</li>
</ul>"""
    },
    "NAT穿越详解": {
        "icon": "🌐",
        "content": """<h2>NAT 穿越 (NAT Traversal) 详解</h2>
<p>当 IPsec 网关位于 NAT 设备后方时，需要特殊处理。</p>

<h3>问题分析</h3>
<ul>
<li>ESP 协议 (IP 协议 50) 没有端口号，NAT 无法正确转换</li>
<li>AH 协议会被 NAT 修改破坏（因为AH保护整个IP头）</li>
<li>NAT 修改 IP 地址后，IKE 通信地址与实际不匹配</li>
</ul>

<h3>NAT-T 解决方案</h3>
<ol>
<li><b>NAT-D (NAT Detection)</b>: 检测路径上是否存在 NAT</li>
<li><b>UDP 封装</b>: 将 ESP 包封装在 UDP 4500 端口中</li>
<li><b>Keepalive</b>: 保持 NAT 映射表项不过期</li>
</ol>

<h3>NAT-T 协商流程</h3>
<pre>
1. IKE 协商时双方发送 NAT-D 载荷
2. 检测到 NAT → 协商使用 UDP 封装
3. 后续 ESP 报文封装在 UDP 4500 中
4. 定期发送 NAT Keepalive (默认20s)
</pre>

<h3>UDP 封装格式</h3>
<pre>
| IP头 | UDP头(4500) | SPI(0=Keepalive) | ESP报文 |
</pre>

<h3>配置要点</h3>
<pre>
# 启用 NAT-T
nat-traversal enable
ikev2 nat-detect

# NAT 后的 Keepalive
nat keepalive 20

# DPD 配置
dpd interval 30
dpd retry 5
</pre>

<h3>NAT 场景分类</h3>
<table border="1" cellpadding="5">
<tr><th>场景</th><th>NAT类型</th><th>配置建议</th></tr>
<tr><td>总部公网-分支NAT后</td><td>单向NAT</td><td>分支发起连接</td></tr>
<tr><td>双方都在NAT后</td><td>双向NAT</td><td>IKEv2 + NAT-T</td></tr>
<tr><td>移动用户</td><td>CGN</td><td>IKEv2 + EAP + NAT-T</td></tr>
</table>

<h3>RFC 参考</h3>
<p>RFC 3947/3948 - UDP Encapsulation of IPsec ESP Packets</p>"""
    },
    "DPD与隧道维护": {
        "icon": "📡",
        "content": """<h2>DPD (Dead Peer Detection) 与隧道维护</h2>
<p>DPD 用于检测 IPsec 对端是否存活。</p>

<h3>工作机制</h3>
<ul>
<li><b>Periodic 模式</b>: 定时发送 DPD 请求</li>
<li><b>On-demand 模式</b>: 有数据发送时才检测</li>
</ul>

<h3>配置参数</h3>
<pre>
# DPD 配置
ike peer PEER1
 dpd type periodic
 dpd interval 30
 dpd timeout 15
 dpd retry 5
</pre>

<h3>建议值</h3>
<table border="1" cellpadding="5">
<tr><th>场景</th><th>Interval</th><th>Retry</th><th>Timeout</th></tr>
<tr><td>稳定网络</td><td>60s</td><td>5</td><td>30s</td></tr>
<tr><td>移动网络</td><td>30s</td><td>3</td><td>10s</td></tr>
<tr><td>高可靠要求</td><td>10s</td><td>3</td><td>5s</td></tr>
</table>

<h3>隧道维护机制</h3>
<ul>
<li><b>SA 重协商</b>: 软超时触发重协商</li>
<li><b>Anti-Replay</b>: 抗重放窗口（默认64）</li>
<li><b>Keepalive</b>: 保持 NAT 映射</li>
<li><b>Fragmentation</b>: IKE 分片 (RFC 7383)</li>
</ul>

<h3>Anti-Replay 窗口</h3>
<p>接收方维护滑动窗口，丢弃序列号在窗口外的旧报文或重复报文。</p>
<pre>
窗口大小: 32/64/128/256
推荐: 64 (平衡内存和安全)
</pre>"""
    },
    "高可用与故障切换": {
        "icon": "🔄",
        "content": """<h2>高可用 (High Availability) 详解</h2>

<h3>实现方式</h3>
<ul>
<li><b>VRRP/HSRP</b>: 虚拟网关冗余</li>
<li><b>双活 IPsec</b>: 两条 IPsec 隧道同时运行</li>
<li><b>IPsec NSR</b>: 状态热备份</li>
</ul>

<h3>VRRP + IPsec</h3>
<pre>
# VRRP 配置
interface GigabitEthernet0/0/1
 vrrp vrid 1 virtual-ip 10.0.0.254
 vrrp vrid 1 priority 120

# IPsec 策略绑定 VRRP
ipsec policy POLICY1 vrrp-aware
</pre>

<h3>NSR (Non-Stop Routing)</h3>
<p>NSR 确保 SA 状态实时同步到备机：</p>
<ul>
<li>IKE SA 同步</li>
<li>IPsec SA 同步</li>
<li>序列号同步</li>
<li>DPD 状态同步</li>
</ul>

<h3>故障切换流程</h3>
<pre>
1. 主设备故障 → VRRP 切换
2. 备设备升为主设备
3. 使用同步的 SA 继续加密/解密
4. 对端无感知（无缝切换）
</pre>

<h3>注意事项</h3>
<ul>
<li>确保两端 SPI 同步</li>
<li>使用 DPD 检测隧道状态</li>
<li>合理设置 SA 生命周期</li>
<li>备机需预配置相同的 IKE/IPsec 参数</li>
</ul>"""
    },
    "IPsec与IPv6": {
        "icon": "🔢",
        "content": """<h2>IPsec 与 IPv6</h2>

<h3>IPv6 中的 IPsec</h3>
<p>IPv6 最初设计时要求 IPsec 支持为强制项，后改为推荐项。但 IPsec 仍然是 IPv6 安全的重要组成。</p>

<h3>IPv6 与 IPv4 的 IPsec 差异</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>IPv4</th><th>IPv6</th></tr>
<tr><td>IPsec 支持</td><td>可选</td><td>推荐</td></tr>
<tr><td>地址长度</td><td>32 bit</td><td>128 bit</td></tr>
<tr><td>NAT 需求</td><td>普遍</td><td>极少</td></tr>
<tr><td>扩展头</td><td>无</td><td>AH/ESP作为扩展头</td></tr>
<tr><td>端到端加密</td><td>受NAT影响</td><td>原生支持</td></tr>
</table>

<h3>IPv6 扩展头顺序</h3>
<pre>
IPv6头 → Hop-by-Hop → Destination → Routing → Fragment → AH → ESP → Destination → 上层协议
</pre>

<h3>IPv6 IPsec 优势</h3>
<ul>
<li>地址空间充足，无需 NAT，更适合端到端 IPsec</li>
<li>扩展头机制使 IPsec 集成更自然</li>
<li>IKEv2 原生支持 IPv6 地址</li>
</ul>

<h3>RFC 参考</h3>
<ul>
<li>RFC 4301 - IPsec for IPv6</li>
<li>RFC 4890 - Recommendations for IPsec in IPv6</li>
</ul>"""
    },
    "IPsec与SD-WAN": {
        "icon": "☁️",
        "content": """<h2>IPsec 与 SD-WAN</h2>

<h3>SD-WAN 中的 IPsec</h3>
<p>SD-WAN 使用 IPsec 作为底层安全传输机制，实现多链路加密和智能选路。</p>

<h3>SD-WAN IPsec 特点</h3>
<ul>
<li><b>自动隧道建立</b>: 控制器自动下发 IPsec 配置</li>
<li><b>多链路负载</b>: 多条 IPsec 隧道并行</li>
<li><b>动态选路</b>: 根据链路质量自动切换</li>
<li><b>集中管理</b>: 统一密钥分发和策略管理</li>
</ul>

<h3>SD-WAN IPsec 架构</h3>
<pre>
          +----------+
          | 控制器    |
          | (Controller)|
          +-----+----+
                | 自动下发配置
    +-----------+-----------+
    |                       |
+---+---+              +---+---+
| CPE-1  |---IPsec---| CPE-2  |
| MPLS   |---IPsec---| Internet|
| LTE    |---IPsec---| LTE    |
+--------+              +--------+
</pre>

<h3>SD-WAN vs 传统 IPsec VPN</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>传统IPsec</th><th>SD-WAN IPsec</th></tr>
<tr><td>隧道建立</td><td>手动配置</td><td>自动建立</td></tr>
<tr><td>密钥管理</td><td>手动/PSK</td><td>自动分发</td></tr>
<tr><td>多链路</td><td>主备切换</td><td>负载均衡</td></tr>
<tr><td>选路</td><td>静态路由</td><td>智能选路</td></tr>
<tr><td>监控</td><td>SNMP/CLI</td><td>可视化面板</td></tr>
</table>

<h3>RFC 参考</h3>
<p>RFC 8206 - SD-WAN Security Considerations</p>"""
    },
    "IPsec性能优化": {
        "icon": "⚡",
        "content": """<h2>IPsec 性能优化</h2>

<h3>性能瓶颈分析</h3>
<ul>
<li><b>CPU</b>: 加密/认证运算消耗大</li>
<li><b>内存</b>: SA 存储、抗重放窗口</li>
<li><b>带宽</b>: ESP/AH 增加报文开销</li>
<li><b>延迟</b>: 加解密处理时间</li>
</ul>

<h3>硬件加速</h3>
<table border="1" cellpadding="5">
<tr><th>技术</th><th>说明</th><th>加速比</th></tr>
<tr><td>AES-NI</td><td>CPU内置AES指令集</td><td>5-10x</td></tr>
<tr><td>IPsec 引擎</td><td>专用加密芯片</td><td>10-50x</td></tr>
<tr><td>SmartNIC</td><td>智能网卡卸载</td><td>20-100x</td></tr>
<tr><td>DPDK</td><td>用户态快速处理</td><td>5-20x</td></tr>
</table>

<h3>算法选择优化</h3>
<ul>
<li>优先使用 AES-GCM (AEAD，一次完成加密+认证)</li>
<li>使用 ECP DH Group (比 MODP 更快)</li>
<li>避免使用 3DES (性能差)</li>
</ul>

<h3>SA 优化</h3>
<ul>
<li>增大 SA 生命周期，减少重协商次数</li>
<li>使用 IPsec SA 聚合 (多流量共享SA)</li>
<li>合理设置抗重放窗口大小</li>
</ul>

<h3>MTU 优化</h3>
<pre>
标准MTU: 1500
ESP开销: ~60 bytes (Tunnel + AES-CBC + SHA256)
建议MTU: 1400 (预留足够空间，避免分片)
</pre>

<h3>连接数优化</h3>
<ul>
<li>使用 IKEv2 减少协商报文</li>
<li>使用 CREATE_CHILD_SA 复用 IKE SA</li>
<li>合理规划 IPsec 策略数量</li>
</ul>"""
    },
    "IPsec故障排查": {
        "icon": "🔍",
        "content": """<h2>IPsec 故障排查</h2>

<h3>常见故障分类</h3>
<table border="1" cellpadding="5">
<tr><th>阶段</th><th>常见问题</th></tr>
<tr><td>IKE Phase 1</td><td>提案不匹配、认证失败、地址不可达</td></tr>
<tr><td>IKE Phase 2</td><td>ACL不匹配、IPsec提案不匹配、PFS不匹配</td></tr>
<tr><td>数据传输</td><td>路由问题、MTU问题、NAT问题</td></tr>
<tr><td>隧道维护</td><td>SA超时、DPD断开、重协商失败</td></tr>
</table>

<h3>排查步骤</h3>
<pre>
1. 检查物理连通性 (ping 对端IP)
2. 检查 IKE 提案是否匹配
3. 检查认证方式 (PSK/证书)
4. 检查 IPsec 提案是否匹配
5. 检查 ACL/流量选择器
6. 检查路由配置
7. 检查 NAT-T 配置
8. 检查 DPD 配置
</pre>

<h3>常用调试命令</h3>
<pre>
# 查看 IKE SA
display ike sa

# 查看 IPsec SA
display ipsec sa

# 查看 IPsec 统计
display ipsec statistics

# 开启调试
debugging ike event
debugging ipsec event

# 测试连通性
ping -a 192.168.1.1 192.168.2.1
</pre>

<h3>常见错误码</h3>
<table border="1" cellpadding="5">
<tr><th>错误</th><th>原因</th><th>解决</th></tr>
<tr><td>No Proposal Chosen</td><td>IKE提案不匹配</td><td>检查加密/认证/DH参数</td></tr>
<tr><td>Authentication Failed</td><td>PSK不匹配或证书无效</td><td>检查密钥/证书</td></tr>
<tr><td>Invalid ID</td><td>身份标识不匹配</td><td>检查peer地址/名称</td></tr>
<tr><td>No Policy Found</td><td>ACL不匹配</td><td>检查感兴趣流</td></tr>
</table>"""
    },
    "IPsec安全最佳实践": {
        "icon": "✅",
        "content": """<h2>IPsec 安全最佳实践</h2>

<h3>算法选择</h3>
<table border="1" cellpadding="5">
<tr><th>参数</th><th>推荐</th><th>不推荐</th></tr>
<tr><td>加密</td><td>AES-256-GCM</td><td>DES/3DES/NULL</td></tr>
<tr><td>认证</td><td>SHA-256+</td><td>MD5/SHA-1</td></tr>
<tr><td>DH Group</td><td>Group 14+/ECP</td><td>Group 1/2/5</td></tr>
<tr><td>PRF</td><td>PRF-HMAC-SHA256</td><td>PRF-HMAC-MD5</td></tr>
</table>

<h3>密钥管理</h3>
<ul>
<li>PSK 至少 24 个字符，包含大小写+数字+特殊字符</li>
<li>每个 Peer 使用不同的 PSK</li>
<li>定期轮换 PSK（建议每90天）</li>
<li>大规模部署使用数字证书</li>
<li>启用 PFS (Perfect Forward Secrecy)</li>
</ul>

<h3>SA 管理</h3>
<ul>
<li>IKE SA 生命周期: 86400s (24h)</li>
<li>IPsec SA 生命周期: 3600s (1h)</li>
<li>启用 Anti-Replay</li>
<li>启用 DPD</li>
</ul>

<h3>网络安全</h3>
<ul>
<li>限制 IKE 只接受已知 Peer 的连接</li>
<li>使用 ACL 限制 IPsec 保护的业务流量</li>
<li>启用 IKEv2 Cookie 防护 (防DoS)</li>
<li>定期审计 IPsec 策略</li>
<li>监控 IPsec 隧道状态</li>
</ul>

<h3>合规要求</h3>
<ul>
<li>等保2.0: 要求使用国密算法或 AES-256+</li>
<li>GDPR: 传输加密要求</li>
<li>PCI DSS: 强加密要求</li>
</ul>"""
    },
    "IPsec安全攻击与防护": {
        "icon": "⚔️",
        "content": """<h2>IPsec 安全攻击与防护</h2>

<h3>已知攻击类型</h3>

<h4>1. IKE 暴力破解</h4>
<ul>
<li>攻击: 对 PSK 进行字典/暴力破解</li>
<li>防护: 使用强 PSK (24+字符) 或数字证书</li>
</ul>

<h4>2. DDoS 攻击</h4>
<ul>
<li>攻击: 大量 IKE_SA_INIT 请求消耗资源</li>
<li>防护: IKEv2 Cookie 机制、限速</li>
</ul>

<h4>3. 中间人攻击 (MITM)</h4>
<ul>
<li>攻击: 拦截 IKE 协商，伪造身份</li>
<li>防护: 使用数字证书认证、启用 MOBIKE 检测</li>
</ul>

<h4>4. 重放攻击</h4>
<ul>
<li>攻击: 重新发送截获的合法报文</li>
<li>防护: Anti-Replay 窗口、序列号检查</li>
</ul>

<h4>5. Oracle Padding Attack</h4>
<ul>
<li>攻击: 利用 CBC 模式填充验证信息</li>
<li>防护: 使用 AEAD 模式 (GCM) 替代 CBC</li>
</ul>

<h4>6. Downgrade Attack</h4>
<ul>
<li>攻击: 强制协商使用弱算法</li>
<li>防护: 配置严格算法策略、IKEv2 签名确认</li>
</ul>

<h3>IKEv2 安全增强</h3>
<ul>
<li>Cookie 机制防 DoS</li>
<li>签名确认防降级攻击</li>
<li>EAP 认证增强身份验证</li>
<li>多认证 (RFC 4739)</li>
</ul>

<h3>RFC 参考</h3>
<ul>
<li>RFC 7427 - IKEv2 Authentication Method Signatures</li>
<li>RFC 8019 - Protecting IKEv2 Against DoS Attacks</li>
</ul>"""
    },
    "IPsec配置实例": {
        "icon": "📝",
        "content": """<h2>IPsec 配置实例</h2>

<h3>实例1: Site-to-Site VPN (IKEv2 + PSK)</h3>
<pre>
# === 总部配置 ===
ike proposal PROP1
 encryption-algorithm aes-256
 authentication-algorithm sha2-256
 dh group14
 prf hmac-sha2-256
 sa duration 86400

ike peer BRANCH
 ikev2 proposal PROP1
 address 202.100.2.2
 pre-shared-key Cipher Str0ng!PSK#2024
 dpd type periodic
 dpd interval 30
 dpd retry 5
 nat-traversal

ipsec proposal PROP1
 encapsulation-mode tunnel
 transform esp
 esp encryption-algorithm aes-256
 esp authentication-algorithm sha2-256

acl number 3000
 rule 5 permit ip source 192.168.1.0 0.0.0.255 destination 192.168.2.0 0.0.0.255

ipsec policy POLICY1 1 isakmp
 security acl 3000
 ike-peer BRANCH
 proposal PROP1
 sa duration time-based 3600

interface GigabitEthernet0/0/1
 ipsec policy POLICY1
</pre>

<h3>实例2: 远程接入 VPN (IKEv2 + EAP)</h3>
<pre>
ike proposal PROP1
 encryption-algorithm aes-256-gcm
 dh group19

ike peer REMOTE_USERS
 ikev2 proposal PROP1
 authentication-method eap
 eap-method eap-mschapv2
 certificate local-cert SERVER_CERT
 nat-traversal

ipsec proposal PROP1
 encapsulation-mode tunnel
 transform esp
 esp encryption-algorithm aes-256-gcm

ipsec policy-template TEMP1 1
 ike-peer REMOTE_USERS
 proposal PROP1

ipsec policy REMOTE_POLICY 1 isakmp template TEMP1
</pre>

<h3>实例3: GRE over IPsec</h3>
<pre>
interface Tunnel0
 ip address 10.10.10.1 255.255.255.0
 tunnel-protocol gre
 source GigabitEthernet0/0/1
 destination 202.100.2.2

acl number 3000
 rule 5 permit gre source 202.100.1.1 0 destination 202.100.2.2 0

ipsec policy GRE_POLICY 1 isakmp
 security acl 3000
 ike-peer BRANCH
 proposal PROP1
</pre>"""
    },
    "IPsec与其他VPN技术对比": {
        "icon": "⚖️",
        "content": """<h2>IPsec 与其他 VPN 技术对比</h2>

<h3>主流 VPN 技术对比</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>IPsec</th><th>SSL/TLS VPN</th><th>WireGuard</th><th>OpenVPN</th></tr>
<tr><td>OSI层</td><td>网络层(L3)</td><td>应用层(L7)</td><td>网络层(L3)</td><td>应用层(L7)</td></tr>
<tr><td>协议</td><td>ESP/AH/IKE</td><td>TLS 1.3</td><td>UDP + Noise</td><td>UDP/TCP + TLS</td></tr>
<tr><td>加密</td><td>AES/ChaCha20</td><td>AES/ChaCha20</td><td>ChaCha20</td><td>AES/ChaCha20</td></tr>
<tr><td>认证</td><td>PSK/证书/EAP</td><td>证书/用户名密码</td><td>公钥</td><td>证书/PSK</td></tr>
<tr><td>NAT穿越</td><td>NAT-T</td><td>原生支持</td><td>原生支持</td><td>原生支持</td></tr>
<tr><td>配置复杂度</td><td>高</td><td>中</td><td>低</td><td>中</td></tr>
<tr><td>性能</td><td>高(硬件加速)</td><td>中</td><td>高</td><td>中</td></tr>
<tr><td>互操作性</td><td>高(标准协议)</td><td>高</td><td>低</td><td>中</td></tr>
<tr><td>移动性</td><td>IKEv2 MOBIKE</td><td>好</td><td>好</td><td>好</td></tr>
</table>

<h3>IPsec 优势</h3>
<ul>
<li>网络层加密，对应用透明</li>
<li>硬件加速支持好</li>
<li>多厂商互操作性强</li>
<li>支持 Site-to-Site 和远程接入</li>
</ul>

<h3>IPsec 劣势</h3>
<ul>
<li>配置复杂</li>
<li>NAT 环境需要特殊处理</li>
<li>调试困难</li>
<li>协议栈复杂，实现差异大</li>
</ul>

<h3>适用场景</h3>
<table border="1" cellpadding="5">
<tr><th>场景</th><th>推荐技术</th></tr>
<tr><td>Site-to-Site VPN</td><td>IPsec (IKEv2)</td></tr>
<tr><td>远程办公接入</td><td>SSL VPN 或 IKEv2 EAP</td></tr>
<tr><td>轻量级点对点</td><td>WireGuard</td></tr>
<tr><td>跨厂商互联</td><td>IPsec</td></tr>
<tr><td>SD-WAN 底层</td><td>IPsec</td></tr>
</table>"""
    },
    "国密算法与IPsec": {
        "icon": "🇨🇳",
        "content": """<h2>国密算法与 IPsec</h2>

<h3>国密算法简介</h3>
<p>国密算法是中国国家密码管理局发布的商用密码算法标准，在等保2.0等合规要求下广泛使用。</p>

<h3>核心国密算法</h3>
<table border="1" cellpadding="5">
<tr><th>算法</th><th>类型</th><th>说明</th></tr>
<tr><td>SM1</td><td>对称加密</td><td>128 bit，硬件实现，不公开</td></tr>
<tr><td>SM2</td><td>非对称加密</td><td>256 bit ECC，替代RSA</td></tr>
<tr><td>SM3</td><td>哈希</td><td>256 bit，替代SHA-256</td></tr>
<tr><td>SM4</td><td>对称加密</td><td>128 bit，软件实现，公开</td></tr>
<tr><td>SM9</td><td>标识密码</td><td>基于身份的加密</td></tr>
</table>

<h3>国密 IPsec 配置</h3>
<pre>
# IKE 提案 (国密)
ike proposal GM_PROP
 encryption-algorithm sm4
 authentication-algorithm sm3
 dh group19
 prf hmac-sm3

# IPsec 提案 (国密)
ipsec proposal GM_PROP
 encapsulation-mode tunnel
 transform esp
 esp encryption-algorithm sm4
 esp authentication-algorithm sm3

# IKE Peer (国密证书)
ike peer GM_PEER
 ikev2 proposal GM_PROP
 certificate local-cert SM2_CERT
</pre>

<h3>国密 vs 国际算法</h3>
<table border="1" cellpadding="5">
<tr><th>功能</th><th>国际算法</th><th>国密算法</th></tr>
<tr><td>对称加密</td><td>AES-128/256</td><td>SM4</td></tr>
<tr><td>哈希</td><td>SHA-256</td><td>SM3</td></tr>
<tr><td>非对称</td><td>RSA-2048</td><td>SM2-256</td></tr>
<tr><td>数字签名</td><td>RSA-PSS</td><td>SM2-Sign</td></tr>
</ul>

<h3>RFC 参考</h3>
<ul>
<li>RFC 8998 - ShangMi (SM) Cipher Suites for TLS 1.3</li>
<li>GM/T 0022 - IPsec VPN 技术规范</li>
</ul>"""
    },
    "GRE over IPsec与IPsec over GRE": {
        "icon": "🔀",
        "content": """<h2>GRE over IPsec 与 IPsec over GRE</h2>

<h3>两种封装方式</h3>

<h4>GRE over IPsec (推荐)</h4>
<pre>
[新IP头] [ESP头] [原始IP头] [GRE头] [乘客协议]
</pre>
<ul>
<li>先封装 GRE，再对 GRE 报文进行 IPsec 加密</li>
<li>IPsec 保护 GRE 隧道</li>
<li>支持组播/广播（OSPF等路由协议）</li>
</ul>

<h4>IPsec over GRE</h4>
<pre>
[新IP头] [GRE头] [原始IP头] [ESP头] [加密载荷]
</pre>
<ul>
<li>先建立 IPsec 隧道，再通过 GRE 封装</li>
<li>GRE 隧道传输 IPsec 报文</li>
<li>较少使用</li>
</ul>

<h3>推荐: GRE over IPsec</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>GRE over IPsec</th><th>IPsec over GRE</th></tr>
<tr><td>安全性</td><td>✅ GRE载荷全部加密</td><td>✅ 同样安全</td></tr>
<tr><td>组播支持</td><td>✅ GRE支持</td><td>✅ GRE支持</td></tr>
<tr><td>配置复杂度</td><td>中</td><td>高</td></tr>
<tr><td>性能</td><td>较好</td><td>额外GRE开销</td></tr>
</table>

<h3>GRE over IPsec 配置</h3>
<pre>
# GRE 隧道
interface Tunnel0
 ip address 10.10.10.1 255.255.255.0
 tunnel-protocol gre
 source 202.100.1.1
 destination 202.100.2.2

# ACL 匹配 GRE 流量
acl number 3000
 rule 5 permit gre source 202.100.1.1 0 destination 202.100.2.2 0

# IPsec 策略
ipsec policy GRE_POLICY 1 isakmp
 security acl 3000
 ike-peer BRANCH
 proposal PROP1

# 运行 OSPF
ospf 1
 network 10.10.10.0 0.0.0.255 area 0
 network 192.168.1.0 0.0.0.255 area 0
</pre>"""
    }
}


# ============ 关卡数据 ============
LEVELS_DATA = [
    {
        "id": 1,
        "name": "IKE 基础配置",
        "difficulty": "入门",
        "description": "配置基本的 IKE Phase 1 参数，建立 ISAKMP SA",
        "scenario": "公司总部(10.1.1.1)需要与分支(10.2.2.2)建立 IPsec VPN。请完成 IKE Phase 1 的基础配置。",
        "knowledge_required": ["IPsec概述", "IKE协议详解"],
        "config_fields": [
            {"name": "ike_version", "label": "IKE版本", "type": "combo", "options": ["v1", "v2"], "default": "v1"},
            {"name": "exchange_mode", "label": "交换模式", "type": "combo", "options": ["main", "aggressive"], "default": "main"},
            {"name": "encryption", "label": "加密算法", "type": "combo", "options": ["aes-128", "aes-256", "3des", "des"], "default": "aes-128"},
            {"name": "authentication", "label": "认证算法", "type": "combo", "options": ["sha256", "sha1", "md5"], "default": "sha256"},
            {"name": "dh_group", "label": "DH Group", "type": "combo", "options": ["group14", "group19", "group5", "group2"], "default": "group14"},
            {"name": "sa_lifetime", "label": "SA生命周期(秒)", "type": "spin", "min": 3600, "max": 86400, "default": 86400},
            {"name": "pre_shared_key", "label": "预共享密钥", "type": "text", "default": ""},
        ],
        "correct_answer": {
            "ike_version": "v1",
            "exchange_mode": "main",
            "encryption": "aes-128",
            "authentication": "sha256",
            "dh_group": "group14",
            "sa_lifetime": 86400,
        },
        "tips": [
            "Main Mode 提供身份保护，推荐使用",
            "AES-128 是性能和安全的平衡点",
            "SHA-256 比 SHA-1 更安全",
            "DH Group 14 (2048-bit) 是当前推荐标准",
            "预共享密钥至少 16 个字符"
        ],
        "reference_config": """
ike proposal PROP1
 encryption-algorithm aes-128
 authentication-algorithm sha256
 dh group14
ike peer PEER1
 exchange-mode main
 pre-shared-key cipher YourStrongKey123!
 ike-proposal PROP1
"""
    },
    {
        "id": 2,
        "name": "IPsec 策略配置",
        "difficulty": "基础",
        "description": "配置 IPsec Phase 2 参数，建立数据传输隧道",
        "scenario": "IKE Phase 1 已建立完成。现在需要配置 IPsec 策略来保护实际的业务流量。本地子网 192.168.1.0/24，远端子网 192.168.2.0/24。",
        "knowledge_required": ["IPsec概述", "加密与认证算法"],
        "config_fields": [
            {"name": "protocol", "label": "安全协议", "type": "combo", "options": ["esp", "ah"], "default": "esp"},
            {"name": "encapsulation", "label": "封装模式", "type": "combo", "options": ["tunnel", "transport"], "default": "tunnel"},
            {"name": "encryption", "label": "ESP加密算法", "type": "combo", "options": ["aes-256", "aes-128", "3des"], "default": "aes-256"},
            {"name": "authentication", "label": "ESP认证算法", "type": "combo", "options": ["sha256", "sha1"], "default": "sha256"},
            {"name": "sa_lifetime_kb", "label": "SA流量生命周期(MB)", "type": "spin", "min": 100, "max": 4096000, "default": 4096000},
            {"name": "sa_lifetime_sec", "label": "SA时间生命周期(秒)", "type": "spin", "min": 1800, "max": 86400, "default": 3600},
            {"name": "local_subnet", "label": "本地子网", "type": "text", "default": ""},
            {"name": "remote_subnet", "label": "远端子网", "type": "text", "default": ""},
        ],
        "correct_answer": {
            "protocol": "esp",
            "encapsulation": "tunnel",
            "encryption": "aes-256",
            "authentication": "sha256",
            "local_subnet": "192.168.1.0/24",
            "remote_subnet": "192.168.2.0/24",
        },
        "tips": [
            "Site-to-Site VPN 必须使用 Tunnel Mode",
            "ESP 提供加密+认证，AH 只提供认证",
            "生产环境推荐 AES-256",
            "子网格式必须是 x.x.x.x/掩码长度",
            "SA 生命周期建议: 时间 3600s 或 流量 4096000KB"
        ],
        "reference_config": """
ipsec proposal PROP1
 encapsulation-mode tunnel
 transform esp
 esp encryption-algorithm aes-256
 esp authentication-algorithm sha256

acl number 3000
 rule 5 permit ip source 192.168.1.0 0.0.0.255 destination 192.168.2.0 0.0.0.255

ipsec policy POLICY1 isakmp
 security acl 3000
 ike-peer PEER1
 proposal PROP1
"""
    },
    {
        "id": 3,
        "name": "NAT 穿越场景",
        "difficulty": "进阶",
        "description": "配置 NAT-T 使 IPsec 能够在 NAT 环境下正常工作",
        "scenario": "分支网关位于运营商 NAT 后方(公网IP动态变化)。需要配置 NAT 穿越功能确保 VPN 稳定运行。",
        "knowledge_required": ["NAT穿越", "DPD与隧道维护"],
        "config_fields": [
            {"name": "nat_traversal", "label": "启用 NAT-T", "type": "check", "default": False},
            {"name": "ike_version", "label": "IKE 版本", "type": "combo", "options": ["v2", "v1"], "default": "v2"},
            {"name": "nat_detect", "label": "启用 NAT-D", "type": "check", "default": True},
            {"name": "dpd_enable", "label": "启用 DPD", "type": "check", "default": True},
            {"name": "dpd_interval", "label": "DPD 间隔(秒)", "type": "spin", "min": 10, "max": 300, "default": 30},
            {"name": "dpd_retry", "label": "DPD 重试次数", "type": "spin", "min": 1, "max": 10, "default": 5},
            {"name": "udp_port", "label": "NAT-T UDP 端口", "type": "combo", "options": ["4500", "500"], "default": "4500"},
        ],
        "correct_answer": {
            "nat_traversal": True,
            "ike_version": "v2",
            "nat_detect": True,
            "dpd_enable": True,
            "dpd_interval": 30,
            "dpd_retry": 5,
            "udp_port": "4500",
        },
        "tips": [
            "IKEv2 原生支持 NAT-T，优先选择",
            "NAT-T 使用 UDP 4500 端口封装 ESP",
            "DPD 对于 NAT 后的隧道维护至关重要",
            "NAT-D 可以自动检测路径上的 NAT 设备",
            "DPD 间隔建议 30s，太长会导致隧道断开检测延迟"
        ],
        "reference_config": """
ike peer PEER1
 ikev2 proposal PROP1
 nat-traversal
 dpd type periodic
 dpd interval 30
 dpd retry 5
 dpd timeout 10

ipsec proposal PROP1
 nat-t-udp-port 4500
"""
    },
    {
        "id": 4,
        "name": "双机热备 HA",
        "difficulty": "高级",
        "description": "配置 IPsec 双机热备，实现故障自动切换",
        "scenario": "总部部署了两台防火墙做 VRRP 热备。需要配置 IPsec 使其在主备切换后能自动恢复 VPN 连接。",
        "knowledge_required": ["高可用与故障切换", "DPD与隧道维护"],
        "config_fields": [
            {"name": "vrrp_aware", "label": "VRRP 感知", "type": "check", "default": True},
            {"name": "nsr_enable", "label": "NSR 状态热备", "type": "check", "default": True},
            {"name": "track_interface", "label": "接口联动", "type": "check", "default": True},
            {"name": "dpd_enable", "label": "DPD 检测", "type": "check", "default": True},
            {"name": "dpd_interval", "label": "DPD 间隔(秒)", "type": "spin", "min": 5, "max": 60, "default": 10},
            {"name": "sa_sync", "label": "SA 同步", "type": "check", "default": True},
            {"name": "rekey_timer", "label": "重协商提前时间(秒)", "type": "spin", "min": 60, "max": 600, "default": 300},
        ],
        "correct_answer": {
            "vrrp_aware": True,
            "nsr_enable": True,
            "track_interface": True,
            "dpd_enable": True,
            "dpd_interval": 10,
            "sa_sync": True,
        },
        "tips": [
            "VRRP Aware 使 IPsec 感知主备切换",
            "NSR 确保 SA 状态同步到备机",
            "接口联动可在接口 DOWN 时快速触发切换",
            "HA 场景下 DPD 间隔应设置较短(10s)",
            "SA 同步是故障无缝切换的关键"
        ],
        "reference_config": """
# VRRP 配置
interface GigabitEthernet0/0/1
 vrrp vrid 1 virtual-ip 10.0.0.254
 vrrp vrid 1 priority 120

# IPsec HA 配置
ipsec policy POLICY1 isakmp
 vrrp-aware
 nsr enable
 sa synchronization

ike peer PEER1
 dpd type periodic
 dpd interval 10
 dpd retry 3
"""
    },
    {
        "id": 5,
        "name": "复杂多对多 VPN",
        "difficulty": "专家",
        "description": "配置多站点全互联 IPsec VPN 网络",
        "scenario": "公司有 4 个站点需要全互联(Full Mesh)。每个站点有不同的子网，需要合理规划 IPsec 策略和 ACL。",
        "knowledge_required": ["IPsec概述", "IKE协议详解", "NAT穿越"],
        "config_fields": [
            {"name": "topology", "label": "拓扑类型", "type": "combo", "options": ["full-mesh", "hub-spoke", "partial-mesh"], "default": "full-mesh"},
            {"name": "ike_version", "label": "IKE 版本", "type": "combo", "options": ["v2", "v1"], "default": "v2"},
            {"name": "naming_convention", "label": "Peer 命名", "type": "combo", "options": ["by-site", "by-remote-ip", "by-function"], "default": "by-site"},
            {"name": "shared_key_mode", "label": "密钥管理模式", "type": "combo", "options": ["unique-per-peer", "shared-all"], "default": "unique-per-peer"},
            {"name": "route_control", "label": "路由控制方式", "type": "combo", "options": ["static-acl", "dynamic-routing", "both"], "default": "static-acl"},
            {"name": "nat_traversal", "label": "全局 NAT-T", "type": "check", "default": True},
            {"name": "peer_count", "label": "Peer 数量(4个站点)", "type": "spin", "min": 3, "max": 3, "default": 3},
        ],
        "correct_answer": {
            "topology": "full-mesh",
            "ike_version": "v2",
            "naming_convention": "by-site",
            "shared_key_mode": "unique-per-peer",
            "route_control": "static-acl",
            "nat_traversal": True,
        },
        "tips": [
            "Full-Mesh 需要 n*(n-1)/2 条隧道，4 个站点 = 6 条",
            "IKEv2 简化了多 peer 配置",
            "按站点命名便于运维管理",
            "每个 Peer 应使用独立的预共享密钥",
            "大型网络建议结合 OSPF/BGP 等动态路由"
        ],
        "reference_config": """
# 站点 A 配置 (Full Mesh)
ike peer PEER_B_SiteB
 ikev2 proposal PROP1
 address 10.2.2.2
 pre-shared-key cipher KeyForB_Unique!

ike peer PEER_C_SiteC
 ikev2 proposal PROP1
 address 10.3.3.3
 pre-shared-key cipher KeyForC_Unique!

ike peer PEER_D_SiteD
 ikev2 proposal PROP1
 address 10.4.4.4
 pre-shared-key cipher KeyForD_Unique!

# 每个 Peer 对应独立策略和 ACL
"""
    }
]


# ============ 进度管理 ============
class ProgressManager:
    def __init__(self, save_file="ipsec_progress.json"):
        self.save_file = save_file
        self.data = self.load()
    
    def load(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data["completed_levels"] = [int(x) for x in data.get("completed_levels", [])]
                    data["best_scores"] = {int(k): v for k, v in data.get("best_scores", {}).items()}
                    return data
            except:
                pass
        return {
            "completed_levels": [],
            "best_scores": {},
            "total_attempts": 0,
            "knowledge_read": [],
            "achievements": [],
            "start_time": datetime.now().isoformat()
        }
    
    def save(self):
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def complete_level(self, level_id, score):
        if level_id not in self.data["completed_levels"]:
            self.data["completed_levels"].append(level_id)
        if level_id not in self.data["best_scores"] or score > self.data["best_scores"][level_id]:
            self.data["best_scores"][level_id] = score
        self.data["total_attempts"] += 1
        self.check_achievements()
        self.save()
    
    def record_knowledge_read(self, knowledge_name):
        if knowledge_name not in KNOWLEDGE_DATA:
            return
        if knowledge_name not in self.data["knowledge_read"]:
            self.data["knowledge_read"].append(knowledge_name)
            self.check_achievements()
            self.save()
    
    def check_achievements(self):
        achievements = self.data["achievements"]
        if "first_knowledge" not in achievements and len(self.data["knowledge_read"]) >= 1:
            self.data["achievements"].append("first_knowledge")
        if "knowledge_master" not in achievements and len(self.data["knowledge_read"]) >= len(KNOWLEDGE_DATA):
            self.data["achievements"].append("knowledge_master")
        if "first_level" not in achievements and len(self.data["completed_levels"]) >= 1:
            self.data["achievements"].append("first_level")
        if "all_levels" not in achievements and len(self.data["completed_levels"]) >= 5:
            self.data["achievements"].append("all_levels")
        if "perfect_score" not in achievements:
            for score in self.data["best_scores"].values():
                if score == 100:
                    self.data["achievements"].append("perfect_score")
                    break


# ============ 主窗口 ============
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.progress = ProgressManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('IPsec配置大师 - IPsec Configuration Master')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(self.load_stylesheet())
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_menu = MainMenu(self)
        self.knowledge_view = KnowledgeView(self)
        self.level_select = LevelSelectView(self)
        self.game_view = GameView(self)
        self.achievement_view = AchievementView(self)
        
        self.central_widget.addWidget(self.main_menu)
        self.central_widget.addWidget(self.knowledge_view)
        self.central_widget.addWidget(self.level_select)
        self.central_widget.addWidget(self.game_view)
        self.central_widget.addWidget(self.achievement_view)
        
        self.show_main_menu()
    
    def show_main_menu(self):
        self.central_widget.setCurrentWidget(self.main_menu)
        self.main_menu.refresh_stats()
    
    def show_knowledge(self):
        self.central_widget.setCurrentWidget(self.knowledge_view)
        self.knowledge_view.refresh()
    
    def show_level_select(self):
        self.central_widget.setCurrentWidget(self.level_select)
        self.level_select.refresh()
    
    def start_level(self, level_id):
        self.game_view.load_level(level_id)
        self.central_widget.setCurrentWidget(self.game_view)
    
    def show_achievements(self):
        self.central_widget.setCurrentWidget(self.achievement_view)
        self.achievement_view.refresh()
    
    def load_stylesheet(self):
        return """
            QMainWindow {
                background-color: #0d1117;
            }
            QLabel {
                color: #e6edf3;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: #00d4ff;
            }
            QLabel#subtitle {
                font-size: 16px;
                color: #8b949e;
            }
            QLabel#section_title {
                font-size: 18px;
                font-weight: bold;
                color: #00d4ff;
            }
            QLabel#card_title {
                font-size: 15px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#score {
                font-size: 22px;
                font-weight: bold;
                color: #4caf50;
            }
            QPushButton {
                background-color: #21262d;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
                border-color: #00d4ff;
            }
            QPushButton:pressed {
                background-color: #161b22;
            }
            QPushButton#primary {
                background-color: #00d4ff;
                color: #ffffff;
                border-color: #00d4ff;
                font-size: 15px;
                padding: 12px 24px;
            }
            QPushButton#primary:hover {
                background-color: #00b8d4;
            }
            QPushButton#success {
                background-color: #238636;
                color: #ffffff;
                border-color: #238636;
                font-size: 14px;
            }
            QPushButton#success:hover {
                background-color: #2ea043;
            }
            QPushButton#danger {
                background-color: #da3633;
                color: #ffffff;
                border-color: #da3633;
            }
            QPushButton#danger:hover {
                background-color: #f85149;
            }
            QPushButton:disabled {
                background-color: #21262d;
                color: #6e7681;
                border-color: #30363d;
            }
            QFrame#card {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
            QFrame#card:hover {
                border-color: #00d4ff;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QGroupBox {
                color: #00d4ff;
                border: 2px solid #30363d;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QProgressBar {
                border: 2px solid #30363d;
                border-radius: 5px;
                text-align: center;
                background-color: #21262d;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #00d4ff;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #21262d;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #21262d;
                color: #ffffff;
                selection-background-color: #30363d;
                selection-color: #ffffff;
            }
            QSpinBox {
                background-color: #21262d;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #30363d;
            }
            QCheckBox {
                color: #e6edf3;
                spacing: 8px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #30363d;
                border-radius: 3px;
                background-color: #21262d;
            }
            QCheckBox::indicator:checked {
                background-color: #00d4ff;
                border-color: #00d4ff;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }
            QListWidget {
                background-color: #21262d;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #30363d;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #30363d;
                color: #00d4ff;
            }
            QTabWidget::pane {
                border: 1px solid #30363d;
                border-radius: 6px;
                background-color: #161b22;
            }
            QTabBar::tab {
                background-color: #21262d;
                color: #e6edf3;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #30363d;
                color: #00d4ff;
            }
            QLineEdit {
                background-color: #21262d;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 5px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border-color: #00d4ff;
            }
            QRadioButton {
                color: #e6edf3;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #30363d;
                border-radius: 9px;
                background-color: #21262d;
            }
            QRadioButton::indicator:checked {
                background-color: #00d4ff;
                border-color: #00d4ff;
            }
            QMessageBox {
                background-color: #161b22;
            }
            QMessageBox QLabel {
                color: #e6edf3;
            }
            QMessageBox QPushButton {
                background-color: #21262d;
                color: #ffffff;
                border: 1px solid #30363d;
            }
            QDialog {
                background-color: #0d1117;
            }
        """


# ============ 主菜单 ============
class MainMenu(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel('IPsec配置大师')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel('IPsec 协议深度学习平台')
        subtitle.setObjectName('subtitle')
        subtitle.setAlignment(Qt.AlignCenter)
        
        layout.addSpacing(50)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(40)
        
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        btn_knowledge = QPushButton('📖 知识学习')
        btn_knowledge.setObjectName('primary')
        btn_knowledge.setMinimumSize(300, 50)
        btn_knowledge.clicked.connect(self.main_window.show_knowledge)
        
        btn_practice = QPushButton('🎯 练习挑战')
        btn_practice.setObjectName('primary')
        btn_practice.setMinimumSize(300, 50)
        btn_practice.clicked.connect(self.main_window.show_level_select)
        
        btn_achievement = QPushButton('🏆 成就系统')
        btn_achievement.setObjectName('primary')
        btn_achievement.setMinimumSize(300, 50)
        btn_achievement.clicked.connect(self.main_window.show_achievements)
        
        buttons_layout.addWidget(btn_knowledge)
        buttons_layout.addWidget(btn_practice)
        buttons_layout.addWidget(btn_achievement)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.stats_label = QLabel('')
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet('color: #888; font-size: 14px;')
        layout.addWidget(self.stats_label)
        layout.addSpacing(30)
        
        self.setLayout(layout)
    
    def refresh_stats(self):
        progress = self.main_window.progress.data
        completed = len(progress['completed_levels'])
        knowledge_read = len(progress['knowledge_read'])
        achievements = len(progress['achievements'])
        self.stats_label.setText(f'学习进度: {knowledge_read}/{len(KNOWLEDGE_DATA)} 知识点 | {completed}/5 关卡已完成 | {achievements} 成就')


# ============ 知识学习视图 ============
class KnowledgeView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        back_btn = QPushButton('返回菜单')
        back_btn.clicked.connect(self.main_window.show_main_menu)
        
        title = QLabel('IPsec 知识库')
        title.setObjectName('section_title')
        
        header.addWidget(back_btn)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.scroll.setWidget(self.content_widget)
        
        layout.addWidget(self.scroll)
        self.setLayout(layout)
    
    def refresh(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for name, data in KNOWLEDGE_DATA.items():
            card = QFrame()
            card.setObjectName('card')
            card_layout = QVBoxLayout()
            
            card_header = QHBoxLayout()
            icon_label = QLabel(f"{data['icon']} {name}")
            icon_label.setObjectName('card_title')
            
            read_btn = QPushButton('开始学习')
            read_btn.setObjectName('primary')
            read_btn.setFixedSize(100, 30)
            read_btn.clicked.connect(lambda checked, n=name: self.open_knowledge(n))
            
            card_header.addWidget(icon_label)
            card_header.addStretch()
            card_header.addWidget(read_btn)
            
            card_layout.addLayout(card_header)
            card.setLayout(card_layout)
            card.setMinimumHeight(60)
            
            self.content_layout.addWidget(card)
            self.content_layout.addSpacing(10)
        
        self.content_layout.addStretch()
    
    def open_knowledge(self, name):
        dialog = KnowledgeDialog(name, self.main_window)
        dialog.exec_()


class KnowledgeDialog(QDialog):
    def __init__(self, name, main_window, parent=None):
        super().__init__(parent)
        self.name = name
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'📖 {self.name}')
        self.setMinimumSize(900, 700)
        self.setStyleSheet(self.main_window.styleSheet())
        
        layout = QVBoxLayout()
        
        title = QLabel(f"{KNOWLEDGE_DATA[self.name]['icon']} {self.name}")
        title.setObjectName('section_title')
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(KNOWLEDGE_DATA[self.name]['content'])
        content.setMinimumHeight(500)
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(title)
        layout.addWidget(content)
        layout.addWidget(close_btn)
        self.setLayout(layout)
        
        self.main_window.progress.record_knowledge_read(self.name)


# ============ 关卡选择视图 ============
class LevelSelectView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        back_btn = QPushButton('返回菜单')
        back_btn.clicked.connect(self.main_window.show_main_menu)
        
        title = QLabel('练习挑战')
        title.setObjectName('section_title')
        
        header.addWidget(back_btn)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.scroll.setWidget(self.content_widget)
        
        layout.addWidget(self.scroll)
        self.setLayout(layout)
    
    def refresh(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        progress = self.main_window.progress.data
        completed = progress['completed_levels']
        scores = progress['best_scores']
        
        for level in LEVELS_DATA:
            card = QFrame()
            card.setObjectName('card')
            card_layout = QVBoxLayout()
            
            header_layout = QHBoxLayout()
            
            level_num = QLabel(f"第 {level['id']} 关")
            level_num.setObjectName('card_title')
            
            difficulty_colors = {
                '入门': '#4caf50',
                '基础': '#2196f3',
                '进阶': '#ff9800',
                '高级': '#f44336',
                '专家': '#9c27b0'
            }
            diff_label = QLabel(level['difficulty'])
            diff_label.setStyleSheet(f'color: {difficulty_colors.get(level["difficulty"], "#fff")}; font-weight: bold;')
            
            status_label = QLabel('已完成' if level['id'] in completed else '未解锁')
            if level['id'] in completed:
                status_label.setStyleSheet('color: #4caf50;')
            
            header_layout.addWidget(level_num)
            header_layout.addWidget(diff_label)
            header_layout.addStretch()
            header_layout.addWidget(status_label)
            
            name_label = QLabel(level['name'])
            name_label.setStyleSheet('font-size: 18px; color: #fff; margin: 5px 0;')
            
            desc_label = QLabel(level['description'])
            desc_label.setStyleSheet('color: #888;')
            
            score_label = QLabel(f'最高分: {scores.get(level["id"], "-")} / 100')
            score_label.setObjectName('score')
            
            start_btn = QPushButton('开始挑战')
            start_btn.setObjectName('primary')
            start_btn.setFixedSize(120, 35)
            start_btn.clicked.connect(lambda checked, lid=level['id']: self.main_window.start_level(lid))
            
            card_layout.addLayout(header_layout)
            card_layout.addWidget(name_label)
            card_layout.addWidget(desc_label)
            card_layout.addWidget(score_label)
            card_layout.addWidget(start_btn, alignment=Qt.AlignRight)
            card.setLayout(card_layout)
            
            self.content_layout.addWidget(card)
            self.content_layout.addSpacing(15)
        
        self.content_layout.addStretch()


# ============ 游戏视图 ============
class GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_level = None
        self.current_score = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        self.back_btn = QPushButton('返回')
        self.back_btn.clicked.connect(self.main_window.show_level_select)
        
        self.level_title = QLabel('')
        self.level_title.setObjectName('section_title')
        
        self.score_display = QLabel('得分: 0 / 100')
        self.score_display.setObjectName('score')
        
        header.addWidget(self.back_btn)
        header.addWidget(self.level_title)
        header.addStretch()
        header.addWidget(self.score_display)
        layout.addLayout(header)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumHeight(10)
        layout.addWidget(self.progress_bar)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        self.scenario_group = QGroupBox('场景描述')
        self.scenario_label = QLabel('')
        self.scenario_label.setWordWrap(True)
        self.scenario_label.setStyleSheet('padding: 10px; color: #c9d1d9;')
        scenario_layout = QVBoxLayout()
        scenario_layout.addWidget(self.scenario_label)
        self.scenario_group.setLayout(scenario_layout)
        
        self.config_group = QGroupBox('配置面板')
        self.config_layout = QFormLayout()
        self.config_fields = {}
        self.config_group.setLayout(self.config_layout)
        
        self.tips_group = QGroupBox('提示')
        self.tips_label = QLabel('')
        self.tips_label.setWordWrap(True)
        self.tips_label.setStyleSheet('padding: 10px; color: #ffeb3b;')
        tips_layout = QVBoxLayout()
        tips_layout.addWidget(self.tips_label)
        self.tips_group.setLayout(tips_layout)
        
        left_layout.addWidget(self.scenario_group)
        left_layout.addWidget(self.config_group)
        left_layout.addWidget(self.tips_group)
        left_widget.setLayout(left_layout)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        self.reference_group = QGroupBox('参考配置')
        self.reference_label = QLabel('')
        self.reference_label.setStyleSheet('padding: 10px; font-family: Consolas, monospace; color: #c9d1d9; white-space: pre;')
        self.reference_label.setWordWrap(True)
        ref_layout = QVBoxLayout()
        ref_layout.addWidget(self.reference_label)
        self.reference_group.setLayout(ref_layout)
        
        self.knowledge_group = QGroupBox('推荐学习资料')
        self.knowledge_list = QListWidget()
        self.knowledge_list.itemDoubleClicked.connect(self.on_knowledge_clicked)
        know_layout = QVBoxLayout()
        know_layout.addWidget(self.knowledge_list)
        self.knowledge_group.setLayout(know_layout)
        
        buttons_layout = QHBoxLayout()
        self.submit_btn = QPushButton('提交答案')
        self.submit_btn.setObjectName('success')
        self.submit_btn.setMinimumHeight(40)
        self.submit_btn.clicked.connect(self.submit_answer)
        
        self.hint_btn = QPushButton('显示提示')
        self.hint_btn.setMinimumHeight(40)
        self.hint_btn.clicked.connect(self.show_hint)
        
        self.show_ref_btn = QPushButton('显示参考')
        self.show_ref_btn.setMinimumHeight(40)
        self.show_ref_btn.clicked.connect(self.show_reference)
        
        buttons_layout.addWidget(self.hint_btn)
        buttons_layout.addWidget(self.show_ref_btn)
        buttons_layout.addWidget(self.submit_btn)
        
        right_layout.addWidget(self.reference_group)
        right_layout.addWidget(self.knowledge_group)
        right_layout.addLayout(buttons_layout)
        right_widget.setLayout(right_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 500])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def load_level(self, level_id):
        try:
            self.current_level = next(l for l in LEVELS_DATA if l['id'] == level_id)
        except StopIteration:
            QMessageBox.warning(self, '错误', f'关卡 {level_id} 不存在')
            return
        
        self.current_score = 0
        
        self.level_title.setText(f"第 {self.current_level['id']} 关: {self.current_level['name']}")
        self.score_display.setText('得分: 0 / 100')
        self.progress_bar.setValue(0)
        
        self.scenario_label.setText(self.current_level['scenario'])
        
        self.tips_label.setText('点击"显示提示"获取帮助')
        self.reference_label.setText('点击"显示参考"查看')
        
        self.clear_config_fields()
        self.build_config_fields()
        
        self.knowledge_list.clear()
        for k in self.current_level['knowledge_required']:
            item = QListWidgetItem(k)
            self.knowledge_list.addItem(item)
    
    def clear_config_fields(self):
        for i in reversed(range(self.config_layout.rowCount())):
            label = self.config_layout.itemAt(i, QFormLayout.LabelRole)
            widget = self.config_layout.itemAt(i, QFormLayout.FieldRole)
            if label:
                label.widget().deleteLater()
            if widget:
                widget.widget().deleteLater()
        self.config_fields = {}
    
    def build_config_fields(self):
        for field in self.current_level['config_fields']:
            widget = self.create_field_widget(field)
            self.config_layout.addRow(field['label'], widget)
            self.config_fields[field['name']] = {'widget': widget, 'field': field}
    
    def create_field_widget(self, field):
        if field['type'] == 'combo':
            widget = QComboBox()
            widget.addItems(field['options'])
            if 'default' in field:
                idx = field['options'].index(field['default']) if field['default'] in field['options'] else 0
                widget.setCurrentIndex(idx)
        elif field['type'] == 'spin':
            widget = QSpinBox()
            widget.setRange(field['min'], field['max'])
            widget.setValue(field['default'])
        elif field['type'] == 'check':
            widget = QCheckBox()
            widget.setChecked(field['default'])
        elif field['type'] == 'text':
            widget = QLineEdit()
            widget.setText(field['default'])
            widget.setPlaceholderText(f'请输入{field["label"]}')
        else:
            widget = QLineEdit()
        return widget
    
    def get_user_answer(self):
        answer = {}
        for name, data in self.config_fields.items():
            widget = data['widget']
            field = data['field']
            if field['type'] == 'combo':
                answer[name] = widget.currentText()
            elif field['type'] == 'spin':
                answer[name] = widget.value()
            elif field['type'] == 'check':
                answer[name] = widget.isChecked()
            elif field['type'] == 'text':
                answer[name] = widget.text().strip()
        return answer
    
    def submit_answer(self):
        if not self.current_level:
            return
        
        user_answer = self.get_user_answer()
        correct = self.current_level['correct_answer']
        
        total_fields = len(correct)
        correct_count = 0
        feedback = []
        
        for key, expected in correct.items():
            user_val = user_answer.get(key)
            if isinstance(expected, str):
                if isinstance(user_val, str) and user_val.strip().lower() == expected.strip().lower():
                    correct_count += 1
                    feedback.append(f'[✓] {key}: 正确')
                    continue
            if user_val == expected:
                correct_count += 1
                feedback.append(f'[✓] {key}: 正确')
            else:
                if isinstance(expected, bool):
                    feedback.append(f'[✗] {key}: 期望 {expected}')
                elif isinstance(expected, str):
                    feedback.append(f'[✗] {key}: 期望 {expected} (你输入的是 {user_val})')
                else:
                    tolerance = abs(expected * 0.1)
                    if isinstance(user_val, (int, float)) and abs(user_val - expected) <= tolerance:
                        correct_count += 0.5
                        feedback.append(f'[~] {key}: 部分正确 (你输入的是 {user_val})')
                    else:
                        feedback.append(f'[✗] {key}: 期望 {expected} (你输入的是 {user_val})')
        
        score = round((correct_count / total_fields) * 100)
        self.current_score = score
        
        self.score_display.setText(f'得分: {score} / 100')
        self.progress_bar.setValue(score)
        
        if score == 100:
            msg = f'恭喜！完美通过！\n\n得分: {score}/100\n\n'
            msg += '\n'.join(feedback)
            QMessageBox.information(self, '完美！', msg)
        elif score >= 70:
            msg = f'做得好！你通过了！\n\n得分: {score}/100\n\n'
            msg += '\n'.join(feedback)
            QMessageBox.information(self, '通过！', msg)
        elif score >= 50:
            msg = f'接近及格线\n\n得分: {score}/100\n\n'
            msg += '\n'.join(feedback)
            QMessageBox.warning(self, '未通过', msg)
        else:
            msg = f'需要更多练习\n\n得分: {score}/100\n\n'
            msg += '\n'.join(feedback)
            QMessageBox.warning(self, '未通过', msg)
        
        self.main_window.progress.complete_level(self.current_level['id'], score)
    
    def show_hint(self):
        if not self.current_level:
            return
        tips = '\n'.join([f'• {t}' for t in self.current_level['tips']])
        QMessageBox.information(self, '💡 提示', tips)
    
    def show_reference(self):
        if not self.current_level:
            return
        self.reference_label.setText(self.current_level['reference_config'])
    
    def on_knowledge_clicked(self, item):
        name = item.text()
        if name in KNOWLEDGE_DATA:
            dialog = KnowledgeDialog(name, self.main_window, self)
            dialog.exec_()


# ============ 成就视图 ============
class AchievementView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        back_btn = QPushButton('返回菜单')
        back_btn.clicked.connect(self.main_window.show_main_menu)
        
        title = QLabel('成就系统')
        title.setObjectName('section_title')
        
        header.addWidget(back_btn)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.scroll.setWidget(self.content_widget)
        
        layout.addWidget(self.scroll)
        self.setLayout(layout)
    
    def refresh(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        progress = self.main_window.progress.data
        
        stats_group = QGroupBox('学习统计')
        stats_layout = QFormLayout()
        
        total_attempts = progress['total_attempts']
        completed = len(progress['completed_levels'])
        knowledge_read = len(progress['knowledge_read'])
        
        label1 = QLabel('总尝试次数:')
        value1 = QLabel(str(total_attempts))
        stats_layout.addRow(label1, value1)
        
        label2 = QLabel('关卡完成:')
        value2 = QLabel(f'{completed} / 5')
        stats_layout.addRow(label2, value2)
        
        label3 = QLabel('知识点阅读:')
        value3 = QLabel(f'{knowledge_read} / {len(KNOWLEDGE_DATA)}')
        stats_layout.addRow(label3, value3)
        
        if progress['completed_levels']:
            avg_score = sum(progress['best_scores'].values()) / len(progress['best_scores'])
            label4 = QLabel('平均分:')
            value4 = QLabel(f'{avg_score:.1f}')
            stats_layout.addRow(label4, value4)
        
        stats_group.setLayout(stats_layout)
        self.content_layout.addWidget(stats_group)
        self.content_layout.addSpacing(20)
        
        achievements_group = QGroupBox('成就列表')
        ach_layout = QVBoxLayout()
        
        achievements = {
            'first_knowledge': ('初学者', '阅读第一个知识点'),
            'knowledge_master': ('知识大师', f'阅读全部{len(KNOWLEDGE_DATA)}个知识点'),
            'first_level': ('初战告捷', '完成第一个关卡'),
            'all_levels': ('IPsec大师', '完成全部5个关卡'),
            'perfect_score': ('完美主义者', '任意关卡获得100分'),
        }
        
        for key, (name, desc) in achievements.items():
            card = QFrame()
            card.setObjectName('card')
            card_layout = QHBoxLayout()
            
            text_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setObjectName('card_title')
            desc_label = QLabel(desc)
            desc_label.setStyleSheet('color: #8b949e;')
            text_layout.addWidget(name_label)
            text_layout.addWidget(desc_label)
            
            status_label = QLabel('已解锁' if key in progress['achievements'] else '未解锁')
            if key in progress['achievements']:
                status_label.setStyleSheet('color: #4caf50;')
            
            card_layout.addLayout(text_layout)
            card_layout.addStretch()
            card_layout.addWidget(status_label)
            card.setLayout(card_layout)
            
            ach_layout.addWidget(card)
            ach_layout.addSpacing(10)
        
        achievements_group.setLayout(ach_layout)
        self.content_layout.addWidget(achievements_group)
        self.content_layout.addStretch()


# ============ 启动应用 ============
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置字体，确保中文能正常显示
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
