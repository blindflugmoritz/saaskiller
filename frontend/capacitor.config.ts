import { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.saaskiller.app',
  appName: 'SaasKiller',
  webDir: 'build',
  server: { androidScheme: 'https' }
}

export default config
