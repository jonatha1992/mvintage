// Test script to verify frontend-backend API communication
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

async function testEndpoints() {
  console.log('🚀 Testing Backend API Endpoints...\n');

  const tests = [
    {
      name: 'Health Check',
      method: 'GET',
      url: `${BASE_URL.replace('/api/v1', '')}/health`,
      expectAuth: false
    },
    {
      name: 'Admin Shipping Statistics',
      method: 'GET', 
      url: `${BASE_URL}/admin/shipping/statistics`,
      expectAuth: true
    },
    {
      name: 'Admin Shipping Providers',
      method: 'GET',
      url: `${BASE_URL}/admin/shipping/providers`, 
      expectAuth: true
    },
    {
      name: 'Orders with Customer Info (Admin)',
      method: 'GET',
      url: `${BASE_URL}/orders/admin`,
      expectAuth: true
    }
  ];

  for (const test of tests) {
    try {
      console.log(`Testing: ${test.name}...`);

      const response = await axios({
        method: test.method,
        url: test.url,
        timeout: 5000,
        validateStatus: function (status) {
          // Accept both success and auth error responses for testing
          return status < 500;
        }
      });

      if (response.status === 200) {
        console.log(`  ✅ SUCCESS: ${test.name}`);
        if (response.data) {
          console.log(`  📊 Response: ${JSON.stringify(response.data, null, 2).substring(0, 200)}...`);
        }
      } else if (response.status === 401 && test.expectAuth) {
        console.log(`  🔐 AUTH REQUIRED: ${test.name} (Expected)`);
      } else if (response.status === 403) {
        console.log(`  🚫 FORBIDDEN: ${test.name}`);
      } else if (response.status === 404) {
        console.log(`  ❌ NOT FOUND: ${test.name}`);
      } else {
        console.log(`  ⚠️ UNEXPECTED: ${test.name} - Status ${response.status}`);
      }
      
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        console.log(`  🔌 CONNECTION REFUSED: ${test.name} - Backend not running`);
      } else if (error.code === 'ETIMEDOUT') {
        console.log(`  ⏰ TIMEOUT: ${test.name} - Request took too long`);
      } else {
        console.log(`  💥 ERROR: ${test.name} - ${error.message}`);
      }
    }

    console.log(''); // Empty line between tests
  }

  console.log('✨ API Testing Complete!');
}

testEndpoints().catch(console.error);
