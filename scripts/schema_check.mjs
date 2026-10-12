import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const Ajv2020 = require('ajv/dist/2020.js').default;
const root = resolve(process.argv[2] ?? dirname(dirname(fileURLToPath(import.meta.url))));
const json = async path => JSON.parse(await readFile(path, 'utf8'));
const schemaRoot = new URL('./schemas/', import.meta.url);
const ajv = new Ajv2020({ allErrors: true, strict: true });
for (const name of ['plugin', 'mcp']) {
  const schema = await json(new URL(`${name}.schema.json`, schemaRoot));
  const manifest = await json(resolve(root, `${name}.json`));
  if (name === 'mcp') {
    const server = manifest.mcpServers?.ciad;
    assert.deepEqual(server?.extensions, { 'com.openai': { auth: {
      type: 'oauth', client: { mode: 'dcr' }, resource: 'https://mcp.ciad.cz/mcp', baseScopes: ['workspace:read'],
    } } }, 'Documented OpenAI OAuth overlay mismatch');
    delete server.extensions;
  }
  const validate = ajv.compile(schema);
  assert.ok(validate(manifest), `${name}: portable schema validation failed`);
}
console.log('PASS: portable schemas and explicit OpenAI OAuth overlay');
