#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import axios from 'axios';

const SCREAMING_FROG_API = 'https://api.screamingfrog.co.uk';
const API_KEY = process.env.SCREAMING_FROG_API_KEY;

const server = new Server(
  {
    name: 'mcp-server-screaming-frog',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// ツール定義: サイトクロール
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'crawl_site',
        description: 'Crawl a website and return technical SEO issues',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'Website URL to crawl',
            },
            max_pages: {
              type: 'number',
              description: 'Maximum pages to crawl (default: 500)',
            },
          },
          required: ['url'],
        },
      },
      {
        name: 'get_crawl_status',
        description: 'Get the status of a crawl job',
        inputSchema: {
          type: 'object',
          properties: {
            crawl_id: {
              type: 'string',
              description: 'Crawl job ID',
            },
          },
          required: ['crawl_id'],
        },
      },
    ],
  };
});

// ツール実行
server.setRequestHandler('tools/call', async (request) => {
  if (!API_KEY) {
    return {
      content: [{
        type: 'text',
        text: 'Error: SCREAMING_FROG_API_KEY environment variable is not set',
      }],
      isError: true,
    };
  }

  try {
    if (request.params.name === 'crawl_site') {
      const { url, max_pages = 500 } = request.params.arguments;

      // Screaming Frog Cloud API 呼び出し
      const response = await axios.post(`${SCREAMING_FROG_API}/crawl`, {
        url,
        max_pages,
      }, {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
        },
      });

      const crawl_id = response.data.crawl_id;

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            crawl_id,
            status: 'started',
            message: 'Crawl job started. Use get_crawl_status to check progress.',
          }, null, 2),
        }],
      };
    } else if (request.params.name === 'get_crawl_status') {
      const { crawl_id } = request.params.arguments;

      // クロールステータス取得
      const statusResponse = await axios.get(`${SCREAMING_FROG_API}/crawl/${crawl_id}/status`, {
        headers: { 'Authorization': `Bearer ${API_KEY}` },
      });

      const status = statusResponse.data.status;

      if (status === 'completed') {
        // 結果取得
        const results = await axios.get(`${SCREAMING_FROG_API}/crawl/${crawl_id}/results`, {
          headers: { 'Authorization': `Bearer ${API_KEY}` },
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(results.data, null, 2),
          }],
        };
      } else {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              crawl_id,
              status,
              message: `Crawl is ${status}. Please check again later.`,
            }, null, 2),
          }],
        };
      }
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `Error: ${error.message}\n${error.response?.data ? JSON.stringify(error.response.data, null, 2) : ''}`,
      }],
      isError: true,
    };
  }
});

// サーバー起動
const transport = new StdioServerTransport();
await server.connect(transport);
