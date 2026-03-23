# Microsoft Learn MCP Server

Microsoft Learn の技術ドキュメントを検索・取得するための MCP サーバーです。
Azure、.NET、Windows など Microsoft 製品群のドキュメントにアクセスできます。

## 前提条件

`uv` がインストールされていない場合は先にインストールしてください。

```bash
pip install uv
```

または [公式インストールガイド](https://docs.astral.sh/uv/getting-started/installation/) を参照してください。

## セットアップ

```bash
git clone <リポジトリURL>
cd MicrosoftLearnMCPServer
uv venv .venv
uv pip install -e ".[dev]" -p .venv/bin/python
```

## Kiro での設定

`.kiro/settings/mcp.json` に以下を追加してください。

`/path/to/MicrosoftLearnMCPServer` はクローンしたディレクトリの絶対パスに置き換えてください。

```bash
# 絶対パスの確認方法
cd MicrosoftLearnMCPServer && pwd
```

```json
{
  "mcpServers": {
    "microsoft-learn": {
      "command": "/path/to/MicrosoftLearnMCPServer/.venv/bin/microsoft-learn-mcp-server",
      "args": [],
      "disabled": false,
      "autoApprove": [
        "search_documentation",
        "read_documentation"
      ]
    }
  }
}
```

## WSLを利用する場合
`Kiroでの設定`を参考に、以下を`.kiro/settings/mcp.json`に追加してください。

```json
{
  "mcpServers": {
    "microsoft-learn": {
      "command": "wsl",
      "args": [
        "/home/tono/work/kiro/MicrosoftLearnMCPServer/.venv/bin/microsoft-learn-mcp-server"
      ],
      "disabled": false,
      "autoApprove": [
        "search_documentation",
        "read_documentation"
      ]
    }
  }
}
```

## 提供するツール

### `search_documentation`

Microsoft Learn のドキュメントを検索します。

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|------|------|-----------|------|
| `query` | string | ✅ | - | 検索クエリ |
| `locale` | string | - | `en-us` | ロケール（例: `ja-jp`） |

### `read_documentation`

指定 URL のドキュメント記事を取得し、Markdown 形式で返します。

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| `url` | string | ✅ | 記事の URL |

## テスト

```bash
.venv/bin/pytest tests/ -v
```

## ライセンス

Apache License 2.0
