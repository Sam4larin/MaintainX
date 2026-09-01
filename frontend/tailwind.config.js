export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        // Neutral warm-paper content background (not cold slate)
        paper: {
          50: '#faf9f6',
          100: '#f4f2ed',
          200: '#e9e6de',
          300: '#d9d4c8',
        },
        // Dark charcoal-navy for sidebar / chrome
        ink: {
          950: '#0d1117',
          900: '#131a22',
          800: '#1a222c',
          700: '#232d39',
          600: '#37424f',
          500: '#4d5a68',
        },
        // Primary accent: desaturated copper/amber (industrial, not candy)
        rust: {
          50: '#fbf2e9',
          100: '#f4dfc4',
          300: '#dba15b',
          500: '#bd7a35',
          600: '#a2632a',
          700: '#824e23',
        },
        // Reserved status accent: muted teal for "healthy/normal"
        moss: {
          50: '#eef4f1',
          100: '#d6e6de',
          300: '#8db8a9',
          500: '#4f8a76',
          600: '#3d6f5f',
        },
        // Alert states, deliberately desaturated
        signal: {
          amber: '#b8873a',
          red: '#b1493f',
          crimson: '#8f3730',
        },
      },
      boxShadow: {
        panel: '0 1px 2px rgba(23, 17, 8, 0.06), 0 8px 24px -12px rgba(23, 17, 8, 0.12)',
        'panel-lg': '0 4px 12px rgba(23, 17, 8, 0.08), 0 20px 48px -20px rgba(23, 17, 8, 0.18)',
      },
      letterSpacing: {
        tightest: '-0.045em',
      },
    },
  },
  plugins: [],
};
