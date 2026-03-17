/**
 * Feishu Common - Shared authentication and API client
 * Provides fetchWithAuth for Feishu API calls
 */

const fs = require('fs');
const path = require('path');

// Load environment variables
require('dotenv').config({ path: path.resolve(__dirname, '../../.env'), quiet: true });

// Cache for tenant access token
let tokenCache = {
    token: null,
    expireTime: 0
};

/**
 * Get tenant access token from Feishu
 */
async function getTenantAccessToken() {
    // Check cache
    if (tokenCache.token && Date.now() < tokenCache.expireTime) {
        return tokenCache.token;
    }

    const appId = process.env.FEISHU_APP_ID;
    const appSecret = process.env.FEISHU_APP_SECRET;

    if (!appId || !appSecret) {
        // Try to read from openclaw config
        const configPath = path.resolve(process.env.HOME || process.env.USERPROFILE, '.openclaw/openclaw.json');
        if (fs.existsSync(configPath)) {
            try {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                const feishuAccount = config.channels?.feishu?.accounts?.main;
                if (feishuAccount) {
                    process.env.FEISHU_APP_ID = feishuAccount.appId;
                    process.env.FEISHU_APP_SECRET = feishuAccount.appSecret;
                }
            } catch (e) {
                console.error('Error reading config:', e.message);
            }
        }
    }

    const finalAppId = process.env.FEISHU_APP_ID;
    const finalAppSecret = process.env.FEISHU_APP_SECRET;

    if (!finalAppId || !finalAppSecret) {
        throw new Error('FEISHU_APP_ID and FEISHU_APP_SECRET not found. Please set them in .env file or ~/.openclaw/openclaw.json');
    }

    const response = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            app_id: finalAppId,
            app_secret: finalAppSecret
        })
    });

    const data = await response.json();
    
    if (data.code !== 0) {
        throw new Error(`Failed to get token: ${data.msg}`);
    }

    // Cache token (expire 5 minutes early)
    tokenCache.token = data.tenant_access_token;
    tokenCache.expireTime = Date.now() + (data.expire - 300) * 1000;

    return tokenCache.token;
}

/**
 * Fetch with Feishu authentication
 */
async function fetchWithAuth(url, options = {}) {
    const token = await getTenantAccessToken();
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    // Don't set Content-Type for FormData
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    } else if (!headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    // Handle token expiration
    if (response.status === 401 || response.status === 403) {
        // Clear cache and retry once
        tokenCache.token = null;
        tokenCache.expireTime = 0;
        
        const newToken = await getTenantAccessToken();
        headers['Authorization'] = `Bearer ${newToken}`;
        
        return fetch(url, {
            ...options,
            headers
        });
    }

    return response;
}

/**
 * Get user info by email or open_id
 */
async function getUserInfo(emailOrOpenId) {
    const isEmail = emailOrOpenId.includes('@');
    const url = isEmail 
        ? `https://open.feishu.cn/open-apis/contact/v3/users/email_to_user_id?email=${encodeURIComponent(emailOrOpenId)}`
        : `https://open.feishu.cn/open-apis/contact/v3/users/${emailOrOpenId}`;

    const response = await fetchWithAuth(url);
    const data = await response.json();
    
    if (data.code !== 0) {
        throw new Error(`Failed to get user info: ${data.msg}`);
    }

    return data.data;
}

module.exports = {
    fetchWithAuth,
    getTenantAccessToken,
    getUserInfo
};
