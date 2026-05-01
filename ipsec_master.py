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
<p>IPsec 是一组协议，用于在 IP 层保护通信安全。它是核心网、企业网络中 VPN 连接的基础技术。</p>

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
<p>SA是IPsec的基础，包含：SPI、目标地址、安全协议、密钥等信息。IKE负责建立和维护SA。</p>"""
    },
    "IKE协议详解": {
        "icon": "🔑",
        "content": """<h2>IKE (Internet Key Exchange) 协议</h2>
<p>IKE 使用 UDP 端口 500，分为 Phase 1 和 Phase 2 两个阶段。</p>

<h3>IKE Phase 1 - 建立 ISAKMP SA</h3>
<p>目的：建立安全的控制通道，用于后续的 Phase 2 协商。</p>
<ul>
<li><b>Main Mode</b>: 6个报文，提供身份保护</li>
<li><b>Aggressive Mode</b>: 3个报文，快速但不保护身份</li>
</ul>

<h3>IKE Phase 2 - 建立 IPsec SA</h3>
<p>目的：协商实际的数据传输参数（加密算法、认证算法等）。</p>
<ul>
<li><b>Quick Mode</b>: 3个报文，在Phase 1建立的SA保护下进行</li>
</ul>

<h3>IKEv1 vs IKEv2</h3>
<table border="1" cellpadding="5">
<tr><th>特性</th><th>IKEv1</th><th>IKEv2</th></tr>
<tr><td>报文数量</td><td>Phase 1: 4-6, Phase 2: 3</td><td>初始交换: 4, 后续创建: 2</td></tr>
<tr><td>NAT穿越</td><td>需要额外配置</td><td>原生支持</td></tr>
<tr><td>MOBIKE</td><td>不支持</td><td>支持</td></tr>
<tr><td>认证方式</td><td>预共享密钥/证书</td><td>预共享密钥/证书/EAP</td></tr>
</table>"""
    },
    "加密与认证算法": {
        "icon": "🔐",
        "content": """<h2>加密与认证算法</h2>

<h3>加密算法 (Encryption Algorithms)</h3>
<table border="1" cellpadding="5">
<tr><th>算法</th><th>密钥长度</th><th>安全性</th><th>性能</th></tr>
<tr><td>DES</td><td>56 bit</td><td>❌ 已过时</td><td>快</td></tr>
<tr><td>3DES</td><td>168 bit</td><td>⚠️ 逐步淘汰</td><td>慢</td></tr>
<tr><td>AES-128</td><td>128 bit</td><td>✅ 推荐</td><td>快</td></tr>
<tr><td>AES-256</td><td>256 bit</td><td>✅✅ 高安全</td><td>中</td></tr>
</table>

<h3>认证算法 (Integrity Algorithms)</h3>
<table border="1" cellpadding="5">
<tr><th>算法</th><th>哈希长度</th><th>说明</th></tr>
<tr><td>MD5</td><td>128 bit</td><td>❌ 不推荐</td></tr>
<tr><td>SHA-1</td><td>160 bit</td><td>⚠️ 逐步淘汰</td></tr>
<tr><td>SHA-256</td><td>256 bit</td><td>✅ 推荐</td></tr>
<tr><td>SHA-384/512</td><td>384/512 bit</td><td>✅✅ 高安全</td></tr>
</table>

<h3>DH Group (Diffie-Hellman)</h3>
<table border="1" cellpadding="5">
<tr><th>Group</th><th>位数</th><th>安全性</th></tr>
<tr><td>Group 2</td><td>1024 bit</td><td>❌ 弱</td></tr>
<tr><td>Group 5</td><td>1536 bit</td><td>⚠️ 一般</td></tr>
<tr><td>Group 14</td><td>2048 bit</td><td>✅ 推荐</td></tr>
<tr><td>Group 19</td><td>256 bit (ECP)</td><td>✅ 推荐</td></tr>
<tr><td>Group 24</td><td>2048 bit</td><td>✅✅ 高安全</td></tr>
</table>"""
    },
    "NAT穿越": {
        "icon": "🌐",
        "content": """<h2>NAT 穿越 (NAT Traversal)</h2>
<p>当 IPsec 网关位于 NAT 设备后方时，需要特殊处理。</p>

<h3>问题</h3>
<ul>
<li>ESP 协议 (IP 协议 50) 没有端口号，NAT 无法正确转换</li>
<li>AH 协议会被 NAT 修改破坏（因为AH保护整个IP头）</li>
</ul>

<h3>解决方案</h3>
<ul>
<li><b>UDP 封装</b>: 将 ESP 包封装在 UDP 4500 端口中</li>
<li><b>NAT-D (NAT Detection)</b>: 通过 hash 检测路径上是否存在 NAT</li>
</ul>

<h3>配置要点</h3>
<pre>
# 启用 NAT-T
nat-traversal enable
ikev2 nat-detect

# NAT 后的 Keepalive
dpd interval 30
dpd retry 5
</pre>

<h3>典型场景</h3>
<p>移动用户通过家庭路由器接入企业网络时，必须启用 NAT-T。</p>"""
    },
    "高可用与故障切换": {
        "icon": "🔄",
        "content": """<h2>高可用 (High Availability)</h2>

<h3>实现方式</h3>
<ul>
<li><b>VRRP/HSRP</b>: 虚拟网关冗余</li>
<li><b>双活 IPsec</b>: 两条 IPsec 隧道同时运行</li>
<li><b>IPsec NSR</b>: 状态热备份</li>
</ul>

<h3>配置示例</h3>
<pre>
# VRRP 配置
interface GigabitEthernet0/0/1
 vrrp vrid 1 virtual-ip 10.0.0.254
 vrrp vrid 1 priority 120

# IPsec 策略绑定 VRRP
ipsec policy POLICY1 vrrp-aware
</pre>

<h3>注意事项</h3>
<ul>
<li>确保两端 SPI 同步</li>
<li>使用 DPD 检测隧道状态</li>
<li>合理设置 SA 生命周期</li>
</ul>"""
    },
    "DPD与隧道维护": {
        "icon": "📡",
        "content": """<h2>DPD (Dead Peer Detection)</h2>
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
</table>"""
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
        if "knowledge_master" not in achievements and len(self.data["knowledge_read"]) >= 6:
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
        
        subtitle = QLabel('核心网工程师实践学习平台')
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
        self.stats_label.setText(f'学习进度: {knowledge_read}/6 知识点 | {completed}/5 关卡已完成 | {achievements} 成就')


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
        value3 = QLabel(f'{knowledge_read} / 6')
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
            'knowledge_master': ('知识大师', '阅读全部6个知识点'),
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
