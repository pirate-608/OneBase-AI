/**
 * 🔐 API Token 鉴权模块
 *
 * 封装带 Token 的 fetch，自动从 localStorage 读取并注入 Authorization 头。
 * 当服务端返回 401 时，提示用户输入 Token。
 */

const TOKEN_KEY = 'onebase_api_token'

export function getToken() {
    return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
    localStorage.removeItem(TOKEN_KEY)
}

/**
 * 带鉴权的 fetch 封装。自动注入 Bearer Token，遇到 401 弹窗要求输入。
 * 用法与原生 fetch 完全一致：apiFetch(url, options)
 */
export async function apiFetch(url, options = {}) {
    const token = getToken()
    if (token) {
        options.headers = {
            ...options.headers,
            Authorization: `Bearer ${token}`,
        }
    }

    const res = await fetch(url, options)

    if (res.status === 401) {
        const newToken = prompt('此服务已开启 Token 鉴权，请输入 API Token：')
        if (newToken) {
            setToken(newToken.trim())
            // 用新 Token 重试一次
            options.headers = {
                ...options.headers,
                Authorization: `Bearer ${newToken.trim()}`,
            }
            return fetch(url, options)
        }
    }

    return res
}
