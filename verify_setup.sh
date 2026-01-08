#!/bin/bash

# Todo App Setup Verification Script
# This script checks if all services are running correctly

echo "🔍 Todo App Setup Verification"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service URLs
AUTH_URL="${AUTH_URL:-http://localhost:3001}"
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

# Test counter
PASSED=0
FAILED=0

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Checking $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" $url --max-time 5)

    if [ "$response" == "$expected" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $response)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response, expected $expected)"
        ((FAILED++))
        return 1
    fi
}

# Function to check if process is running on port
check_port() {
    local port=$1
    local service=$2

    echo -n "Checking if $service is listening on port $port... "

    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${GREEN}✓ RUNNING${NC}"
            ((PASSED++))
            return 0
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -an | grep ":$port" | grep "LISTEN" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ RUNNING${NC}"
            ((PASSED++))
            return 0
        fi
    fi

    echo -e "${RED}✗ NOT RUNNING${NC}"
    ((FAILED++))
    return 1
}

# Check Prerequisites
echo "📋 Prerequisites Check"
echo "----------------------"

echo -n "Node.js version: "
if command -v node &> /dev/null; then
    node_version=$(node -v)
    echo -e "${GREEN}$node_version${NC}"
    ((PASSED++))
else
    echo -e "${RED}Not installed${NC}"
    ((FAILED++))
fi

echo -n "Python version: "
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo -e "${GREEN}$python_version${NC}"
    ((PASSED++))
elif command -v python &> /dev/null; then
    python_version=$(python --version)
    echo -e "${GREEN}$python_version${NC}"
    ((PASSED++))
else
    echo -e "${RED}Not installed${NC}"
    ((FAILED++))
fi

echo -n "npm version: "
if command -v npm &> /dev/null; then
    npm_version=$(npm -v)
    echo -e "${GREEN}$npm_version${NC}"
    ((PASSED++))
else
    echo -e "${RED}Not installed${NC}"
    ((FAILED++))
fi

echo ""

# Check Environment Files
echo "📄 Environment Files Check"
echo "-------------------------"

check_env_file() {
    local file=$1
    local service=$2

    echo -n "Checking $service environment file... "

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ EXISTS${NC}"
        ((PASSED++))

        # Check for required variables
        if grep -q "DATABASE_URL" "$file" && grep -q "BETTER_AUTH_SECRET" "$file"; then
            echo -e "  ${GREEN}✓ Has required variables${NC}"
        else
            echo -e "  ${YELLOW}⚠ Missing required variables${NC}"
        fi
    else
        echo -e "${RED}✗ MISSING${NC}"
        ((FAILED++))
    fi
}

check_env_file "auth-service/.env" "Auth Service"
check_env_file "backend/.env" "Backend"
check_env_file "frontend/.env.local" "Frontend"

echo ""

# Check if services are running
echo "🚀 Services Status Check"
echo "------------------------"

check_port 3001 "Auth Service"
check_port 8000 "Backend API"
check_port 3000 "Frontend"

echo ""

# Check Service Health Endpoints
echo "💚 Health Endpoints Check"
echo "-------------------------"

check_service "Auth Service Health" "$AUTH_URL/health" "200"
check_service "Backend API Health" "$API_URL/health" "200"
check_service "Frontend Landing Page" "$FRONTEND_URL" "200"

echo ""

# Check API Documentation
echo "📚 API Documentation Check"
echo "-------------------------"

check_service "Backend Swagger Docs" "$API_URL/docs" "200"
check_service "Backend ReDoc" "$API_URL/redoc" "200"

echo ""

# Database Connection Check
echo "🗄️  Database Connection Check"
echo "------------------------------"

echo -n "Checking backend database connection... "

health_response=$(curl -s "$API_URL/health" 2>/dev/null)

if echo "$health_response" | grep -q "database is connected"; then
    echo -e "${GREEN}✓ CONNECTED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT CONNECTED${NC}"
    ((FAILED++))
fi

echo ""

# CORS Configuration Check
echo "🔒 CORS Configuration Check"
echo "---------------------------"

echo -n "Checking backend CORS headers... "

cors_response=$(curl -s -I -X OPTIONS "$API_URL/health" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: GET" 2>/dev/null)

if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✓ CONFIGURED${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ NOT CONFIGURED (may cause frontend issues)${NC}"
    ((FAILED++))
fi

echo ""

# Test Basic Functionality
echo "🧪 Functional Tests"
echo "-------------------"

echo -n "Testing signup endpoint... "
test_email="test$(date +%s)@example.com"
signup_response=$(curl -s -X POST "$AUTH_URL/api/auth/signup/email" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$test_email\",
        \"password\": \"testpassword123\",
        \"name\": \"Test User\"
    }" 2>/dev/null)

if echo "$signup_response" | grep -q "token"; then
    echo -e "${GREEN}✓ WORKING${NC}"
    ((PASSED++))

    # Extract token for further tests
    if command -v jq &> /dev/null; then
        TOKEN=$(echo "$signup_response" | jq -r '.token')
        USER_ID=$(echo "$signup_response" | jq -r '.user.id')

        # Test task creation
        echo -n "Testing task creation endpoint... "
        task_response=$(curl -s -X POST "$API_URL/api/$USER_ID/tasks" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
                "title": "Test task from verification script"
            }' 2>/dev/null)

        if echo "$task_response" | grep -q "id"; then
            echo -e "${GREEN}✓ WORKING${NC}"
            ((PASSED++))
        else
            echo -e "${RED}✗ FAILED${NC}"
            ((FAILED++))
        fi
    else
        echo -e "  ${YELLOW}⚠ jq not installed, skipping task creation test${NC}"
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo ""

# Summary
echo "================================"
echo "📊 Summary"
echo "================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Your setup is ready.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please review the output above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "1. Ensure all services are running (npm run dev / python main.py)"
    echo "2. Check environment files (.env, .env.local) are configured"
    echo "3. Verify database connection string is correct"
    echo "4. Ensure BETTER_AUTH_SECRET matches between auth-service and backend"
    exit 1
fi
