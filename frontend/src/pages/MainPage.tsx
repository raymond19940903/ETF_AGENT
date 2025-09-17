import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { logoutAsync } from '../store/authSlice';
import ConversationPanel from '../components/ConversationPanel';
import StrategyDisplay from '../components/StrategyDisplay';
import StrategyHistory from '../components/StrategyHistory';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import styles from './MainPage.module.css';

type MenuKey = 'conversation' | 'strategy' | 'history';

const MainPage: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { currentStrategy } = useSelector((state: RootState) => state.strategy);
  const [activeMenu, setActiveMenu] = useState<MenuKey>('conversation');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleLogout = async () => {
    if (window.confirm('确定要退出登录吗？')) {
      await dispatch(logoutAsync() as any);
    }
  };

  const menuItems = [
    {
      key: 'conversation' as MenuKey,
      icon: '💬',
      label: '智能对话',
      description: '与AI助手对话生成策略'
    },
    {
      key: 'strategy' as MenuKey,
      icon: '📊',
      label: '策略展示',
      description: '查看当前策略详情'
    },
    {
      key: 'history' as MenuKey,
      icon: '📚',
      label: '历史记录',
      description: '管理历史策略'
    }
  ];

  const renderContent = () => {
    switch (activeMenu) {
      case 'conversation':
        return <ConversationPanel className={styles.contentPanel} />;
      case 'strategy':
        return (
          <div className={styles.contentPanel}>
            <StrategyDisplay strategy={currentStrategy} />
          </div>
        );
      case 'history':
        return <StrategyHistory className={styles.contentPanel} />;
      default:
        return null;
    }
  };

  return (
    <div className={styles.mainPage}>
      {/* 顶部导航栏 */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.logo}>
            <span className={styles.logoIcon}>🚀</span>
            <span className={styles.logoText}>ETF智能策略</span>
          </div>
        </div>
        
        <div className={styles.headerRight}>
          <div className={styles.userInfo}>
            <div className={styles.avatar}>
              {user?.nickname?.charAt(0) || 'U'}
            </div>
            <div className={styles.userDetails}>
              <span className={styles.userName}>{user?.nickname || '用户'}</span>
              <span className={styles.userType}>
                {user?.isNewUser ? '新用户' : '老用户'}
              </span>
            </div>
          </div>
          <Button variant="secondary" onClick={handleLogout}>
            退出登录
          </Button>
        </div>
      </header>

      <div className={styles.mainContent}>
        {/* 侧边栏 */}
        <aside className={`${styles.sidebar} ${sidebarCollapsed ? styles.collapsed : ''}`}>
          <div className={styles.sidebarHeader}>
            <Button
              variant="text"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className={styles.collapseButton}
            >
              {sidebarCollapsed ? '▶' : '◀'}
            </Button>
          </div>
          
          <nav className={styles.navigation}>
            {menuItems.map((item) => (
              <button
                key={item.key}
                className={`${styles.navItem} ${activeMenu === item.key ? styles.active : ''}`}
                onClick={() => setActiveMenu(item.key)}
              >
                <span className={styles.navIcon}>{item.icon}</span>
                {!sidebarCollapsed && (
                  <div className={styles.navContent}>
                    <span className={styles.navLabel}>{item.label}</span>
                    <span className={styles.navDescription}>{item.description}</span>
                  </div>
                )}
              </button>
            ))}
          </nav>
        </aside>

        {/* 主要内容区域 */}
        <main className={styles.content}>
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default MainPage;