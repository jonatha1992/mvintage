// Comprehensive API Test for M-Vintage Frontend-Backend Communication
// This script tests all the endpoints used by the AdminOrdersView and other components

async function testAPI() {
    const BASE_URL = 'http://localhost:8000/api/v1';

    // Test cases organized by category
    const testSuites = [
        {
            name: '🔐 Authentication & Users',
            tests: [
                { name: 'Get Current User', method: 'GET', url: '/users/me', requiresAuth: true },
                { name: 'Get All Users', method: 'GET', url: '/users/', requiresAuth: true },
                { name: 'Get My Roles', method: 'GET', url: '/roles/me/roles', requiresAuth: true }
            ]
        },
        {
            name: '📦 Orders Management',
            tests: [
                { name: 'Get Orders', method: 'GET', url: '/orders/', requiresAuth: true },
                { name: 'Get Orders with Customer Info (Admin)', method: 'GET', url: '/orders/admin', requiresAuth: true },
                { name: 'Get My Orders', method: 'GET', url: '/orders/my-orders', requiresAuth: true }
            ]
        },
        {
            name: '🚚 Admin Shipping (NEW ENDPOINTS)',
            tests: [
                { name: 'Get Shipping Statistics', method: 'GET', url: '/admin/shipping/statistics', requiresAuth: true },
                { name: 'Get Shipping Providers', method: 'GET', url: '/admin/shipping/providers', requiresAuth: true },
                { name: 'Get Pending Shipments', method: 'GET', url: '/admin/shipping/orders/pending', requiresAuth: true },
                { name: 'Get Bulk Action Ready Orders', method: 'GET', url: '/admin/shipping/bulk-actions/ready', requiresAuth: true }
            ]
        },
        {
            name: '🎨 Master Data',
            tests: [
                { name: 'Get Colors', method: 'GET', url: '/colors', requiresAuth: false },
                { name: 'Get Categories', method: 'GET', url: '/categories', requiresAuth: false },
                { name: 'Get Categories with Stock', method: 'GET', url: '/categories/with-stock', requiresAuth: false },
                { name: 'Get Sizes', method: 'GET', url: '/sizes', requiresAuth: false }
            ]
        },
        {
            name: '👕 Products',
            tests: [
                { name: 'Get Products', method: 'GET', url: '/products/', requiresAuth: false },
                { name: 'Check Stock', method: 'POST', url: '/products/check-stock/', requiresAuth: false }
            ]
        },
        {
            name: '👥 Customers',
            tests: [
                { name: 'Get Customers', method: 'GET', url: '/customers/', requiresAuth: true },
                { name: 'Get My Customer Data', method: 'GET', url: '/customers/my-data', requiresAuth: true }
            ]
        },
        {
            name: '💳 Payments',
            tests: [
                { name: 'Create MercadoPago Preference', method: 'POST', url: '/payments/create-preference?order_id=1', requiresAuth: true },
                { name: 'Get Payment Status', method: 'GET', url: '/payments/status/1', requiresAuth: true }
            ]
        }
    ];

    let totalTests = 0;
    let successfulTests = 0;
    let authRequiredTests = 0;
    let failedTests = 0;

    // Run all test suites
    for (const suite of testSuites) {
        console.log(`\n${suite.name}`);

        for (const test of suite.tests) {
            totalTests++;

            try {
                const startTime = Date.now();

                // Prepare fetch options
                const options = {
                    method: test.method,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };

                // Add test data for POST requests
                if (test.method === 'POST' && test.url.includes('check-stock')) {
                    options.body = JSON.stringify([
                        { product_id: 1, variant_id: null, quantity: 1 }
                    ]);
                }

                const response = await fetch(`${BASE_URL}${test.url}`, options);
                const responseTime = Date.now() - startTime;

                // Analyze response
                let status = '';
                let icon = '';

                if (response.status === 200) {
                    status = `SUCCESS (${responseTime}ms)`;
                    icon = '✅';
                    successfulTests++;

                    // Try to get response preview
                    try {
                        const data = await response.json();
                        if (Array.isArray(data)) {
                            status += ` - ${data.length} items`;
                        } else if (typeof data === 'object' && data.total !== undefined) {
                            status += ` - total: ${data.total}`;
                        } else if (typeof data === 'object' && Object.keys(data).length > 0) {
                            status += ` - keys: ${Object.keys(data).slice(0, 3).join(', ')}${Object.keys(data).length > 3 ? '...' : ''}`;
                        }
                    } catch (e) {
                        // Response might not be JSON
                    }

                } else if (response.status === 401 && test.requiresAuth) {
                    status = `AUTH REQUIRED (${responseTime}ms)`;
                    icon = '🔐';
                    authRequiredTests++;
                } else if (response.status === 403) {
                    status = `PERMISSION DENIED (${responseTime}ms)`;
                    icon = '🚫';
                    authRequiredTests++;
                } else if (response.status === 404) {
                    status = `NOT FOUND (${responseTime}ms)`;
                    icon = '❌';
                    failedTests++;
                } else if (response.status === 422) {
                    status = `VALIDATION ERROR (${responseTime}ms)`;
                    icon = '⚠️';
                    failedTests++;
                } else {
                    status = `HTTP ${response.status} (${responseTime}ms)`;
                    icon = '⚠️';
                    failedTests++;
                }

                console.log(`  ${icon} ${test.name}: ${status}`);

            } catch (error) {
                failedTests++;
                let errorMsg = '';

                if (error.code === 'ECONNREFUSED') {
                    errorMsg = 'CONNECTION REFUSED - Backend not running';
                } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    errorMsg = 'NETWORK ERROR - Cannot reach backend';
                } else {
                    errorMsg = error.message;
                }

                console.log(`  ❌ ${test.name}: ERROR - ${errorMsg}`);
            }
        }
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('🎯 API TEST SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total Tests: ${totalTests}`);
    console.log(`✅ Successful: ${successfulTests}`);
    console.log(`🔐 Auth Required: ${authRequiredTests}`);
    console.log(`❌ Failed: ${failedTests}`);

    const workingEndpoints = successfulTests + authRequiredTests;
    const successRate = ((workingEndpoints / totalTests) * 100).toFixed(1);

    console.log(`\n📊 Success Rate: ${successRate}%`);

    if (successRate >= 90) {
        console.log('🎉 Excellent! API is working well.');
    } else if (successRate >= 75) {
        console.log('⚠️  Good, but some endpoints need attention.');
    } else {
        console.log('🚨 Poor performance - multiple endpoints failing.');
    }

    console.log('\n📝 Notes:');
    if (authRequiredTests > 0) {
        console.log(`- ${authRequiredTests} endpoints require authentication`);
    }
    if (failedTests > 0) {
        console.log(`- ${failedTests} endpoints are failing and need investigation`);
    }
    console.log('='.repeat(60));
}

// Run the test
testAPI().catch(console.error);
