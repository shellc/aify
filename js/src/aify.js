import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { useState } from 'react'
import { Layout, List, Avatar, Space, Typography, Button, Card } from 'antd'
import { MenuUnfoldOutlined, MenuFoldOutlined, MessageFilled } from '@ant-design/icons'
import {

} from '@ant-design/icons';
import { ReactMarkdown } from 'react-markdown/lib/react-markdown';
import remarkGfm from 'remark-gfm'
import { Chat } from './chat'
import Link from 'antd/es/typography/Link';

const { Sider } = Layout
const { Text } = Typography
const { Meta } = Card

let welcome_message = `
# Welcome to aify.run

##### Build your AI-native application in seconds.

🛠️ AI-native application framework and runtime. Simply write a YAML file.

🤖 Ready-to-use AI chatbot UI.

🚀 [Getting started: Create your first AI application](https://docs.aify.run/getting_started.html)
`

const Aify = (props) => {
    const [leftCollapsed, setLeftCollapsed] = useState(false);
    const [rightCollapsed, setRightCollapsed] = useState(false);
    const [apps, setApps] = useState();
    const [appMap, setAppMap] = useState({});
    const [currentAppName, setCurrentAppName] = useState(null);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [sessions, setSessions] = useState();
    const [welcomMessage, setWelcomeMessage] = useState();

    const loadApps = () => {
        fetch('/api/apps')
            .then(r => r.json())
            .then(apps => {
                let m = {};
                apps.forEach(app => {
                    m[app.name] = app;
                });
                setApps(apps);
                setAppMap(m);
            })
    }

    const loadSessions = () => {
        fetch('/api/sessions')
            .then(r => r.json())
            .then(sessions => setSessions(sessions))
    }

    const loadWelcomeMessage = () => {
        fetch('/apps/static/welcome.md')
            .then(r => {
                if (r.status === 200) {
                    return r.text();
                } else {
                    return welcome_message
                }
            })
            .then(data => setWelcomeMessage(data))
    }

    useEffect(() => {
        loadApps();
        loadSessions();
        loadWelcomeMessage();
    }, [])

    const createSession = (appName) => {
        let sessionId = crypto.randomUUID();
        switchSession(appName, sessionId);
    }

    const switchSession = (appName, sessionId) => {
        setCurrentAppName(appName);
        setCurrentSessionId(sessionId);
    }

    return (
        <Layout
            hasSider
            style={{
                minHeight: '100vh',
            }}
        >
            <Sider
                collapsible
                collapsed={leftCollapsed}
                onCollapse={(value) => setLeftCollapsed(value)}
                breakpoint="lg"
                theme="light"
                style={{
                    overflow: 'auto',
                    height: '100vh',
                    backgroundColor: '#eee'
                }}
                width={300}
                collapsedWidth={65}
                trigger={null}
            >
                <List
                    size='small'
                    itemLayout="horizontal"
                    dataSource={sessions}
                    renderItem={(session => (
                        <List.Item>
                            <Link
                                onClick={() => switchSession(session.name, session.session_id)}
                            >
                                <Space>
                                    <Avatar style={{ backgroundColor: '#fff' }}>{(appMap[session.name] && appMap[session.name]['icon_emoji']) ?? '🤖'}</Avatar>
                                    {!leftCollapsed ? (
                                        <Space direction='vertical' size={0}>
                                            <Text type="secondary"
                                                ellipsis={{
                                                    rows: 1,
                                                }}
                                                style={{ width: '220px' }}
                                            >
                                                {session.content}
                                            </Text>
                                        </Space>
                                    ) : null}

                                </Space>
                            </Link>
                        </List.Item>
                    ))}
                />
            </Sider>
            <Layout
                id="content"
                style={{
                    height: '100vh',
                    overflow: 'scroll',
                }}
                className='bg-white'
            >
                <div className='d-flex p-2'>
                    <Button
                        type="text"
                        icon={leftCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => setLeftCollapsed(!leftCollapsed)}
                        style={{
                            fontSize: '14px',
                        }}
                        className='me-auto'
                    />
                    <Button
                        type="text"
                        icon={rightCollapsed ? <MenuFoldOutlined /> : <MenuUnfoldOutlined />}
                        onClick={() => setRightCollapsed(!rightCollapsed)}
                        style={{
                            fontSize: '14px',
                        }}
                        className='ms-auto'
                    />
                </div>
                {(currentAppName != null && currentSessionId != null) ? (
                    <Chat
                        name={currentAppName}
                        session_id={currentSessionId}
                        width="100%"
                        onMessageReceived={loadSessions}
                        icon={(appMap[currentAppName] && appMap[currentAppName]['icon_emoji']) ?? '🤖'}
                    />
                ) : (
                    <div className='p-5'>
                        <ReactMarkdown children={props.message} remarkPlugins={[remarkGfm]} className='p-0 m-0'>
                            {welcomMessage}
                        </ReactMarkdown>
                    </div>
                )}

            </Layout>

            <Sider
                collapsible
                collapsed={rightCollapsed}
                onCollapse={(value) => setRightCollapsed(value)}
                breakpoint="lg"
                theme="light"
                style={{
                    overflow: 'auto',
                    height: '100vh',
                    backgroundColor: '#eee'
                }}
                width={300}
                collapsedWidth={0}
                trigger={null}
                reverseArrow
            >

                <List
                    split={false}
                    size='small'
                    itemLayout="horizontal"
                    dataSource={apps}
                    renderItem={(app) => (
                        <List.Item>
                            <Card
                                style={{
                                    width: 268,
                                    marginTop: 16,
                                }}
                                actions={[
                                    <span><MessageFilled key="createSession" onClick={() => createSession(app.name)} /></span>,
                                ]}
                            >
                                <Meta
                                    avatar={<Avatar style={{ backgroundColor: '#eee' }}>{app.icon_emoji ?? '🤖'}</Avatar>}
                                    title={app.title}
                                />
                                <div className='pt-3'>
                                    <Text type="secondary">
                                        {app.description}
                                    </Text>
                                </div>
                            </Card>
                        </List.Item>
                    )}

                />
            </Sider>
        </Layout>
    );
}

export const create = (elementId, height) => {
    const root = ReactDOM.createRoot(document.getElementById(elementId));
    root.render(
        <React.StrictMode>
            <Aify />
        </React.StrictMode>
    );
}