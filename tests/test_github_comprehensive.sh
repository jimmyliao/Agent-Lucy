#!/bin/bash
# Comprehensive GitHub MCP Testing Script
# Tests all core GitHub operations through Agent Lucy

API_URL="http://localhost:8001/api/chat"
USER_ID="github_tester"

echo "========================================="
echo "🧪 Agent Lucy - GitHub MCP 完整測試"
echo "========================================="
echo ""

# Test 1: Get authenticated user info
echo "📋 測試 1: 取得認證用戶資訊"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Get my authenticated GitHub user information\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -30
echo ""
sleep 2

# Test 2: List user repositories
echo "📋 測試 2: 列出 jimmyliao 的儲存庫"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"List the first 5 repositories for GitHub user 'jimmyliao'\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -40
echo ""
sleep 2

# Test 3: Get repository information
echo "📋 測試 3: 取得特定儲存庫資訊"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Get information about the repository 'agent-lucy' owned by 'jimmyliao'\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -40
echo ""
sleep 2

# Test 4: Search repositories
echo "📋 測試 4: 搜尋儲存庫"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Search for GitHub repositories about 'azure ai agents'\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -40
echo ""
sleep 2

# Test 5: Get file contents
echo "📋 測試 5: 讀取檔案內容"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Get the contents of README.md from repository 'agent-lucy' owned by 'jimmyliao'\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -50
echo ""
sleep 2

# Test 6: List repository branches
echo "📋 測試 6: 列出儲存庫分支"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"List all branches in the repository 'agent-lucy' owned by 'jimmyliao'\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -40
echo ""
sleep 2

# Test 7: Get commit history
echo "📋 測試 7: 取得 Commit 歷史"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Show me the latest 5 commits from repository 'agent-lucy' owned by 'jimmyliao'\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -50
echo ""
sleep 2

# Test 8: List issues (if any)
echo "📋 測試 8: 列出 Issues"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"List open issues in repository 'agent-lucy' owned by 'jimmyliao'\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -40
echo ""
sleep 2

# Test 9: Get repository contributors
echo "📋 測試 9: 取得儲存庫貢獻者"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Who are the contributors to repository 'agent-lucy' owned by 'jimmyliao'?\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -40
echo ""
sleep 2

# Test 10: Complex query combining multiple operations
echo "📋 測試 10: 複雜查詢（組合多個操作）"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Analyze the 'agent-lucy' repository by jimmyliao: Tell me the main programming languages used, recent activity, and key features from the README\",
    \"user_id\": \"$USER_ID\"
  }" | python3 -m json.tool | head -60
echo ""

echo "========================================="
echo "✅ GitHub MCP 測試完成！"
echo "========================================="
