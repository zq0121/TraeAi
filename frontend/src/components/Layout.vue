<template>
  <div class="layout">
    <aside class="sidebar" :class="{ collapsed: !opened }">
      <div class="brand"><el-icon><Cpu /></el-icon><span v-if="opened">钢材缺陷检测</span></div>
      <el-menu :default-active="$route.path" router :collapse="!opened" background-color="transparent" text-color="#cbd5e1" active-text-color="#38bdf8">
        <el-menu-item index="/dashboard"><el-icon><DataBoard /></el-icon><template #title>首页大屏</template></el-menu-item>
        <el-sub-menu index="detection"><template #title><el-icon><Aim /></el-icon><span>缺陷检测</span></template>
          <el-menu-item index="/detection/image">图片检测</el-menu-item>
          <el-menu-item index="/detection/video">视频检测</el-menu-item>
          <el-menu-item index="/detection/camera">摄像头检测</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/records"><el-icon><Document /></el-icon><template #title>检测记录</template></el-menu-item>
        <el-menu-item index="/quality"><el-icon><CircleCheck /></el-icon><template #title>质量管理</template></el-menu-item>
        <el-menu-item index="/analysis"><el-icon><TrendCharts /></el-icon><template #title>统计分析</template></el-menu-item>
        <el-sub-menu index="produce"><template #title><el-icon><Operation /></el-icon><span>生产运营</span></template>
          <el-menu-item index="/production">生产管理</el-menu-item>
          <el-menu-item index="/order">订单管理</el-menu-item>
          <el-menu-item index="/report">报表中心</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="device"><template #title><el-icon><Cpu /></el-icon><span>设备物联</span></template>
          <el-menu-item index="/equipment">设备管理</el-menu-item>
          <el-menu-item index="/maintenance">设备维护</el-menu-item>
          <el-menu-item index="/iot">物联监控</el-menu-item>
          <el-menu-item index="/model">模型管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="logistics"><template #title><el-icon><Box /></el-icon><span>物料仓储</span></template>
          <el-menu-item index="/material">原料管理</el-menu-item>
          <el-menu-item index="/warehouse">成品仓储</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="hse"><template #title><el-icon><Lock /></el-icon><span>安全能环</span></template>
          <el-menu-item index="/energy">能耗管理</el-menu-item>
          <el-menu-item index="/safety">安全环保</el-menu-item>
        </el-sub-menu>
        <el-sub-menu v-if="isAdmin" index="system"><template #title><el-icon><Setting /></el-icon><span>系统管理</span></template>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
          <el-menu-item index="/system/roles">角色管理</el-menu-item>
          <el-menu-item index="/system/logs">日志审计</el-menu-item>
          <el-menu-item index="/system/settings">系统设置</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="files"><template #title><el-icon><Folder /></el-icon><span>文件管理</span></template>
          <el-menu-item index="/files/images">图片文件</el-menu-item>
          <el-menu-item index="/files/videos">视频文件</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </aside>
    <section class="main" :class="{ collapsed: !opened }">
      <header class="topbar">
        <div class="left"><el-button link @click="toggle"><el-icon size="22"><Fold /></el-icon></el-button><b>钢材表面缺陷智能识别与分析平台V1.0</b></div>
        <div class="right"><span class="status-dot"></span>模型在线 <el-divider direction="vertical" /> {{ user?.real_name || user?.username }} <el-button link type="primary" @click="logout">退出</el-button></div>
      </header>
      <main class="content"><router-view /></main>
    </section>
  </div>
</template>
<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { Aim, Box, CircleCheck, Cpu, DataBoard, Document, Folder, Fold, Lock, Operation, Setting, TrendCharts } from '@element-plus/icons-vue'
const store = useStore(); const router = useRouter()
const opened = computed(() => store.getters.sidebarOpened)
const user = computed(() => store.getters.user)
const isAdmin = computed(() => store.getters.isAdmin)
const toggle = () => store.dispatch('toggleSidebar')
const logout = () => { store.dispatch('logout'); router.push('/login') }
</script>
<style scoped>
.layout{min-height:100vh;background:radial-gradient(circle at top left,#123456 0,#07111f 42%,#020617 100%)}
.sidebar{position:fixed;inset:0 auto 0 0;width:230px;background:rgba(15,23,42,.92);border-right:1px solid rgba(56,189,248,.25);transition:.25s;z-index:2;overflow-y:auto;overflow-x:hidden}.sidebar::-webkit-scrollbar{width:6px}.sidebar::-webkit-scrollbar-thumb{background:rgba(56,189,248,.3);border-radius:3px}.sidebar.collapsed{width:72px}.brand{height:64px;display:flex;align-items:center;gap:12px;padding:0 20px;color:#38bdf8;font-weight:800;font-size:18px;border-bottom:1px solid rgba(148,163,184,.16);white-space:nowrap;position:sticky;top:0;background:rgba(15,23,42,.96);z-index:1}.sidebar.collapsed .brand{justify-content:center;padding:0}.main{margin-left:230px;min-height:100vh;transition:.25s}.main.collapsed{margin-left:72px}.topbar{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:rgba(15,23,42,.75);border-bottom:1px solid rgba(56,189,248,.18);backdrop-filter:blur(10px)}.left,.right{display:flex;align-items:center;gap:12px}.status-dot{width:9px;height:9px;background:#22c55e;border-radius:50%;box-shadow:0 0 14px #22c55e}.content{min-height:calc(100vh - 64px)}:deep(.el-menu){border-right:0;width:100%}:deep(.el-menu--collapse){width:72px}:deep(.el-menu-item.is-active){background:rgba(56,189,248,.12)}:deep(.el-menu--collapse .el-sub-menu__title span),:deep(.el-menu--collapse .el-menu-item span),:deep(.el-menu--collapse .el-sub-menu__icon-arrow){display:none!important}:deep(.el-menu--collapse .el-menu-item),:deep(.el-menu--collapse .el-sub-menu__title){justify-content:center;padding:0!important}
</style>
