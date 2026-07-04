import { defineConfig } from 'wxt';

export default defineConfig({
  modules: ['@wxt-dev/module-react'],
  webExt: {
    disabled: true,
  },
  manifest: {
    name: 'AI Brief Decoder',
    description: 'Decode client briefs into structured summaries',
    host_permissions: ['http://localhost:8000/*'],
  },
});