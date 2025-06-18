import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'game-primary': '#1a1a1a',
        'game-secondary': '#2a2a2a',
        'game-accent': '#ffd700',
        'game-text': '#ffffff',
        'game-success': '#4caf50',
        'game-warning': '#ff9800',
        'game-danger': '#f44336',
      },
      fontFamily: {
        'game': ['Press Start 2P', 'system-ui'],
      },
    },
  },
  plugins: [],
}
export default config 