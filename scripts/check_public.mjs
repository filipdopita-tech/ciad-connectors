import assert from 'node:assert/strict';
const base = 'https://mcp.ciad.cz';
const get = async path => {
  const response = await fetch(base + path, { signal: AbortSignal.timeout(20000), redirect: 'error' });
  assert.equal(response.status, 200, `Public route failed: ${path}`);
  return response;
};
const health = await (await get('/healthz')).json();
assert.equal(health.ok, true);
assert.match(health.version, /^\d+\.\d+\.\d+$/);
const resource = await (await get('/.well-known/oauth-protected-resource/mcp')).json();
assert.equal(resource.resource, `${base}/mcp`);
assert.deepEqual(resource.authorization_servers.map(url => new URL(url).origin), [base]);
assert.deepEqual(resource.scopes_supported, ['workspace:read']);
const metadata = await (await get('/.well-known/oauth-authorization-server')).json();
assert.equal(new URL(metadata.issuer).origin, base);
for (const [key, path] of [['authorization_endpoint', '/authorize'], ['token_endpoint', '/token'], ['registration_endpoint', '/register']]) assert.equal(metadata[key], base + path);
assert.ok(metadata.code_challenge_methods_supported.includes('S256'));
assert.deepEqual(metadata.scopes_supported, ['workspace:read']);
const mcp = await fetch(base + '/mcp', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-11-25', capabilities: {}, clientInfo: { name: 'CIAD-public-check', version: '1.0.0' } } }), signal: AbortSignal.timeout(20000), redirect: 'error' });
assert.equal(mcp.status, 401);
assert.ok(mcp.headers.get('www-authenticate')?.includes(`${base}/.well-known/oauth-protected-resource/mcp`));
await mcp.body?.cancel();
for (const path of ['/docs', '/onboarding', '/privacy', '/terms', '/support']) await (await get(path)).body?.cancel();
for (const path of ['/api/tenants', '/operator.js']) {
  const response = await fetch(base + path, { signal: AbortSignal.timeout(20000) });
  assert.equal(response.status, 404); await response.body?.cancel();
}
console.log(JSON.stringify({ ok: true, version: health.version, oauth: true, publicRoutes: 5, privateRoutesClosed: 2, mcpUnauthorized: true }));
